import unittest
from os.path import (join, dirname)
from schedule.helpers.utils import (get_arguments, load_translation_file)

USAGE='USAGE: schedule.py -s <town schedule file> -t <town>' 

TOWN_NAME = 'town name'

class TestGetArguments(unittest.TestCase):
    def test_help(self):
        expected_args = {
            'town_file': None, 'town': None
        }
        with self.assertLogs(level='INFO') as cm:
            rc, args = get_arguments(['-h'])
        self.assertEqual(cm.output, [f"ERROR:root:{USAGE}"])
        self.assertEqual(rc, 99)
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


class TestLoadTransactionFile(unittest.TestCase):
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
