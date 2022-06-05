import logging
from datetime import datetime
from pytz import timezone

from MangaTaggerLib.errors import MetadataNotCompleteError
from MangaTaggerLib.utils import AppSettings, compare


class Metadata:
    _log = None

    @classmethod
    def fully_qualified_class_name(cls):
        return f'{cls.__module__}.{cls.__name__}'

    def __init__(self, manga_title, logging_info, anilist_details=None, details=None):
        Metadata._log = logging.getLogger(self.fully_qualified_class_name())

        self.search_value = manga_title
        Metadata._log.info(f'Creating Metadata model for series "{manga_title}"...', extra=logging_info)

        if anilist_details:  # If details are grabbed from Anilist APIs
            self._construct_api_metadata(anilist_details, logging_info)
        elif details:  # If details were stored in the database
            self._construct_database_metadata(details)
        else:
            Metadata._log.exception(MetadataNotCompleteError, extra=logging_info)
        Metadata._log.debug(f'{self.search_value} Metadata Model: {self.__dict__.__str__()}')

        logging_info['metadata'] = self.__dict__
        Metadata._log.info('Successfully created Metadata model.', extra=logging_info)

    def _construct_api_metadata(self, anilist_details, logging_info):
        self._id = anilist_details['id']
        self.series_title = anilist_details['title']['romaji']

        if anilist_details['title']['english'] == 'None' or anilist_details['title']['english'] is None:
            self.series_title_eng = None
        else:
            self.series_title_eng = anilist_details['title']['english']

        if anilist_details['title']['native'] == 'None' or anilist_details['title']['native'] is None:
            self.series_title_jap = None
        else:
            self.series_title_jap = anilist_details['title']['native']

        self.status = anilist_details['status']
        if anilist_details.get('volumes'):
            self.volumes = anilist_details.get('volumes')
        else:
            self.volumes = None

        self.type = anilist_details['type']
        self.description = anilist_details['description']
        self.anilist_url = anilist_details['siteUrl']
        self.publish_date = None
        self.genres = []
        self.staff = {}

        self._construct_publish_date(anilist_details['startDate'])
        self._parse_genres(anilist_details['genres'], logging_info)
        self._parse_staff(anilist_details['staff']['edges'], logging_info)

        self.scrape_date = timezone(AppSettings.timezone).localize(datetime.now()).strftime('%Y-%m-%d %I:%M %p %Z')

    def _construct_database_metadata(self, details):
        self._id = details['_id']
        self.series_title = details['series_title']
        self.series_title_eng = details['series_title_eng']
        self.series_title_jap = details['series_title_jap']
        self.status = details['status']
        self.volumes = details.get("volumes")
        self.type = details['type']
        self.description = details['description']
        self.anilist_url = details['anilist_url']
        self.publish_date = details['publish_date']
        self.genres = details['genres']
        self.staff = details['staff']
        self.publish_date = details['publish_date']
        self.scrape_date = details['scrape_date']

    def _construct_publish_date(self, date):
        if date['month'] == 'None' or date['day'] == 'None' or date['day'] is None or date['month'] is None:
            yearstr = str(date.get('year'))
            datestr = yearstr + "-" + "01" + "-" "01"
        else:
            datestr = str(date.get('year')) + "-" + str(date.get('month')) + "-" + str(date.get('day'))
        self.publish_date = datetime.strptime(datestr, '%Y-%m-%d').strftime('%Y-%m-%d')
        Metadata._log.debug(f'Publish date constructed: {self.publish_date}')

    def _parse_genres(self, genres, logging_info):
        Metadata._log.info('Parsing genres...', extra=logging_info)
        for genre in genres:
            Metadata._log.debug(f'Genre found: {genre}')
            self.genres.append(genre)

    def _parse_staff(self, anilist_staff, logging_info):
        Metadata._log.info('Parsing staff roles...', extra=logging_info)

        roles = []

        self.staff = {
            'story': {},
            'art': {}
        }

        for a_staff in anilist_staff:
            Metadata._log.debug(f'Staff Member (Anilist): {a_staff}')

            anilist_staff_name = ''

            if a_staff['node']['name']['last'] is not None:
                anilist_staff_name = a_staff['node']['name']['last']

            if a_staff['node']['name']['first'] is not None:
                anilist_staff_name += ', ' + a_staff['node']['name']['first']

            names_to_compare = [anilist_staff_name]
            if '' not in a_staff['node']['name']['alternative']:
                for name in a_staff['node']['name']['alternative']:
                    names_to_compare.append(name)
 
            role = a_staff['role'].lower()
            if 'story & art' in role:
                roles.append('story')
                roles.append('art')
                self._add_anilist_staff_member('story', a_staff)
                self._add_anilist_staff_member('art', a_staff)
            elif 'story' in role:
                roles.append('story')
                self._add_anilist_staff_member('story', a_staff)
            elif 'art' in role:
                roles.append('art')
                self._add_anilist_staff_member('art', a_staff)
            else:
                Metadata._log.warning(f'Expected role not found for staff member "{a_staff}"; instead'
                                      f' found "{role}"', extra=logging_info)
                
        # Validate expected roles for staff members
        role_set = ['story', 'art']

        if set(roles) != set(role_set):

            Metadata._log.warning(f'Not all expected roles are present for series "{self.search_value}"; '
                                  f'double check ID "{self._id}"', extra=logging_info)

    def _add_anilist_staff_member(self, role, a_staff):
        self.staff[role][a_staff['node']['name']['full']] = {
            'first_name': a_staff['node']['name']['first'],
            'last_name': a_staff['node']['name']['last'],
            'anilist_url': a_staff['node']['siteUrl'],
        }

    def _parse_serializations(self, serializations, logging_info):
        Metadata._log.info('Parsing serializations...', extra=logging_info)
        for serialization in serializations:
            Metadata._log.debug(serialization)
            self.serializations[serialization['name'].strip('.')] = {
                'mal_id': serialization['mal_id'],
                'url': serialization['url']
            }

    def test_value(self):
        return {
            'series_title': self.series_title,
            'series_title_eng': self.series_title_eng,
            'series_title_jap': self.series_title_jap,
            'status': self.status,
            'volumes':self.volumes,
#            'mal_url': self.mal_url,
            'anilist_url': self.anilist_url,
            'publish_date': self.publish_date,
            'genres': self.genres,
            'staff': self.staff,
#            'serializations': self.serializations
        }
