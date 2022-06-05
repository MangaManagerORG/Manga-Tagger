import unittest
import logging
import shutil
from pathlib import Path
from typing import List
from unittest.mock import patch

from MangaTaggerLib.MangaTaggerLib import filename_parser, rename_action
from MangaTaggerLib.errors import FileAlreadyProcessedError, FileUpdateNotRequiredError
from tests.database import ProcFilesTable as ProcFilesTableTest

class FilenameParserTestCase(unittest.TestCase):

   def test_filename_parser_manga(self):
       filename = "Naruto -.- Chap 0.cbz"
       directory_name = "Naruto"
       logging_info = { 'event_id': 0, 'manga_title': directory_name, "original_filename": filename }
       expected_result = ("Naruto", "000", "MANGA",None)
       result = filename_parser(filename, logging_info)
       self.assertEqual(expected_result, result)

   def test_filename_parser_decnumber(self):
       filename = "Naruto -.- Chap 15.5.cbz"
       directory_name = "Naruto"
       logging_info = { 'event_id': 0, 'manga_title': directory_name, "original_filename": filename }
       expected_result = ("Naruto", "015.5", "MANGA",None)
       result = filename_parser(filename, logging_info)
       self.assertEqual(expected_result, result)

   def test_filename_parser_oneshot(self):
       ## Naruto Oneshot for the same author
       filename = "Naruto -.- Oneshot.cbz"
       directory_name = "Naruto"
       logging_info = { 'event_id': 0, 'manga_title': directory_name, "original_filename": filename }
       expected_result = ("Naruto", "000", "ONE_SHOT",None)
       result = filename_parser(filename, logging_info)
       self.assertEqual(expected_result, result)

   def test_filename_parser_prologue(self):
       ## Berserk Prologue 1-16 goes back to chapter 1 once the prologue ends.
       filename = "Berserk -.- Prologue 5.cbz"
       directory_name = "Berserk"
       logging_info = { 'event_id': 0, 'manga_title': directory_name, "original_filename": filename }
       expected_result = ("Berserk", "000.5", "MANGA",None)
       result = filename_parser(filename, logging_info)
       self.assertEqual(expected_result, result)

   def test_filename_parser_ignore_fluff(self):
       ## Ignore Volume, chapter name and (part)
       filename = "One Piece -.- Volume 50 Episode 156 A Chapter Name (15).cbz"
       directory_name = "Naruto"
       logging_info = { 'event_id': 0, 'manga_title': directory_name, "original_filename": filename }
       expected_result = ("One Piece", "156", "MANGA","50")
       result = filename_parser(filename, logging_info)
       self.assertEqual(expected_result, result)

   def test_filename_parser_ignore_fluff_2(self):
       ## Ignore Volume, chapter name and (part)
       filename = "Kuma Kuma Kuma Bear -.- Ch. 064 - Kuma-san and the Shop's Opening Day 2.cbz"
       directory_name = "Kuma Kuma Kuma Bear"
       logging_info = {'event_id': 0, 'manga_title': directory_name, "original_filename": filename}
       expected_result = ("Kuma Kuma Kuma Bear", "064", "MANGA", None)
       result = filename_parser(filename, logging_info)
       self.assertEqual(expected_result, result)
class TestMangaRenameAction(unittest.TestCase):
    download_dir = Path('tests/downloads')
    library_dir = Path('tests/library')
    current_file = None
    new_file = None

    @classmethod
    def setUpClass(cls) -> None:
        logging.disable(logging.CRITICAL)
        cls.current_file = Path(cls.download_dir, 'Absolute Boyfriend -.- Absolute Boyfriend 01 Lover Shop.cbz')
        cls.new_file = Path(cls.library_dir, 'Absolute Boyfriend 001.cbz')

    def setUp(self) -> None:
        self.download_dir.mkdir()
        self.library_dir.mkdir()

    def tearDown(self) -> None:
        shutil.rmtree(self.download_dir)
        shutil.rmtree(self.library_dir)

    @patch('MangaTaggerLib.MangaTaggerLib.ProcFilesTable')
    @patch('MangaTaggerLib.MangaTaggerLib.CURRENTLY_PENDING_RENAME', new_callable=list)
    def test_rename_action_initial(self, CURRENTLY_PENDING_RENAME: List, ProcFilesTable):
        """
        Tests for initial file rename when no results are returned from the database. Test should execute without error.
        """
        self.current_file.touch()
        ProcFilesTable.search = ProcFilesTableTest.search_return_no_results

        CURRENTLY_PENDING_RENAME.append(self.new_file)

        self.assertFalse(rename_action(self.current_file, self.new_file, 'Absolute Boyfriend', '01', {}))

    @patch('MangaTaggerLib.MangaTaggerLib.ProcFilesTable')
    def test_rename_action_duplicate(self, ProcFilesTable):
        """
        Tests for duplicate file rename when results are returned from the database. Test should assert
        FileAlreadyProcessedError.
        """
        self.current_file.touch()
        ProcFilesTable.search = ProcFilesTableTest.search_return_results

        with self.assertRaises(FileAlreadyProcessedError):
            rename_action(self.current_file, self.new_file, 'Absolute Boyfriend', '01', {})

    @patch('MangaTaggerLib.MangaTaggerLib.ProcFilesTable')
    def test_rename_action_downgrade(self, ProcFilesTable):
        """
        Tests for version in file rename when results are returned from the database. Since the current file is a
        lower version than the existing file, test should assert FileUpdateNotRequiredError.
        """
        self.current_file.touch()
        ProcFilesTable.search = ProcFilesTableTest.search_return_results_version

        with self.assertRaises(FileUpdateNotRequiredError):
            rename_action(self.current_file, self.new_file, 'Absolute Boyfriend', '01', {})

    @patch('MangaTaggerLib.MangaTaggerLib.ProcFilesTable')
    def test_rename_action_version_duplicate(self, ProcFilesTable):
        """
        Tests for version and duplicate file rename when results are returned from the database. Since the current
        version is the same as the one in the database, test should assert FileUpdateNotRequiredError.
        """
        self.current_file = Path(self.download_dir, 'Absolute Boyfriend -.- Absolute Boyfriend 01 Lover Shop v2.cbz')
        self.current_file.touch()

        ProcFilesTable.search = ProcFilesTableTest.search_return_results_version

        with self.assertRaises(FileUpdateNotRequiredError):
            rename_action(self.current_file, self.new_file, 'Absolute Boyfriend', '01', {})

    @patch('MangaTaggerLib.MangaTaggerLib.ProcFilesTable')
    @patch('MangaTaggerLib.MangaTaggerLib.CURRENTLY_PENDING_RENAME', new_callable=list)
    def test_rename_action_upgrade(self, CURRENTLY_PENDING_RENAME: List, ProcFilesTable):
        """
        Tests for version in file rename when results are returned from the database. Since the current file is a
        higher version than the exisitng file, test should execute without error.
        """
        self.current_file = Path(self.download_dir, 'Absolute Boyfriend -.- Absolute Boyfriend 01 Lover Shop v3.cbz')
        self.current_file.touch()

        self.new_file.touch()
        CURRENTLY_PENDING_RENAME.append(self.new_file)

        ProcFilesTable.search = ProcFilesTableTest.search_return_results_version

        self.assertFalse(rename_action(self.current_file, self.new_file, 'Absolute Boyfriend', '01', {}))



