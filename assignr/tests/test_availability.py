import sys
from os.path import join, dirname
from datetime import datetime
import unittest
from unittest.mock import patch
import pandas as pd
from availability import get_arguments, main

USAGE='USAGE: availability.py -s <start-date> -e <end-date>'


class TestGetArguments(unittest.TestCase):
    def test_help(self):
        expected_args = {
            'start_date': None, 'end_date': None
        }
        with self.assertLogs(level='INFO') as cm:
            rc, args = get_arguments(['-h'])
        self.assertEqual(cm.output, [f"ERROR:root:{USAGE}"])
        self.assertEqual(rc, 99)
        self.assertEqual(args, expected_args)

    def test_invalid_options(self):
        expected_args = {
            'start_date': None, 'end_date': None
        }
        with self.assertLogs(level='INFO') as cm:
            rc, args = get_arguments(['-n'])
        self.assertEqual(cm.output, [f"ERROR:root:{USAGE}"])
        self.assertEqual(rc, 77)
        self.assertEqual(args, expected_args)
        
    def test_missing_start_date(self):
        expected_args = {
            'start_date': None, 'end_date': None
        }
        with self.assertLogs(level='INFO') as cm:
            rc, args = get_arguments(['-o', 'output', '-s', 'town_file'])
        self.assertEqual(cm.output, [f"ERROR:root:{USAGE}"])
        self.assertEqual(rc, 99)
        self.assertEqual(args, expected_args)

    def test_missing_end_date(self):
        expected_args = {
            'start_date': None, 'end_date': None
        }
        with self.assertLogs(level='INFO') as cm:
            rc, args = get_arguments(['-o', 'output', '-t', 'town'])
        self.assertEqual(cm.output, [f"ERROR:root:{USAGE}"])
        self.assertEqual(rc, 99)
        self.assertEqual(args, expected_args)
