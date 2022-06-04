import json
import logging
import os
import unittest
from pathlib import Path
from unittest.mock import patch

from MangaTaggerLib.api import AniList
from MangaTaggerLib.MangaTaggerLib import metadata_tagger, construct_comicinfo_xml
from MangaTaggerLib.models import Metadata
from tests.database import MetadataTable as MetadataTableTest


# noinspection DuplicatedCode
class TestMetadata(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data_dir = 'tests/data'
        cls.data_file = 'data.json'

    def setUp(self) -> None:
        logging.disable(logging.CRITICAL)
        AniList.initialize()
        self.maxDiff = None
        patch1 = patch('MangaTaggerLib.models.AppSettings')
        self.models_AppSettings = patch1.start()
        self.addCleanup(patch1.stop)
        self.models_AppSettings.timezone = 'America/New_York'

        patch2 = patch('MangaTaggerLib.MangaTaggerLib.MetadataTable')
        self.MetadataTable = patch2.start()
        self.addCleanup(patch2.stop)
        self.MetadataTable.search_by_search_value = MetadataTableTest.search_return_no_results
        self.MetadataTable.search_by_series_title = MetadataTableTest.search_return_no_results
        self.MetadataTable.search_by_series_title_eng = MetadataTableTest.search_return_no_results

        patch3 = patch('MangaTaggerLib.MangaTaggerLib.AppSettings')
        self.MangaTaggerLib_AppSettings = patch3.start()
        self.addCleanup(patch3.stop)

    def test_comicinfo_xml_creation_case_1(self):
        title = 'BLEACH'

        self.MangaTaggerLib_AppSettings.mode_settings = {}

        with open(Path(self.data_dir, title, self.data_file), encoding='utf-8') as data:
            anilist_details = json.load(data)

        manga_metadata = Metadata(title, {}, anilist_details)

        self.assertTrue(construct_comicinfo_xml(manga_metadata, '001', {}, None))

    def test_comicinfo_xml_creation_case_2(self):
        title = 'Naruto'

        self.MangaTaggerLib_AppSettings.mode_settings = {}

        with open(Path(self.data_dir, title, self.data_file), encoding='utf-8') as data:
            anilist_details = json.load(data)

        manga_metadata = Metadata(title, {}, anilist_details)

        self.assertTrue(construct_comicinfo_xml(manga_metadata, '001', {}, None))

    def test_metadata_case_1(self):
        title = 'BLEACH'

        self.MangaTaggerLib_AppSettings.mode_settings = {'write_comicinfo': False}
        self.MangaTaggerLib_AppSettings.mode_settings = {'rename_file': False}

        with open(Path(self.data_dir, title, self.data_file), encoding='utf-8') as data:
            anilist_details = json.load(data)

        expected_manga_metadata = Metadata(title, {}, anilist_details)
        actual_manga_metadata = metadata_tagger("NOWHERE", title, '001', "MANGA", {}, None)

        self.assertEqual(expected_manga_metadata.test_value(), actual_manga_metadata.test_value())

    def test_metadata_case_2(self):
        title = 'Naruto'

        self.MangaTaggerLib_AppSettings.mode_settings = {'write_comicinfo': False}
        self.MangaTaggerLib_AppSettings.mode_settings = {'rename_file': False}

        with open(Path(self.data_dir, title, self.data_file), encoding='utf-8') as data:
            anilist_details = json.load(data)

        expected_manga_metadata = Metadata(title, {}, anilist_details)
        actual_manga_metadata = metadata_tagger("NOWHERE", title, '001', "MANGA", {}, None)

        self.assertEqual(expected_manga_metadata.test_value(), actual_manga_metadata.test_value())

    def test_metadata_case_3(self):
        title = '3D Kanojo Real Girl'
        downloaded_title = '3D Kanojo'

        self.MangaTaggerLib_AppSettings.mode_settings = {'write_comicinfo': False}
        self.MangaTaggerLib_AppSettings.mode_settings = {'rename_file': False}
        self.MangaTaggerLib_AppSettings.adult_result = False

        with open(Path(self.data_dir, title, self.data_file), encoding='utf-8') as data:
            anilist_details = json.load(data)

        expected_manga_metadata = Metadata(title, {}, anilist_details)
        actual_manga_metadata = metadata_tagger("NOWHERE", downloaded_title, '001', "MANGA", {}, None)

        self.assertEqual(expected_manga_metadata.test_value(), actual_manga_metadata.test_value())

    def test_metadata_case_4(self):
        title = 'Hurejasik'
        downloaded_title = 'Bastard'

        self.MangaTaggerLib_AppSettings.mode_settings = {'write_comicinfo': False}
        self.MangaTaggerLib_AppSettings.mode_settings = {'rename_file': False}

        with open(Path(self.data_dir, title, self.data_file), encoding='utf-8') as data:
            anilist_details = json.load(data)

        expected_manga_metadata = Metadata(title, {}, anilist_details)
        actual_manga_metadata = metadata_tagger("NOWHERE", downloaded_title, '001', "MANGA", {}, None)

        self.assertEqual(expected_manga_metadata.test_value(), actual_manga_metadata.test_value())

    def test_metadata_case_5(self):
        title = 'Naruto'

        self.MangaTaggerLib_AppSettings.mode_settings = {'write_comicinfo': False}
        self.MangaTaggerLib_AppSettings.mode_settings = {'rename_file': False}

        with open(Path(self.data_dir, title, self.data_file), encoding='utf-8') as data:
            anilist_details = json.load(data)

        expected_manga_metadata = Metadata(title, {}, anilist_details)
        actual_manga_metadata = metadata_tagger("NOWHERE", title, '001', "ONE_SHOT", {}, None)

        self.assertNotEqual(expected_manga_metadata.test_value(), actual_manga_metadata.test_value())
