import sys
from os.path import join, dirname
from datetime import datetime
import unittest
from unittest.mock import patch
import pandas as pd
from assignr.availability import get_arguments, main

USAGE='USAGE: availability.py -s <start-date> -e <end-date>' \
' FORMAT=MM/DD/YYYY'

TEST_DATE='01/01/2023'
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
            'start_date': None, 'end_date': TEST_DATE
        }
        with self.assertLogs(level='INFO') as cm:
            rc, args = get_arguments(['-e', TEST_DATE])
        self.assertEqual(cm.output, [f"ERROR:root:{USAGE}"])
        self.assertEqual(rc, 99)
        self.assertEqual(args, expected_args)

    def test_missing_end_date(self):
        expected_args = {
            'start_date': TEST_DATE, 'end_date': None
        }
        with self.assertLogs(level='INFO') as cm:
            rc, args = get_arguments(['-s', TEST_DATE])
        self.assertEqual(cm.output, [f"ERROR:root:{USAGE}"])
        self.assertEqual(rc, 99)
        self.assertEqual(args, expected_args)

    def test_invalid_dates(self):
        INVALID_DATE = '01/10/ee'

        expected_args = {
            'start_date': INVALID_DATE, 'end_date': INVALID_DATE
        }
        with self.assertLogs(level='INFO') as cm:
            rc, args = get_arguments(['-s', INVALID_DATE, '-e', INVALID_DATE])
        self.assertEqual(cm.output, [
            f"ERROR:root:Start Date value, {INVALID_DATE} is invalid",
            f"ERROR:root:End Date value, {INVALID_DATE} is invalid",
        ])
        self.assertEqual(rc, 88)
        self.assertEqual(args, expected_args)

    def test_valid_dates(self):
        send_args = [
            '-s', '01/10/2023', '-e', '01/11/2023'
        ]
        expected_args = {
            'start_date': '01/10/2023', 'end_date': '01/11/2023'
        }
        rc, args = get_arguments(send_args)
        self.assertEqual(rc, 0)
        self.assertEqual(args, expected_args)
