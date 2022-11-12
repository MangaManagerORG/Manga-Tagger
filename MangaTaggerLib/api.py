import logging
import requests
from ratelimit import limits, sleep_and_retry

# https://anilist.gitbook.io/anilist-apiv2-docs/overview/rate-limiting
# Will limit to 60 calls per minute, 30 under the max
# With the changes that have been made we shouldn't hit this limit.
# As we are multithreading Run this to be a global limit as opposed to a class defined limit
CALLS = 60
RATE_LIMIT = 60
@sleep_and_retry
@limits(calls=CALLS, period=RATE_LIMIT)
def check_limit():
    """
    Empty function just to check for calls to API
    """
    return

class AniList:
    _log = None

    @classmethod
    def initialize(cls):
        cls._log = logging.getLogger(f'{cls.__module__}.{cls.__name__}')

    @classmethod
    def _post(cls, query, variables, logging_info):
        check_limit()
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

    @classmethod
    def search_details_by_series_title(cls, manga_title, isAdult, format, logging_info):
        query = '''
        query search_details_by_series_title ($manga_title: String, $isAdult: Boolean, $format: MediaFormat) {
          Media (search: $manga_title, type: MANGA, format: $format, isAdult: $isAdult) {
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
            'manga_title': manga_title,
            'isAdult': isAdult,
            'format': format
        }

        return cls._post(query, variables, logging_info)

class AniListRateLimit(Exception):
    """
    Exception raised when AniList rate-limit is breached.
    """