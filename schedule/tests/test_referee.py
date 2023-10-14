import sys
from os.path import join, dirname
from datetime import datetime
import unittest
from unittest.mock import patch
import pandas as pd
from referee import read_master_spreadsheet, get_age_gender, \
                    get_arguments, load_transaction_file, process_row, \
                    get_town_games, read_town_spreadsheet, \
                    main

USAGE='USAGE: referee.py -m <master schedule file> -s <town schedule file>' \
' -t <town> -c <conversion file> -o <output file>' 

TOWN_NAME = 'town name'

class TestGetArguments(unittest.TestCase):
    def test_help(self):
        expected_args = {
            'master_file': None, 'town_file': None, 'town': None,
            'output_file': None, 'conversion_file': None
        }
        with self.assertLogs(level='INFO') as cm:
            rc, args = get_arguments(['-h'])
        self.assertEqual(cm.output, [f"ERROR:root:{USAGE}"])
        self.assertEqual(rc, 99)
        self.assertEqual(args, expected_args)

    def test_invalid_options(self):
        expected_args = {
            'master_file': None, 'town_file': None, 'town': None,
            'output_file': None, 'conversion_file': None
        }
        with self.assertLogs(level='INFO') as cm:
            rc, args = get_arguments(['-n'])
        self.assertEqual(cm.output, [f"ERROR:root:{USAGE}"])
        self.assertEqual(rc, 77)
        self.assertEqual(args, expected_args)
        
    def test_missing_town_name(self):
        expected_args = {
            'master_file': None, 'town_file': 'town_file', 'town': None,
            'output_file': 'output', 'conversion_file': None
        }
        with self.assertLogs(level='INFO') as cm:
            rc, args = get_arguments(['-o', 'output', '-s', 'town_file'])
        self.assertEqual(cm.output, [f"ERROR:root:{USAGE}"])
        self.assertEqual(rc, 99)
        self.assertEqual(args, expected_args)

    def test_missing_town_file(self):
        expected_args = {
            'master_file': None, 'town_file': None, 'town': 'town',
            'output_file': 'output', 'conversion_file': None
        }
        with self.assertLogs(level='INFO') as cm:
            rc, args = get_arguments(['-o', 'output', '-t', 'town'])
        self.assertEqual(cm.output, [f"ERROR:root:{USAGE}"])
        self.assertEqual(rc, 99)
        self.assertEqual(args, expected_args)

    def test_missing_master_file(self):
        expected_args = {
            'master_file': None, 'town_file': None, 'town': 'town',
            'output_file': None, 'conversion_file': None
        }
        with self.assertLogs(level='INFO') as cm:
            rc, args = get_arguments(['-t', 'town'])
        self.assertEqual(cm.output, [f"ERROR:root:{USAGE}"])
        self.assertEqual(rc, 99)
        self.assertEqual(args, expected_args)

    def test_missing_field_file(self):
        expected_args = {
            'master_file': 'master', 'town_file': None, 'town': 'town',
            'output_file': None, 'conversion_file': None
        }
        with self.assertLogs(level='INFO') as cm:
            rc, args = get_arguments(['-m', 'master', '-t', 'town'])
        self.assertEqual(cm.output, [f"ERROR:root:{USAGE}"])
        self.assertEqual(rc, 99)
        self.assertEqual(args, expected_args)

    def test_invalid_no_output_file(self):
        send_args = [
            '-m', 'master_file', '-s', 'town_file', '-t', TOWN_NAME,
            '-c', 'conversion_file'
        ]
        expected_args = {
            'master_file': 'master_file', 'town_file': 'town_file',
            'town': TOWN_NAME, 'output_file': None,
            'conversion_file': 'conversion_file'
        }
        rc, args = get_arguments(send_args)
        self.assertEqual(rc, 99)
        self.assertEqual(args, expected_args)

    def test_valid_output_file(self):
        send_args = [
            '-m', 'master_file', '-s', 'town_file', '-t', TOWN_NAME,
            '-o', 'output_file', '-c', 'conversion_file'
        ]
        expected_args = {
            'master_file': 'master_file', 'town_file': 'town_file',
            'town': TOWN_NAME, 'output_file': 'output_file',
            'conversion_file': 'conversion_file'
        }
        rc, args = get_arguments(send_args)
        self.assertEqual(rc, 0)
        self.assertEqual(args, expected_args)


class TestGetAgeGender(unittest.TestCase):
# expected format "Grade 3/4 Boys"
    def test_get_male(self):
        gender, age_group = get_age_gender("Grade 3/4 Boys")
        self.assertEqual(gender, 'Boys')
        self.assertEqual(age_group, 'Grade 3/4')

    def test_get_female(self):
        gender, age_group = get_age_gender("Grade 3/4 Girls")
        self.assertEqual(gender, 'Girls')
        self.assertEqual(age_group, 'Grade 3/4')


class TestReadMasterSchedule(unittest.TestCase):
    def test_valid_schedule(self):
        referee_games = [{
            'game_id': '', 'game_type': 'Coastal', 'gender': 'Boys', 
            'age_group': 'Grade 3/4', 'date': '04/01/2023',
            'league': 'London', 'home_team': 'London-1',
            'away_team': 'Kingston-4'
            },{
            'game_id': '', 'game_type': 'Coastal', 'gender': 'Boys', 
            'age_group': 'Grade 3/4', 'date': '04/08/2023',
            'league': 'London', 'home_team': 'London-1',
            'away_team': 'Toronto-1'
            },{
            'game_id': '', 'game_type': 'Coastal', 'gender': 'Boys', 
            'age_group': 'Grade 3/4', 'date': '04/22/2023',
            'league': 'London', 'home_team': 'London-2',
            'away_team': 'Hanover-2'
            },{
            'game_id': '', 'game_type': 'Coastal', 'gender': 'Boys', 
            'age_group': 'Grade 3/4', 'date': '04/29/2023',
            'league': 'London', 'home_team': 'London-2',
            'away_team': 'Kingston-4'
            },{
            'game_id': '', 'game_type': 'Coastal', 'gender': 'Girls',
            'age_group': 'Grade 3/4', 'date': '04/01/2023',
            'league': 'London', 'home_team': 'London-2',
            'away_team': 'London-3'
            },{
            'game_id': '', 'game_type': 'Coastal', 'gender': 'Girls',
            'age_group': 'Grade 3/4', 'date': '04/08/2023',
            'league': 'London', 'home_team': 'London-1',
            'away_team': 'London-3'
            },{
            'game_id': '', 'game_type': 'Coastal', 'gender': 'Girls',
            'age_group': 'Grade 3/4', 'date': '04/22/2023',
            'league': 'London', 'home_team': 'London-1','away_team': 'Toronto-1'
            }
        ]

        file_name = join(dirname(__file__),'files' ,'valid_file.xlsx')
        results = read_master_spreadsheet(file_name, "london")

        self.assertEqual(referee_games, results['referee_games'])
        self.assertEqual(results['rc'], 0)

    def test_missing_master_sheet(self):
        file_name = join(dirname(__file__),'files' ,'missing_master.xlsx')
        with self.assertLogs(level='ERROR') as cm:
            results = read_master_spreadsheet(file_name, "test town")
        self.assertEqual(cm.output,
                         [f"ERROR:root:Master sheet not found in {file_name}"])
        self.assertEqual(results['se_games'], [])
        self.assertEqual(results['referee_games'], [])
        self.assertEqual(results['rc'], 22)

    def test_invalid_town(self):
        file_name = join(dirname(__file__),'files' ,'valid_file.xlsx')
        results = read_master_spreadsheet(file_name, "test town")
        self.assertEqual(results['se_games'], [])
        self.assertEqual(results['referee_games'], [])
        self.assertEqual(results['rc'], 0)



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

        actual_json, rc = load_transaction_file(join(dirname(__file__),'files' ,'translations.json'))
        self.assertEqual(rc, 0)
        self.assertEqual(actual_json, expected_json)

    def test_invalid_file(self):
        with self.assertLogs(level='INFO') as cm:
            fields, rc = load_transaction_file('file_does_not_exist.json')
        self.assertEqual(
            cm.output, ["ERROR:root:No such file or directory: file_does_not_exist.json"]
        )
        self.assertEqual(rc, 66)
        self.assertEqual(fields, {})


class TestProcessRow(unittest.TestCase):
    def test_process_row(self):
        test_input = [
            'Grade 3/4 Boys', 'Test League',
            datetime.strptime('2023-04-01','%Y-%m-%d'),
            'Boston', 1, 'New York', 2
        ]
        excepted_result = {
            'gender': 'Boys', 'age_group': 'Grade 3/4', 'date': '04/01/2023',
            'home_team': 'Boston-1', 'away_team': 'New York-2'
        }
        result = process_row(test_input)
        self.assertDictEqual(excepted_result, result)

class TestGetTownGames(unittest.TestCase):
    def test_get_town_games(self):
        fields = {
            'Field1': {
                "venue": "Fenway Parking",
                "sub-venue": "Pool 1"
            }
        }
        AM8 = "08:00 AM"
        AM10 = "10:00 AM"
        POOL = 'Pool 1'
        FENWAY = 'Fenway Parking'
        expected_results = [
            {
                'date': '04/01/2023', 'time': AM8, 'venue': FENWAY,
                'sub_venue': POOL, 'age_group': '7TH_8TH',
                'gender': 'Girls', 'home_team': 'Boston-2'
            }, {
                'date': '04/08/2023', 'time': AM8, 'venue': FENWAY,
                'sub_venue': POOL, 'age_group': '7TH_8TH',
                'gender': 'Boys', 'home_team': 'Boston-1'
            }, {
                'date': '04/22/2023', 'time': AM8, 'venue': FENWAY,
                'sub_venue': POOL, 'age_group': '7TH_8TH',
                'gender': 'Boys', 'home_team': 'Boston-3'
            }, {
                'date': '04/29/2023', 'time': AM8, 'venue': FENWAY,
                'sub_venue': POOL, 'age_group': '7TH_8TH',
                'gender': 'Girls', 'home_team': 'Boston-2'
            }, {
                'date': '05/06/2023', 'time': AM8, 'venue': FENWAY,
                'sub_venue': POOL, 'age_group': '7TH_8TH',
                'gender': 'Girls', 'home_team': 'Boston-3'
            }, {
                'date': '05/13/2023', 'time': AM8, 'venue': FENWAY,
                'sub_venue': POOL, 'age_group': '7TH_8TH',
                'gender': 'Girls', 'home_team': 'Boston-1'
            }, {
                'date': '05/20/2023', 'time': AM8, 'venue': FENWAY,
                'sub_venue': POOL, 'age_group': '7TH_8TH',
                'gender': 'Girls', 'home_team': 'Boston-2'
            }, {
                'date': '05/27/2023', 'time': AM8, 'venue': FENWAY,
                'sub_venue': POOL, 'age_group': '7TH_8TH',
                'gender': 'Girls', 'home_team': 'Boston-1'
            }, {
                'date': '04/01/2023', 'time': AM10, 'venue': FENWAY,
                'sub_venue': POOL, 'age_group': '7TH_8TH',
                'gender': 'Boys', 'home_team': 'Boston-1'
            }, {
                'date': '04/08/2023', 'time': AM10, 'venue': FENWAY,
                'sub_venue': POOL, 'age_group': '7TH_8TH',
                'gender': 'Girls', 'home_team': 'Boston-1'
            }, {
                'date': '04/22/2023', 'time': AM10, 'venue': FENWAY,
                'sub_venue': POOL, 'age_group': '7TH_8TH',
                'gender': 'Girls', 'home_team': 'Boston-2'
            }, {
                'date': '04/29/2023', 'time': AM10, 'venue': FENWAY,
                'sub_venue': POOL, 'age_group': '7TH_8TH',
                'gender': 'Boys', 'home_team': 'Boston-3'
            }, {
                'date': '05/06/2023', 'time': AM10, 'venue': FENWAY,
                'sub_venue': POOL, 'age_group': '7TH_8TH',
                'gender': 'Girls', 'home_team': 'Boston-3'
            }, {
                'date': '05/13/2023', 'time': AM10, 'venue': FENWAY,
                'sub_venue': POOL, 'age_group': '7TH_8TH',
                'gender': 'Boys', 'home_team': 'Boston-1'
            }, {
                'date': '05/20/2023', 'time': AM10, 'venue': FENWAY,
                'sub_venue': POOL, 'age_group': '7TH_8TH',
                'gender': 'Girls', 'home_team': 'Boston-3'
            }, {
                'date': '05/27/2023', 'time': AM10, 'venue': FENWAY,
                'sub_venue': POOL, 'age_group': '7TH_8TH',
                'gender': 'Boys', 'home_team': 'Boston-1'
            }, {
                'date': '06/03/2023', 'time': AM10, 'venue': FENWAY,
                'sub_venue': POOL, 'age_group': '7TH_8TH',
                'gender': 'Girls', 'home_team': 'Boston-1'
            }
        ]

        df = pd.read_excel(io=join(dirname(__file__), 'files' ,'town_file.xlsx'),
                           sheet_name='7TH_8TH')
        results = get_town_games(df.values, '7TH_8TH', fields, 'boston')
        self.assertEqual(results, expected_results)

class TestReadTownSpreadsheet(unittest.TestCase):
    def test_read_town_spreadsheet(self):
        POOL = 'Pool 1'
        AM8 = "08:00 AM"
        AM10 = "10:00 AM"
        FENWAY = 'Fenway Parking'
        AGE_GROUP = 'Grade 7/8'
        age_groups = {
            "3rd_4th": "Grade 3/4",
            "5th_6th": "Grade 5/6",
            "7th_8th": "Grade 7/8"     
        }
        fields = {
            'Field1': {
                "venue": "Fenway Parking",
                "sub-venue": "Pool 1"
            }
        }

        expected_results = [
            {
                'date': '04/01/2023', 'time': AM8, 'venue': FENWAY,
                'sub_venue': POOL, 'age_group': AGE_GROUP,
                'gender': 'Girls', 'home_team': 'Boston-2'
            }, {
                'date': '04/08/2023', 'time': AM8, 'venue': FENWAY,
                'sub_venue': POOL, 'age_group': AGE_GROUP,
                'gender': 'Boys', 'home_team': 'Boston-1'
            }, {
                'date': '04/22/2023', 'time': AM8, 'venue': FENWAY,
                'sub_venue': POOL, 'age_group': AGE_GROUP,
                'gender': 'Boys', 'home_team': 'Boston-3'
            }, {
                'date': '04/29/2023', 'time': AM8, 'venue': FENWAY,
                'sub_venue': POOL, 'age_group': AGE_GROUP,
                'gender': 'Girls', 'home_team': 'Boston-2'
            }, {
                'date': '05/06/2023', 'time': AM8, 'venue': FENWAY,
                'sub_venue': POOL, 'age_group': AGE_GROUP,
                'gender': 'Girls', 'home_team': 'Boston-3'
            }, {
                'date': '05/13/2023', 'time': AM8, 'venue': FENWAY,
                'sub_venue': POOL, 'age_group': AGE_GROUP,
                'gender': 'Girls', 'home_team': 'Boston-1'
            }, {
                'date': '05/20/2023', 'time': AM8, 'venue': FENWAY,
                'sub_venue': POOL, 'age_group': AGE_GROUP,
                'gender': 'Girls', 'home_team': 'Boston-2'
            }, {
                'date': '05/27/2023', 'time': AM8, 'venue': FENWAY,
                'sub_venue': POOL, 'age_group': AGE_GROUP,
                'gender': 'Girls', 'home_team': 'Boston-1'
            }, {
                'date': '04/01/2023', 'time': AM10, 'venue': FENWAY,
                'sub_venue': POOL, 'age_group': AGE_GROUP,
                'gender': 'Boys', 'home_team': 'Boston-1'
            }, {
                'date': '04/08/2023', 'time': AM10, 'venue': FENWAY,
                'sub_venue': POOL, 'age_group': AGE_GROUP,
                'gender': 'Girls', 'home_team': 'Boston-1'
            }, {
                'date': '04/22/2023', 'time': AM10, 'venue': FENWAY,
                'sub_venue': POOL, 'age_group': AGE_GROUP,
                'gender': 'Girls', 'home_team': 'Boston-2'
            }, {
                'date': '04/29/2023', 'time': AM10, 'venue': FENWAY,
                'sub_venue': POOL, 'age_group': AGE_GROUP,
                'gender': 'Boys', 'home_team': 'Boston-3'
            }, {
                'date': '05/06/2023', 'time': AM10, 'venue': FENWAY,
                'sub_venue': POOL, 'age_group': AGE_GROUP,
                'gender': 'Girls', 'home_team': 'Boston-3'
            }, {
                'date': '05/13/2023', 'time': AM10, 'venue': FENWAY,
                'sub_venue': POOL, 'age_group': AGE_GROUP,
                'gender': 'Boys', 'home_team': 'Boston-1'
            }, {
                'date': '05/20/2023', 'time': AM10, 'venue': FENWAY,
                'sub_venue': POOL, 'age_group': AGE_GROUP,
                'gender': 'Girls', 'home_team': 'Boston-3'
            }, {
                'date': '05/27/2023', 'time': AM10, 'venue': FENWAY,
                'sub_venue': POOL, 'age_group': AGE_GROUP,
                'gender': 'Boys', 'home_team': 'Boston-1'
            }, {
                'date': '06/03/2023', 'time': AM10, 'venue': FENWAY,
                'sub_venue': POOL, 'age_group': AGE_GROUP,
                'gender': 'Girls', 'home_team': 'Boston-1'
            }
        ]


        results = read_town_spreadsheet(
            join(dirname(__file__), 'files' ,'town_file.xlsx'),
            'boston', fields, age_groups
        )
        self.assertEqual(results, expected_results)


class TestMain(unittest.TestCase):
    def test_main_invalid_args(self):
        testargs = ["prog", "-t", "Boston"]
        with patch('sys.argv', testargs):
            with self.assertRaises(SystemExit) as cm:
                main()       
        self.assertEqual(cm.exception.code, 77)

    def test_main_invalid_load_fields(self):
        testargs = ["prog", "-m", "master_file", "-s", "town_file",
                    "-f", "field_file", "-t", "Boston"]
        with patch('sys.argv', testargs):
            with self.assertRaises(SystemExit) as cm:
                main()    
# Arguments aren't being passed in so it returns the same code
# as failed arguments
        self.assertEqual(cm.exception.code, 77)
