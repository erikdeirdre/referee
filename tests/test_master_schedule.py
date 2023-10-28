from os.path import join, dirname
from datetime import datetime
import unittest
from unittest.mock import patch
from schedule.helpers.master_schedule import (get_age_gender, process_row,
                                              MasterSchedule)


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
    def test_init(self):
        master_schedule = MasterSchedule('invalidid', 'A1:A1')
        self.assertEqual(master_schedule.id, 'invalidid')
        self.assertEqual(master_schedule.sheet_range, 'A1:A1')
#    def test_valid_schedule(self):
#        referee_games = [{
#            'game_id': '', 'game_type': 'Coastal', 'gender': 'Boys', 
#            'age_group': 'Grade 3/4', 'date': '04/01/2023',
#            'league': 'London', 'home_team': 'London-1',
#            'away_team': 'Kingston-4'
#            },{
#            'game_id': '', 'game_type': 'Coastal', 'gender': 'Boys', 
#            'age_group': 'Grade 3/4', 'date': '04/08/2023',
#            'league': 'London', 'home_team': 'London-1',
#            'away_team': 'Toronto-1'
#            },{
#            'game_id': '', 'game_type': 'Coastal', 'gender': 'Boys', 
#            'age_group': 'Grade 3/4', 'date': '04/22/2023',
#            'league': 'London', 'home_team': 'London-2',
#            'away_team': 'Hanover-2'
#            },{
#            'game_id': '', 'game_type': 'Coastal', 'gender': 'Boys', 
#            'age_group': 'Grade 3/4', 'date': '04/29/2023',
#            'league': 'London', 'home_team': 'London-2',
#            'away_team': 'Kingston-4'
#            },{
#            'game_id': '', 'game_type': 'Coastal', 'gender': 'Girls',
#            'age_group': 'Grade 3/4', 'date': '04/01/2023',
#            'league': 'London', 'home_team': 'London-2',
#            'away_team': 'London-3'
#            },{
#            'game_id': '', 'game_type': 'Coastal', 'gender': 'Girls',
#            'age_group': 'Grade 3/4', 'date': '04/08/2023',
#            'league': 'London', 'home_team': 'London-1',
#            'away_team': 'London-3'
#            },{
#            'game_id': '', 'game_type': 'Coastal', 'gender': 'Girls',
#            'age_group': 'Grade 3/4', 'date': '04/22/2023',
#            'league': 'London', 'home_team': 'London-1','away_team': 'Toronto-1'
#            }
#        ]
#
#        file_name = join(dirname(__file__),'files' ,'valid_file.xlsx')
#        results = read_master_spreadsheet(file_name, "london")
#
#        self.assertEqual(referee_games, results['referee_games'])
#        self.assertEqual(results['rc'], 0)
#
#    def test_missing_master_sheet(self):
#        file_name = join(dirname(__file__),'files' ,'missing_master.xlsx')
#        with self.assertLogs(level='ERROR') as cm:
#            results = read_master_spreadsheet(file_name, "test town")
#        self.assertEqual(cm.output,
#                         [f"ERROR:root:Master sheet not found in {file_name}"])
#        self.assertEqual(results['referee_games'], [])
#        self.assertEqual(results['rc'], 22)


class TestProcessRow(unittest.TestCase):
    def test_process_row(self):
        test_input = [
            'Grade 3/4 Boys', 'Test League', '1/1/99',
            'Boston', 1, 'New York', 2
        ]
        excepted_result = {
            'gender': 'Boys', 'age_group': 'Grade 3/4', 'date': '01/01/1999',
            'home_team': 'Boston-1', 'away_team': 'New York-2'
        }
        result = process_row(test_input)
        self.assertDictEqual(excepted_result, result)
