import atexit
import json
import logging
import subprocess
import sys
import os

from logging.handlers import RotatingFileHandler, SocketHandler
from pathlib import Path

import numpy
import psutil
from pythonjsonlogger import jsonlogger

from MangaTaggerLib.database import Database
from MangaTaggerLib.task_queue import QueueWorker
from MangaTaggerLib.api import AniList


class AppSettings:
    mode_settings = None
    timezone = None
    version = None
    image = False
    image_first = False
    adult_result = False
    download_dir = None
    image_dir = None
    library_dir = None
    data_dir = None
    is_network_path = None

    processed_series = None

    _log = None

    @classmethod
    def load(cls):
        settings_location = Path(Path.cwd(), 'settings.json')
        if Path(settings_location).exists():
            with open(settings_location, 'r') as settings_json:
                settings = json.load(settings_json)
        else:
            with open(settings_location, 'w+') as settings_json:
                settings = cls._create_settings()
                json.dump(settings, settings_json, indent=4)

        with open(settings_location, 'r+') as settings_json:
            if os.getenv("MANGA_TAGGER_DB_NAME") is not None:
                settings['database']['database_name'] = os.getenv("MANGA_TAGGER_DB_NAME")
            if os.getenv("MANGA_TAGGER_DB_HOST_ADDRESS") is not None:
                settings['database']['host_address'] = os.getenv("MANGA_TAGGER_DB_HOST_ADDRESS")
            if os.getenv("MANGA_TAGGER_DB_PORT") is not None:
                settings['database']['port'] = int(os.getenv("MANGA_TAGGER_DB_PORT"))
            if os.getenv("MANGA_TAGGER_DB_USERNAME") is not None:
                settings['database']['username'] = os.getenv("MANGA_TAGGER_DB_USERNAME")
            if os.getenv("MANGA_TAGGER_DB_PASSWORD") is not None:
                settings['database']['password'] = os.getenv("MANGA_TAGGER_DB_PASSWORD")
            if os.getenv("MANGA_TAGGER_DB_AUTH_SOURCE") is not None:
                settings['database']['auth_source'] = os.getenv("MANGA_TAGGER_DB_AUTH_SOURCE")
            if os.getenv("MANGA_TAGGER_DB_SELECTION_TIMEOUT") is not None:
                settings['database']['server_selection_timeout_ms'] = int(os.getenv("MANGA_TAGGER_DB_SELECTION_TIMEOUT"))

            if os.getenv("MANGA_TAGGER_DOWNLOAD_DIR") is not None:
                settings['application']['library']['download_dir'] = os.getenv("MANGA_TAGGER_DOWNLOAD_DIR")

            if os.getenv("MANGA_TAGGER_DATA_DIR") is not None:
                settings['application']['data_dir'] = os.getenv("MANGA_TAGGER_DATA_DIR")

            if os.getenv('TZ') is not None:
                settings['application']['timezone'] = os.getenv("TZ")

            if os.getenv("MANGA_TAGGER_DRY_RUN") is not None:
                if os.getenv("MANGA_TAGGER_DRY_RUN").lower() == 'true':
                    settings['application']['dry_run']['enabled'] = True
                elif os.getenv("MANGA_TAGGER_DRY_RUN").lower() == 'false':
                    settings['application']['dry_run']['enabled'] = False
            if os.getenv("MANGA_TAGGER_DB_INSERT") is not None:
                if os.getenv("MANGA_TAGGER_DB_INSERT").lower() == 'true':
                    settings['application']['dry_run']['database_insert'] = True
                elif os.getenv("MANGA_TAGGER_DB_INSERT").lower() == 'false':
                    settings['application']['dry_run']['database_insert'] = False
            if os.getenv("MANGA_TAGGER_RENAME_FILE") is not None:
                if os.getenv("MANGA_TAGGER_RENAME_FILE").lower() == 'true':
                    settings['application']['dry_run']['rename_file'] = True
                elif os.getenv("MANGA_TAGGER_RENAME_FILE").lower() == 'false':
                    settings['application']['dry_run']['rename_file'] = False
            if os.getenv("MANGA_TAGGER_WRITE_COMICINFO") is not None:
                if os.getenv("MANGA_TAGGER_WRITE_COMICINFO").lower() == 'true':
                    settings['application']['dry_run']['write_comicinfo'] = True
                elif os.getenv("MANGA_TAGGER_WRITE_COMICINFO").lower() == 'false':
                    settings['application']['dry_run']['write_comicinfo'] = False

            if os.getenv("MANGA_TAGGER_THREADS") is not None:
                settings['application']['multithreading']['threads'] = int(os.getenv("MANGA_TAGGER_THREADS"))
            if os.getenv("MANGA_TAGGER_MAX_QUEUE_SIZE") is not None:
                settings['application']['multithreading']['max_queue_size'] = int(os.getenv("MANGA_TAGGER_MAX_QUEUE_SIZE"))

            if os.getenv("MANGA_TAGGER_DEBUG_MODE") is not None:
                if os.getenv("MANGA_TAGGER_DEBUG_MODE").lower() == 'true':
                    settings['application']['debug_mode'] = True
                elif os.getenv("MANGA_TAGGER_DEBUG_MODE").lower() == 'false':
                    settings['application']['debug_mode'] = False

            if os.getenv("MANGA_TAGGER_IMAGE_COVER") is not None:
                if os.getenv("MANGA_TAGGER_IMAGE_COVER").lower() == 'true':
                    settings['application']['image']['enabled'] = True
                elif os.getenv("MANGA_TAGGER_IMAGE_COVER").lower() == 'first':
                    settings['application']['image']['enabled'] = True
                    settings['application']['image']['first'] = True
                elif os.getenv("MANGA_TAGGER_IMAGE_COVER").lower() == 'false':
                    settings['application']['image']['enabled'] = False
            if os.getenv("MANGA_TAGGER_IMAGE_DIR") is not None:
                settings['application']['image']['image_dir'] = os.getenv("MANGA_TAGGER_IMAGE_DIR")

            if os.getenv("MANGA_TAGGER_ADULT_RESULT") is not None:
                if os.getenv("MANGA_TAGGER_ADULT_RESULT").lower() == 'true':
                    settings['application']['adult_result'] = True
                elif os.getenv("MANGA_TAGGER_ADULT_RESULT").lower() == 'false':
                    settings['application']['adult_result'] = False

            if os.getenv("MANGA_TAGGER_LIBRARY_DIR") is not None:
                settings['application']['library']['dir'] = os.getenv("MANGA_TAGGER_LIBRARY_DIR")

            if os.getenv("MANGA_TAGGER_LOGGING_LEVEL") is not None:
                settings['logger']['logging_level'] = os.getenv("MANGA_TAGGER_LOGGING_LEVEL")
            if os.getenv("MANGA_TAGGER_LOGGING_DIR") is not None:
                settings['logger']['log_dir'] = os.getenv("MANGA_TAGGER_LOGGING_DIR")
            if os.getenv("MANGA_TAGGER_LOGGING_CONSOLE") is not None:
                if os.getenv("MANGA_TAGGER_LOGGING_CONSOLE").lower() == 'true':
                    settings['logger']['console']['enabled'] = True
                elif os.getenv("MANGA_TAGGER_LOGGING_CONSOLE").lower() == 'false':
                    settings['logger']['console']['enabled'] = False
            if os.getenv("MANGA_TAGGER_LOGGING_FILE") is not None:
                if os.getenv("MANGA_TAGGER_LOGGING_FILE").lower() == 'true':
                    settings['logger']['file']['enabled'] = True
                elif os.getenv("MANGA_TAGGER_LOGGING_FILE").lower() == 'false':
                    settings['logger']['file']['enabled'] = False
            if os.getenv("MANGA_TAGGER_LOGGING_JSON") is not None:
                if os.getenv("MANGA_TAGGER_LOGGING_JSON").lower() == 'true':
                    settings['logger']['json']['enabled'] = True
                elif os.getenv("MANGA_TAGGER_LOGGING_JSON").lower() == 'false':
                    settings['logger']['json']['enabled'] = False
            if os.getenv("MANGA_TAGGER_LOGGING_TCP") is not None:
                if os.getenv("MANGA_TAGGER_LOGGING_TCP").lower() == 'true':
                    settings['logger']['tcp']['enabled'] = True
                elif os.getenv("MANGA_TAGGER_LOGGING_TCP").lower() == 'false':
                    settings['logger']['tcp']['enabled'] = False
            if os.getenv("MANGA_TAGGER_LOGGING_JSONTCP") is not None:
                if os.getenv("MANGA_TAGGER_LOGGING_JSONTCP").lower() == 'true':
                    settings['logger']['json_tcp']['enabled'] = True
                elif os.getenv("MANGA_TAGGER_LOGGING_JSONTCP").lower() == 'false':
                    settings['logger']['json_tcp']['enabled'] = False

        with open(settings_location, 'w+') as settings_json:
                json.dump(settings, settings_json, indent=4)

        cls._initialize_logger(settings['logger'])
        cls._log = logging.getLogger(f'{cls.__module__}.{cls.__name__}')

        # Database Configuration
        cls._log.debug('Now setting database configuration...')

        Database.database_name = settings['database']['database_name']
        Database.host_address = settings['database']['host_address']
        Database.port = settings['database']['port']
        Database.username = settings['database']['username']
        Database.password = settings['database']['password']
        Database.auth_source = settings['database']['auth_source']
        Database.server_selection_timeout_ms = settings['database']['server_selection_timeout_ms']

        cls._log.debug('Database settings configured!')
        Database.initialize()
        Database.print_debug_settings()

        # Download Directory Configuration
         # Set the download directory
        if settings['application']['library']['download_dir'] is not None:
            cls.download_dir = Path(settings['application']['library']['download_dir'])
            if not cls.download_dir.exists():
                cls._log.info(f'Library directory "{AppSettings.library_dir}" does not exist; creating now.')
                cls.download_dir.mkdir()
            QueueWorker.download_dir = cls.download_dir
            cls._log.info(f'Download directory has been set as "{QueueWorker.download_dir}"')
        else:
            cls._log.critical('Manga Tagger cannot function without a download directory for moving processed '
                              'files into. Configure one in the "settings.json" and try again.')
            sys.exit(1)

        # Set Application Timezone
        cls.timezone = settings['application']['timezone']
        if os.getenv('TZ') is not None:
            cls.timezone = os.getenv("TZ")
        cls._log.debug(f'Timezone: {cls.timezone}')

        # Dry Run Mode Configuration
        # No logging here due to being handled at the INFO level in MangaTaggerLib
        if settings['application']['dry_run']['enabled']:
            cls.mode_settings = {'database_insert': settings['application']['dry_run']['database_insert'],
                                 'rename_file': settings['application']['dry_run']['rename_file'],
                                 'write_comicinfo': settings['application']['dry_run']['write_comicinfo']}

        # Multithreading Configuration
        if settings['application']['multithreading']['threads'] <= 0:
            QueueWorker.threads = 1
        else:
            QueueWorker.threads = settings['application']['multithreading']['threads']

        cls._log.debug(f'Threads: {QueueWorker.threads}')

        if settings['application']['multithreading']['max_queue_size'] < 0:
            QueueWorker.max_queue_size = 0
        else:
            QueueWorker.max_queue_size = settings['application']['multithreading']['max_queue_size']

        cls._log.debug(f'Max Queue Size: {QueueWorker.max_queue_size}')

        # Debug Mode - Prevent application from processing files
        if settings['application']['debug_mode']:
            QueueWorker._debug_mode = True

        cls._log.debug(f'Debug Mode: {QueueWorker._debug_mode}')

        # Image Directory
        if settings['application']['image']['enabled']:
            cls.image = True
            if settings['application']['image'].get('first'):
                cls.image_first = True
            if settings['application']['image']['image_dir'] is not None:
                if settings['application']['image']['image_dir'] is not None:
                    cls.image_dir = settings['application']['image']['image_dir']
                if not Path(cls.image_dir).exists():
                    cls._log.info(f'Image directory "{cls.image_dir}" does not exist; creating now.')
                    Path(cls.image_dir).mkdir()
                cls._log.debug(f'Image Directory: {cls.image_dir}')
            else:
                cls._log.critical('Image cover is enabled but cannot function without an image directory for moving downloaded cover images '
                              'files into. Configure one in the "settings.json" and try again.')
                sys.exit(1)
        else:
            cls._log.debug(f'Image cover not enabled')

        # Data Dir
        if settings['application']['data_dir'] is not None:
            cls.data_dir = settings['application']['data_dir']
            cls._log.debug(f'Data Directory: {cls.library_dir}')
            if not Path(cls.data_dir).exists():
                cls._log.info(f'Data directory "{AppSettings.library_dir}" does not exist; creating now.')
                Path(cls.data_dir).mkdir()

        # Enable or disable adult result
        if settings['application']['adult_result']:
            cls.adult_result = True
            cls._log.info('Adult result enabled.')

        # Manga Library Configuration
        if settings['application']['library']['dir'] is not None:
            cls.library_dir = settings['application']['library']['dir']
            cls._log.debug(f'Library Directory: {cls.library_dir}')

            cls.is_network_path = settings['application']['library']['is_network_path']

            if not Path(cls.library_dir).exists():
                cls._log.info(f'Library directory "{AppSettings.library_dir}" does not exist; creating now.')
                Path(cls.library_dir).mkdir()
        else:
            cls._log.critical('Manga Tagger cannot function without a library directory for moving processed '
                              'files into. Configure one in the "settings.json" and try again.')
            sys.exit(1)

        # Load necessary database tables
        Database.load_database_tables()

        # Initialize QueueWorker and load task queue
        QueueWorker.initialize()
        QueueWorker.load_task_queue()

        # Scan download directory for downloads not already in database upon loading
        cls._scan_download_dir()

        # Initialize API
        AniList.initialize()

        # Register function to be run prior to application termination
        atexit.register(cls._exit_handler)
        cls._log.debug(f'{cls.__name__} class has been initialized')

    @classmethod
    def _initialize_logger(cls, settings):
        logger = logging.getLogger('MangaTaggerLib')
        logging_level = settings['logging_level']
        log_dir = settings['log_dir']

        if logging_level.lower() == 'info':
            logging_level = logging.INFO
        elif logging_level.lower() == 'debug':
            logging_level = logging.DEBUG
        else:
            logger.critical('Logging level not of expected values "info" or "debug". Double check the configuration'
                            'in settings.json and try again.')
            sys.exit(1)

        logger.setLevel(logging_level)

        # Create log directory and allow the application access to it
        if not Path(log_dir).exists():
            Path(log_dir).mkdir()

        # Console Logging
        if settings['console']['enabled']:
            log_handler = logging.StreamHandler()
            log_handler.setFormatter(logging.Formatter(settings['console']['log_format']))
            logger.addHandler(log_handler)

        # File Logging
        if settings['file']['enabled']:
            log_handler = cls._create_rotating_file_handler(log_dir, 'log', settings, 'utf-8')
            log_handler.setFormatter(logging.Formatter(settings['file']['log_format']))
            logger.addHandler(log_handler)

        # JSON Logging
        if settings['json']['enabled']:
            log_handler = cls._create_rotating_file_handler(log_dir, 'json', settings)
            log_handler.setFormatter(jsonlogger.JsonFormatter(settings['json']['log_format']))
            logger.addHandler(log_handler)

        # Check TCP and JSON TCP for port conflicts before creating the handlers
        if settings['tcp']['enabled'] and settings['json_tcp']['enabled']:
            if settings['tcp']['port'] == settings['json_tcp']['port']:
                logger.critical('TCP and JSON TCP logging are both enabled, but their port numbers are the same. '
                                'Either change the port value or disable one of the handlers in settings.json '
                                'and try again.')
                sys.exit(1)

        # TCP Logging
        if settings['tcp']['enabled']:
            log_handler = SocketHandler(settings['tcp']['host'], settings['tcp']['port'])
            log_handler.setFormatter(logging.Formatter(settings['tcp']['log_format']))
            logger.addHandler(log_handler)

        # JSON TCP Logging
        if settings['json_tcp']['enabled']:
            log_handler = SocketHandler(settings['json_tcp']['host'], settings['json_tcp']['port'])
            log_handler.setFormatter(jsonlogger.JsonFormatter(settings['json_tcp']['log_format']))
            logger.addHandler(log_handler)

    @staticmethod
    def _create_rotating_file_handler(log_dir, extension, settings, encoder=None):
        return RotatingFileHandler(Path(log_dir, f'MangaTagger.{extension}'),
                                   maxBytes=settings['max_size'],
                                   backupCount=settings['backup_count'],
                                   encoding=encoder)

    @classmethod
    def _exit_handler(cls):
        cls._log.info('Initiating shutdown procedures...')

        # Stop worker threads
        QueueWorker.exit()

        # Save necessary database tables
        Database.save_database_tables()

        # Close MongoDB connection
        Database.close_connection()

        cls._log.info('Now exiting Manga Tagger')

    @classmethod
    def _create_settings(cls):

        return {
            "application": {
                "debug_mode": False,
                "timezone": "Europe/Paris",
                "data_dir": "data",
                "image": {
                    "enabled" : True,
                    "image_dir" : "cover"
                },
                "adult_result" : False,
                "library": {
                    "dir": "manga",
                    "is_network_path": False,
                    "download_dir": "downloads"
                },
                "dry_run": {
                    "enabled": False,
                    "rename_file": False,
                    "database_insert": False,
                    "write_comicinfo": False
                },
                "multithreading": {
                    "threads": 8,
                    "max_queue_size": 0
                }
            },
            "database": {
                "database_name": "manga_tagger",
                "host_address": "localhost",
                "port": 27017,
                "username": "manga_tagger",
                "password": "Manga4LYFE",
                "auth_source": "admin",
                "server_selection_timeout_ms": 1
            },
            "logger": {
                "logging_level": "info",
                "log_dir": "logs",
                "max_size": 10485760,
                "backup_count": 5,
                "console": {
                    "enabled": True,
                    "log_format": "%(asctime)s | %(threadName)s %(thread)d | %(name)s | %(levelname)s - %(message)s"
                },
                "file": {
                    "enabled": True,
                    "log_format": "%(asctime)s | %(threadName)s %(thread)d | %(name)s | %(levelname)s - %(message)s"
                },
                "json": {
                    "enabled": False,
                    "log_format": "%(threadName)s %(thread)d %(asctime)s %(name)s %(levelname)s %(message)s"
                },
                "tcp": {
                    "enabled": False,
                    "host": "localhost",
                    "port": 1798,
                    "log_format": "%(threadName)s %(thread)d | %(asctime)s | %(name)s | %(levelname)s - %(message)s"
                },
                "json_tcp": {
                    "enabled": False,
                    "host": "localhost",
                    "port": 1799,
                    "log_format": "%(threadName)s %(thread)d %(asctime)s %(name)s %(levelname)s %(message)s"
                }
            }
        }

    @classmethod
    def _scan_download_dir(cls):
        for directory in QueueWorker.download_dir.iterdir():
            for manga_chapter in directory.glob('*.cbz'):
                if manga_chapter.name.strip('.cbz') not in QueueWorker.task_list.keys():
                    QueueWorker.add_to_task_queue(manga_chapter)

def levenshtein_distance_no_numpy(s1, s2):
    """
    Calculates the Levenshtein distance between two strings without using NumPy.

    Args:
        s1 (str): The first string.
        s2 (str): The second string.

    Returns:
        int: The Levenshtein distance between the two strings.
    """

    rows = len(s1) + 1
    cols = len(s2) + 1
    distance = [[0 for _ in range(cols)] for _ in range(rows)]

    for i in range(1, rows):
        for j in range(1, cols):
            if s1[i - 1] == s2[j - 1]:
                distance[i][j] = distance[i - 1][j - 1]
            else:
                distance[i][j] = min(distance[i - 1][j] + 1, distance[i][j - 1] + 1, distance[i - 1][j - 1] + 1)

    return distance[rows - 1][cols - 1]
def compare(s1, s2):
    s1 = s1.lower().strip('/[^a-zA-Z ]/g", ')
    s2 = s2.lower().strip('/[^a-zA-Z ]/g", ')

    rows = len(s1) + 1
    cols = len(s2) + 1
    distance = levenshtein_distance_no_numpy(s1, s2)

    for i in range(1, rows):
        distance[i][0] = i

    for i in range(1, cols):
        distance[0][i] = i

    for col in range(1, cols):
        for row in range(1, rows):
            if s1[row - 1] == s2[col - 1]:
                cost = 0
            else:
                cost = 2

            distance[row][col] = min(distance[row - 1][col] + 1,
                                     distance[row][col - 1] + 1,
                                     distance[row - 1][col - 1] + cost)

    return ((len(s1) + len(s2)) - distance[row][col]) / (len(s1) + len(s2))
