import sys
import os
from datetime import datetime
from unittest import TestCase
import pytest
from unittest.mock import patch
import pandas as pd
from assignr.availability import (get_arguments, authenticate,
                                  get_availability, get_referees, main)
from mock_assignr_response import (mocked_requests_post, mocked_requests_get)

USAGE='USAGE: availability.py -s <start-date> -e <end-date>' \
' FORMAT=MM/DD/YYYY'

TEST_DATE='01/01/2023'

@pytest.fixture(autouse=True)
def mock_settings_env_vars():
    with patch.dict(os.environ, {
        "CLIENT_ID": "clientid",
        "CLIENT_SECRET": "clientsecret",
        "CLIENT_SCOPE": "read write",
        "AUTH_URL": "http://test.com/oauth/token",
        "BASE_URL": "http://test.com/api/v2/",
        "REDIRECT_URI": "urn:ietf:wg:oauth:2.0:oob"
    }):
        yield

class TestGetArguments(TestCase):
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

    @patch.dict(os.environ, {"AUTH_URL": "http://test.com/oauth/valid"})
    @patch('requests.post', side_effect=mocked_requests_post)
    def test_valid_token(self, mock_post):
        token = authenticate()
        self.assertEqual(token, "validtoken")


    @patch.dict(os.environ, {"AUTH_URL": "http://test.com/oauth/invalid"})
    @patch('requests.post', side_effect=mocked_requests_post)
    def test_invalid_token(self, mock_post):
        with self.assertLogs(level='INFO') as cm:
            token = authenticate()

        self.assertEqual(cm.output, [f"ERROR:root:Token not found"])
        self.assertEqual(token, None)

    @patch('requests.get', side_effect=mocked_requests_get)
    def test_valid_availability(self, mock_get):
        expected_results = [
            {'date': '2023-01-01', 'avail': 'ALL DAY'},
            {'date': '2023-01-08', 'avail': '08:00 AM - 3:00 PM'}
        ]
        avail = get_availability("token", "test", TEST_DATE, TEST_DATE)
        self.assertEqual(avail, expected_results)

    @patch.dict(os.environ, {"BASE_URL": "http://fail.com/api/v2/"})
    @patch('requests.get', side_effect=mocked_requests_get)
    def test_failed_availability(self, mock_get):
        with self.assertLogs(level='INFO') as cm:
            avail = get_availability("token", "test", TEST_DATE, TEST_DATE)

        self.assertEqual(cm.output, [f"ERROR:root:Key: 'availability', missing from Availability response"])
        self.assertEqual(avail, [])

    @patch.dict(os.environ, {"BASE_URL": "http://nouser.com/api/v2/"})
    @patch('requests.get', side_effect=mocked_requests_get)
    def test_invalid_user_availability(self, mock_get):
        with self.assertLogs(level='INFO') as cm:
            avail = get_availability("token", "invaliduser", TEST_DATE, TEST_DATE)
        self.assertEqual(cm.output, [f"WARNING:root:User: invaliduser has no availability"])
        self.assertEqual(avail, [])

    @patch.dict(os.environ, {"FILE_NAME": "file_not_found.csv"})
    def test_get_referee_no_file_found(self):
        with self.assertLogs(level='INFO') as cm:
            temp = get_referees()
        self.assertEqual(cm.output, ["ERROR:root:file_not_found.csv Not Found!"])
        self.assertEqual(temp, [])

 #   @patch.dict(os.environ, clear=True)
 #   def test_get_referee_no_environment_value(self):
 #       with self.assertLogs(level='INFO') as cm:
 #           temp = get_referees()
 #       self.assertEqual(cm.output, ["ERROR:root:FILE_NAME environment variable not found"])
 #       self.assertEqual(temp, [])

    @patch.dict(os.environ, {"FILE_NAME": "./tests/files/referees.csv"})
    def test_get_referees(self):
        expected_response = [
            {"referee": "Homer Simpson", "id": 1},
            {"referee": "Marge Simpson", "id": 2}
        ]
        temp = get_referees()
        self.assertEqual(temp, expected_response)

#    def test_main_no_log_level(self):
#        with self.assertLogs(level='INFO') as cm:
#            main()
#        self.assertEqual(cm.output, ["LOG_LEVEL environment variable not found"])

    def test_main_no_arguments(self):
        with pytest.raises(SystemExit) as e:
            main()
        self.assertEqual(e.typename, 'SystemExit')
        self.assertEqual(e.value.code, 77)

    @patch('assignr.availability.get_arguments')
    @patch('assignr.availability.authenticate')
    def test_main_no_token(self, mock_authenticate, mock_arguments):
        mock_arguments.return_value = [0, 
            {
            "start_date": "01/01/2023",
            "end_date": "01/10/2023"
            }
        ]
        mock_authenticate.return_value = None

        with pytest.raises(SystemExit) as e:
            main()
        self.assertEqual(e.typename, 'SystemExit')
        self.assertEqual(e.value.code, 88)
