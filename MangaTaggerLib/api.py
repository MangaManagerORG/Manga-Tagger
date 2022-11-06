import logging
import requests
import time
from datetime import datetime
from typing import Optional, Dict, Mapping, Union, Any

class AniList:
    _log = None

    @classmethod
    def initialize(cls):
        cls._log = logging.getLogger(f'{cls.__module__}.{cls.__name__}')

    @classmethod
    def _post(cls, query, variables, logging_info):
        try:
            response = requests.post('https://graphql.anilist.co', json={'query': query, 'variables': variables})
            if response.status_code == 429:  # Anilist rate-limit code
                raise AniListRateLimit()
        except Exception as e:
            cls._log.exception(e, extra=logging_info)
            cls._log.warning('Manga Tagger is unfamiliar with this error. Please log an issue for investigation.',
                             extra=logging_info)
            return None

        cls._log.debug(f'Query: {query}')
        cls._log.debug(f'Variables: {variables}')
        cls._log.debug(f'Response JSON: {response.json()}')
        try:
            return response.json()['data']['Media']
        except TypeError:
            return None

    @classmethod
    def search_for_manga_title_by_id(cls, manga_id, logging_info):
        query = '''
        query search_for_manga_title_by_id ($manga_id: Int) {
          Media (id: $manga_id, type: MANGA) {
            id
            title {
              romaji
              english
              native
            }
            synonyms
          }
        }
        '''

        variables = {
            'manga_id': manga_id,
        }

        return cls._post(query, variables, logging_info)

    @classmethod
    def search_for_manga_title_by_manga_title(cls, manga_title, format, logging_info):
        query = '''
        query search_manga_by_manga_title ($manga_title: String, $format: MediaFormat) {
          Media (search: $manga_title, type: MANGA, format: $format, isAdult: false) {
            id
            title {
              romaji
              english
              native
            }
            synonyms
          }
        }
        '''

        variables = {
            'manga_title': manga_title,
            'format': format
        }

        return cls._post(query, variables, logging_info)

    @classmethod
    def search_for_manga_title_by_manga_title_with_adult(cls, manga_title, format, logging_info):
        query = '''
        query search_manga_by_manga_title ($manga_title: String, $format: MediaFormat) {
          Media (search: $manga_title, type: MANGA, format: $format) {
            id
            title {
              romaji
              english
              native
            }
            synonyms
          }
        }
        '''

        variables = {
            'manga_title': manga_title,
            'format': format
        }

        return cls._post(query, variables, logging_info)

    @classmethod
    def search_details_by_series_id(cls, series_id, format, logging_info):
        query = '''
        query search_details_by_series_id ($series_id: Int, $format: MediaFormat) {
          Media (id: $series_id, type: MANGA, format: $format) {
            id
            status
            volumes
            siteUrl
            title {
              romaji
              english
              native
            }
            type
            genres
            synonyms
            startDate {
              day
              month
              year
            }
            coverImage {
              extraLarge
            }
            staff {
              edges {
                node{
                  name {
                    first
                    last
                    full
                    alternative
                  }
                  siteUrl
                }
                role
              }
            }
            description
          }
        }
        '''

        variables = {
            'series_id': series_id,
            'format': format
        }
        
        return cls._post(query, variables, logging_info)


class AniListRateLimit(Exception):
    """
    Exception raised when AniList rate-limit is breached.
    """