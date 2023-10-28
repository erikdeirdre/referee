from unittest import (TestCase, mock)
from os import environ
from os.path import (join, dirname)
from schedule.helpers.utils import (get_arguments, load_translation_file,
                                    get_environment)

USAGE='USAGE: schedule.py -s <town schedule file> -t <town>' 

TOWN_NAME = 'town name'

class TestGetArguments(TestCase):
    def test_help(self):
        expected_args = {
            'town_file': None, 'town': None
        }
        with self.assertLogs(level='INFO') as cm:
            rc, args = get_arguments(['-h'])
        self.assertEqual(cm.output, [f"ERROR:root:{USAGE}"])
        self.assertEqual(rc, 99)
        self.assertEqual(args, expected_args)

    def test_valid_options(self):
        expected_args = {'town_file': 'test_file', 'town': 'test'}
        rc, args = get_arguments(['-t', 'test', '-s', 'test_file'])
        self.assertEqual(rc, 0)
        self.assertEqual(args, expected_args)

    def test_invalid_options(self):
        expected_args = {'town_file': None, 'town': None}
        with self.assertLogs(level='INFO') as cm:
            rc, args = get_arguments(['-n'])
        self.assertEqual(cm.output, [f"ERROR:root:{USAGE}"])
        self.assertEqual(rc, 77)
        self.assertEqual(args, expected_args)
        
    def test_missing_town_name(self):
        expected_args = {'town_file': 'town_file', 'town': None}
        with self.assertLogs(level='INFO') as cm:
            rc, args = get_arguments(['-s', 'town_file'])
        self.assertEqual(cm.output, [f"ERROR:root:{USAGE}"])
        self.assertEqual(rc, 99)
        self.assertEqual(args, expected_args)

    def test_missing_town_file(self):
        expected_args = {'town_file': None, 'town': 'town'}
        with self.assertLogs(level='INFO') as cm:
            rc, args = get_arguments(['-t', 'town'])
        self.assertEqual(cm.output, [f"ERROR:root:{USAGE}"])
        self.assertEqual(rc, 99)
        self.assertEqual(args, expected_args)


class TestGetEnvironment(TestCase):
    @mock.patch.dict(environ,{
    "MASTER_SCHEDULE_ID": "schedule_id",
    "RANGE_NAME": "range_name",
    "OUTPUT_FILE_PREFIX": "file_prefix",
    "GOOGLE_APPLICATION_CREDENTIALS": "dontshare",
    "TRANSLATION_FILE": "translation_file"
    }, clear=True)
    def test_all_variables_set(self):
        expected_result = {
            'spreadsheet_id': 'schedule_id',
            'range_name': 'range_name',
            'translation_file': 'translation_file',
            'output_file_prefix': 'file_prefix',
            'credentials': 'dontshare'
        }
        rc, result = get_environment()
        self.assertEqual(rc, 0)
        self.assertEqual(result, expected_result)

    @mock.patch.dict(environ,{
    "RANGE_NAME": "range_name",
    "OUTPUT_FILE_PREFIX": "file_prefix",
    "GOOGLE_APPLICATION_CREDENTIALS": "dontshare",
    "TRANSLATION_FILE": "translation_file"
    }, clear=True)
    def test_missing_master_id(self):
        expected_result = {
            'range_name': 'range_name',
            'translation_file': 'translation_file',
            'output_file_prefix': 'file_prefix',
            'credentials': 'dontshare'
        }

        with self.assertLogs(level='INFO') as cm:
            rc, result = get_environment()
        self.assertEqual(rc, 66)
        self.assertEqual(cm.output,
                         ['ERROR:root:MASTER_SCHEDULE_ID environment variable is missing'])
        self.assertEqual(result, expected_result)

    @mock.patch.dict(environ,{
    "MASTER_SCHEDULE_ID": "schedule_id",
    "RANGE_NAME": "range_name",
    "GOOGLE_APPLICATION_CREDENTIALS": "dontshare",
    }, clear=True)
    def test_default_values(self):
        expected_result = {
            'spreadsheet_id': 'schedule_id',
            'range_name': 'range_name',
            'translation_file': 'files/translations.json',
            'output_file_prefix': 'schedule',
            'credentials': 'dontshare'
        }

        with self.assertLogs(level='INFO') as cm:
            rc, result = get_environment()
        self.assertEqual(rc, 0)
        self.assertEqual(cm.output,
                         ['WARNING:root:TRANSLATION_FILE environment variable is missing, using default',
                          'WARNING:root:OUTPUT_FILE_PREFIX environment variable is missing, using default'])
        self.assertEqual(result, expected_result)

    def test_missing_everything(self):
        expected_result = {
            'translation_file': 'files/translations.json',
            'output_file_prefix': 'schedule'
        }

        with self.assertLogs(level='INFO') as cm:
            rc, result = get_environment()
        self.assertEqual(rc, 66)
        self.assertEqual(cm.output,
                         ['ERROR:root:MASTER_SCHEDULE_ID environment variable is missing',
                          'ERROR:root:RANGE_NAME environment variable is missing',
                          'WARNING:root:TRANSLATION_FILE environment variable is missing, using default',
                          'WARNING:root:OUTPUT_FILE_PREFIX environment variable is missing, using default',
                          'ERROR:root:GOOGLE_APPLICATION_CREDENTIALS environment variable is missing'])
        self.assertEqual(result, expected_result)


class TestLoadTransactionFile(TestCase):
    def test_valid_file(self):
        expected_json = {
            "age_groups": {
                "3rd_4th": "Grade 3/4",
                "5th_6th": "Grade 5/6",
                "7th_8th": "Grade 7/8"     
            },
            "fields": {
                "Boston": {
                    "Field1": {
                        "venue": "High School",
                        "sub-venue": "Field One"
                    },
                    "Field2": {
                        "venue": "HS",
                        "sub-venue": "Field Two"
                    }
                }
            }
        }

        actual_json, rc = load_translation_file(join(dirname(__file__),'files' ,'translations.json'))
        self.assertEqual(rc, 0)
        self.assertEqual(actual_json, expected_json)

    def test_invalid_file(self):
        with self.assertLogs(level='INFO') as cm:
            fields, rc = load_translation_file('file_does_not_exist.json')
        self.assertEqual(
            cm.output, ["ERROR:root:No such file or directory: file_does_not_exist.json"]
        )
        self.assertEqual(rc, 66)
        self.assertEqual(fields, {})
