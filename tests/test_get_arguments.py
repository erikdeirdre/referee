import unittest
from getopt import GetoptError
from referee import get_arguments

USAGE = 'USAGE: referee.py -m <master schedule file> -s <town schedule file>'
'-t <town> -f <field conversion file> -o <output file name> -e <sport engine file>'

TOWN_NAME = 'town name'

class TestGetArguments(unittest.TestCase):
    def test_help(self):
        expected_args = {
            'master_file': None, 'town_file': None, 'town': None,
            'se_file': None, 'output_file': None, 'field_file': None
        }
        with self.assertLogs(level='INFO') as cm:
            rc, args = get_arguments(['-h'])
        self.assertEqual(cm.output, [f"ERROR:root:{USAGE}"])
        self.assertEqual(rc, 99)
        self.assertEqual(args, expected_args)

    def test_invalid_options(self):
        expected_args = {
            'master_file': None, 'town_file': None, 'town': None,
            'se_file': None, 'output_file': None, 'field_file': None
        }
        with self.assertLogs(level='INFO') as cm:
            rc, args = get_arguments(['-n'])
        self.assertEqual(cm.output, [f"ERROR:root:{USAGE}"])
        self.assertEqual(rc, 77)
        self.assertEqual(args, expected_args)
        
    def test_missing_town_name(self):
        expected_args = {
            'master_file': None, 'town_file': 'town_file', 'town': None,
            'se_file': None, 'output_file': 'output', 'field_file': None
        }
        with self.assertLogs(level='INFO') as cm:
            rc, args = get_arguments(['-o', 'output', '-s', 'town_file'])
        self.assertEqual(cm.output, [f"ERROR:root:{USAGE}"])
        self.assertEqual(rc, 99)
        self.assertEqual(args, expected_args)

    def test_missing_town_file(self):
        expected_args = {
            'master_file': None, 'town_file': None, 'town': 'town',
            'se_file': None, 'output_file': 'output', 'field_file': None
        }
        with self.assertLogs(level='INFO') as cm:
            rc, args = get_arguments(['-o', 'output', '-t', 'town'])
        self.assertEqual(cm.output, [f"ERROR:root:{USAGE}"])
        self.assertEqual(rc, 99)
        self.assertEqual(args, expected_args)

    def test_missing_master_file(self):
        expected_args = {
            'master_file': None, 'town_file': None, 'town': 'town',
            'se_file': 'sport', 'output_file': None, 'field_file': None
        }
        with self.assertLogs(level='INFO') as cm:
            rc, args = get_arguments(['-e', 'sport', '-t', 'town'])
        self.assertEqual(cm.output, [f"ERROR:root:{USAGE}"])
        self.assertEqual(rc, 99)
        self.assertEqual(args, expected_args)

    def test_missing_field_file(self):
        expected_args = {
            'master_file': 'master', 'town_file': None, 'town': 'town',
            'se_file': None, 'output_file': None, 'field_file': None
        }
        with self.assertLogs(level='INFO') as cm:
            rc, args = get_arguments(['-m', 'master', '-t', 'town'])
        self.assertEqual(cm.output, [f"ERROR:root:{USAGE}"])
        self.assertEqual(rc, 99)
        self.assertEqual(args, expected_args)

    def test_missing_output_file(self):
        expected_args = {
            'master_file': 'master', 'town_file': None, 'town': None,
            'se_file': None, 'output_file': 'output', 'field_file': None
        }
        with self.assertLogs(level='INFO') as cm:
            rc, args = get_arguments(['-o', 'output', '-m', 'master'])
        self.assertEqual(cm.output, [f"ERROR:root:{USAGE}"])
        self.assertEqual(rc, 99)
        self.assertEqual(args, expected_args)

    def test_valid_no_se_file(self):
        send_args = [
            '-m', 'master_file', '-s', 'town_file', '-t', TOWN_NAME,
            '-o', 'output_file', '-f', 'field_file'
        ]
        expected_args = {
            'master_file': 'master_file', 'town_file': 'town_file',
            'town': TOWN_NAME, 'se_file': None, 'output_file': 'output_file',
            'field_file': 'field_file'
        }
        rc, args = get_arguments(send_args)
        self.assertEqual(rc, 0)
        self.assertEqual(args, expected_args)

    def test_valid_se_file(self):
        send_args = [
            '-m', 'master_file', '-s', 'town_file', '-t', TOWN_NAME,
            '-o', 'output_file', '-f', 'field_file', '-e', 'se_file'
        ]
        expected_args = {
            'master_file': 'master_file', 'town_file': 'town_file',
            'town': TOWN_NAME, 'se_file': 'se_file', 
            'output_file': 'output_file', 'field_file': 'field_file'
        }
        rc, args = get_arguments(send_args)
        self.assertEqual(rc, 0)
        self.assertEqual(args, expected_args)