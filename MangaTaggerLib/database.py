import logging
import sys
from datetime import datetime
from pathlib import Path
from queue import Queue

from bson.errors import InvalidDocument
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, DuplicateKeyError


class Database:
    database_name = None
    host_address = None
    port = None
    username = None
    password = None
    auth_source = None
    server_selection_timeout_ms = None

    _client = None
    _database = None
    _log = None

    @classmethod
    def initialize(cls):
        cls._log = logging.getLogger(f'{cls.__module__}.{cls.__name__}')

        if cls.auth_source is None:
            cls._client = MongoClient(cls.host_address,
                                      cls.port,
                                      username=cls.username,
                                      password=cls.password,
                                      serverSelectionTimeoutMS=cls.server_selection_timeout_ms)
        else:
            cls._client = MongoClient(cls.host_address,
                                      cls.port,
                                      username=cls.username,
                                      password=cls.password,
                                      authSource=cls.auth_source,
                                      serverSelectionTimeoutMS=cls.server_selection_timeout_ms)

        try:
            cls._log.info('Establishing database connection...')
            cls._client.is_mongos
        except ServerSelectionTimeoutError as sste:
            cls._log.exception(sste)
            cls._log.critical('Manga Tagger cannot run without a database connection. Please check the'
                              'configuration in settings.json and try again.')
            sys.exit(1)

        cls._database = cls._client[cls.database_name]

        MetadataTable.initialize()
        ProcFilesTable.initialize()
        ProcSeriesTable.initialize()
        TaskQueueTable.initialize()

        cls._log.info('Database connection established!')
        cls._log.debug(f'{cls.__name__} class has been initialized')

    @classmethod
    def load_database_tables(cls):
        ProcSeriesTable.load()

    @classmethod
    def save_database_tables(cls):
        ProcSeriesTable.save()

    @classmethod
    def close_connection(cls):
        cls._log.info('Closing database connection...')
        cls._client.close()

    @classmethod
    def print_debug_settings(cls):
        cls._log.debug(f'Database Name: {Database.database_name}')
        cls._log.debug(f'Host Address: {Database.host_address}')
        cls._log.debug(f'Port: {Database.port}')
        cls._log.debug(f'Username: {Database.username}')
        cls._log.debug(f'Password: {Database.password}')
        cls._log.debug(f'Authentication Source: {Database.auth_source}')
        cls._log.debug(f'Server Selection Timeout (ms): {Database.server_selection_timeout_ms}')

    @classmethod
    def insert(cls, data, logging_info=None):
        try:
            cls._log.info('Attempting to insert record into the database...', extra=logging_info)

            if type(data) is dict:
                cls._database.insert_one(data)
            else:
                cls._database.insert_one(data.__dict__)
        except (DuplicateKeyError, InvalidDocument) as e:
            cls._log.exception(e, extra=logging_info)
            return
        except Exception as e:
            cls._log.exception(e, extra=logging_info)
            cls._log.warning('Manga Tagger is unfamiliar with this error. Please log an issue for investigation.',
                             extra=logging_info)
            return

        cls._log.info('Insertion was successful!', extra=logging_info)

    @classmethod
    def update(cls, search_filter, data, logging_info):
        try:
            cls._log.info('Attempting to update record in the database...', extra=logging_info)
            cls._database.update_one(search_filter, data)
        except Exception as e:
            cls._log.exception(e, extra=logging_info)
            cls._log.warning('Manga Tagger is unfamiliar with this error. Please log an issue for investigation.',
                             extra=logging_info)
            return

        cls._log.info('Update was successful!', extra=logging_info)

    @classmethod
    def delete_all(cls, logging_info):
        try:
            cls._log.info('Attempting to delete all records in the database...', extra=logging_info)
            cls._database.delete_many({})
        except Exception as e:
            cls._log.exception(e, extra=logging_info)
            cls._log.warning('Manga Tagger is unfamiliar with this error. Please log an issue for investigation.',
                             extra=logging_info)
            return

        cls._log.info('Deletion was successful!', extra=logging_info)


class MetadataTable(Database):
    @classmethod
    def initialize(cls):
        cls._log = logging.getLogger(f'{cls.__module__}.{cls.__name__}')
        cls._database = super()._database['manga_metadata']
        cls._log.debug(f'{cls.__name__} class has been initialized')

    @classmethod
    def search_by_search_id(cls, manga_id):
        cls._log.debug(f'Searching manga_metadata cls by key "_id" using value "{manga_id}"')
        return cls._database.find_one({
            '_id': manga_id
        })

    @classmethod
    def search_by_search_value(cls, manga_title):
        cls._log.debug(f'Searching manga_metadata cls by key "search_value" using value "{manga_title}"')
        return cls._database.find_one({'$or': [
            {'search_value': manga_title},
            {'series_title': manga_title},
            {'series_title_eng': manga_title},
            {'series_title_jap': manga_title},
            {'synonyms': manga_title}
        ]})


    @classmethod
    def search_id_by_search_value(cls, manga_title):
        cls._log.debug(f'Searching "series_id" using value "{manga_title}"')
        cursor = cls._database.find_one({"search_value": manga_title}, {"_id": 1})
        return cursor['_id']

    @classmethod
    def search_series_title(cls, manga_title):
        cls._log.debug(f'Searching "series_title" using value "{manga_title}"')
        return cls._database.find_one({"$or": [
            {'search_value': manga_title},
            {'series_title': manga_title},
            {'series_title_eng': manga_title},
            {'series_title_jap': manga_title},
            {'synonyms': manga_title}
        ]}, {'series_title': 1})['series_title']

class ProcFilesTable(Database):
    @classmethod
    def initialize(cls):
        cls._log = logging.getLogger(f'{cls.__module__}.{cls.__name__}')
        cls._database = super()._database['processed_files']
        cls._log.debug(f'{cls.__name__} class has been initialized')

    @classmethod
    def search(cls, manga_title, chapter_number):
        cls._log.debug(f'Searching processed_files cls by keys "series_title" and "chapter_number" '
                       f'using values "{manga_title}" and {chapter_number}')
        return cls._database.find_one({
            'series_title': manga_title,
            'chapter_number': chapter_number
        })

    @classmethod
    def insert_record(cls, old_file_path: Path, new_file_path: Path, manga_title, chapter, logging_info):
        record = {
            "series_title": manga_title,
            "chapter_number": chapter,
            "old_filename": old_file_path.name,
            "new_filename": new_file_path.name,
            "process_date": datetime.now().date().strftime('%Y-%m-%d @ %I:%M:%S %p')
        }

        cls._log.debug(f'Record: {record}')

        logging_info['inserted_processed_record'] = record
        cls._database.insert(record, logging_info)

    @classmethod
    def update_record(cls, results, old_file_path: Path, new_file_path: Path, logging_info):
        record = {
            "$set": {
                "old_filename": old_file_path.name,
                "update_date": datetime.now().date().strftime('%Y-%m-%d @ %I:%M:%S %p')
            }
        }
        cls._log.debug(f'Record: {record}')

        logging_info['updated_processed_record'] = record
        cls._database.update(results, record, logging_info)


class ProcSeriesTable(Database):
    processed_series = set()

    @classmethod
    def initialize(cls):
        cls._log = logging.getLogger(f'{cls.__module__}.{cls.__name__}')
        cls._database = super()._database['processed_series']
        cls._id = None
        cls._last_save_time = None
        cls._log.debug(f'{cls.__name__} class has been initialized')

    @classmethod
    def save(cls):
        cls._log.info('Saving processed series...')
        cls._database.delete_one({
            '_id': cls._id
        })
        super(ProcSeriesTable, cls).insert(dict.fromkeys(cls.processed_series, True))

    @classmethod
    def load(cls):
        cls._log.info('Loading processed series...')
        results = cls._database.find_one()
        if results is not None:
            cls._id = results.pop('_id')
            cls.processed_series = set(results.keys())

    @classmethod
    def save_while_running(cls):
        if cls._last_save_time is not None:
            last_save_delta = (datetime.now() - cls._last_save_time).total_seconds()

            # Save every hour
            if last_save_delta > 3600:
                cls._last_save_time = datetime.now()
                cls.save()


class TaskQueueTable(Database):
    @classmethod
    def initialize(cls):
        cls._log = logging.getLogger(f'{cls.__module__}.{cls.__name__}')
        cls._database = super()._database['task_queue']
        cls.queue = Queue()
        cls._log.debug(f'{cls.__name__} class has been initialized')

    @classmethod
    def load(cls, task_list: dict):
        cls._log.info('Loading task queue...')
        results = cls._database.find()

        if results is not None:
            for result in results:
                task_list[result['manga_chapter']] = result

    @classmethod
    def save(cls, queue):
        if not queue.empty():
            cls._log.info('Saving task queue...')
            while not queue.empty():
                event = queue.get()
                super(TaskQueueTable, cls).insert(event.dictionary())

    @classmethod
    def delete_all(cls):
        super(TaskQueueTable, cls).delete_all(None)
