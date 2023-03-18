from os.path import join, dirname
import unittest
from referee import read_master_spreadsheet

class TestReadMasterSchedule(unittest.TestCase):
    def test_valid_schedule(self):
        referee_games = [{
            'game_nbr': '', 'game_level': '', 'game_description': '',
            'crew_size': '', 'crew_description': '', 'notes': '',
            'gender': 'M', 'age_group': '3/4', 'date': '04/01/2023',
            'home_team': 'London-1', 'away_team': 'Kingston-4'
            },{
            'game_nbr': '', 'game_level': '', 'game_description': '',
            'crew_size': '', 'crew_description': '', 'notes': '',
            'gender': 'M', 'age_group': '3/4', 'date': '04/08/2023',
            'home_team': 'London-1', 'away_team': 'Toronto-1'
            },{
            'game_nbr': '', 'game_level': '', 'game_description': '',
            'crew_size': '', 'crew_description': '', 'notes': '',
            'gender': 'M', 'age_group': '3/4', 'date': '04/22/2023',
            'home_team': 'London-2', 'away_team': 'Hanover-2'
            },{
            'game_nbr': '', 'game_level': '', 'game_description': '',
            'crew_size': '', 'crew_description': '', 'notes': '',
            'gender': 'M', 'age_group': '3/4', 'date': '04/29/2023',
            'home_team': 'London-2', 'away_team': 'Kingston-4'
            },{
            'game_nbr': '', 'game_level': '', 'game_description': '',
            'crew_size': '', 'crew_description': '', 'notes': '',
            'gender': 'F', 'age_group': '3/4', 'date': '04/01/2023',
            'home_team': 'London-2', 'away_team': 'London-3'
            },{
            'game_nbr': '', 'game_level': '', 'game_description': '',
            'gender': 'F', 'age_group': '3/4', 'date': '04/08/2023',
            'crew_size': '', 'crew_description': '', 'notes': '',
            'home_team': 'London-1', 'away_team': 'London-3'
            },{
            'game_nbr': '', 'game_level': '', 'game_description': '',
            'crew_size': '', 'crew_description': '', 'notes': '',
            'gender': 'F', 'age_group': '3/4', 'date': '04/22/2023',
            'home_team': 'London-1', 'away_team': 'Toronto-1'
            }
        ]
        
        se_games = [
            {'gender': 'M', 'age_group': '3/4', 'date': '04/01/2023',
            'home_team': 'Hull-1', 'away_team': 'London-2'},
            {'gender': 'M', 'age_group': '3/4', 'date': '04/01/2023',
            'home_team': 'London-1', 'away_team': 'Kingston-4'},
            {'gender': 'M', 'age_group': '3/4', 'date': '04/08/2023',
            'home_team': 'London-1', 'away_team': 'Toronto-1'},
            {'gender': 'M', 'age_group': '3/4', 'date': '04/08/2023',
            'home_team': 'Frankfurt-2', 'away_team': 'London-2'},
            {'gender': 'M', 'age_group': '3/4', 'date': '04/22/2023',
            'home_team': 'Hanover-1', 'away_team': 'London-1'},
            {'gender': 'M', 'age_group': '3/4', 'date': '04/22/2023',
            'home_team': 'London-2', 'away_team': 'Hanover-2'},
            {'gender': 'M', 'age_group': '3/4', 'date': '04/29/2023',
            'home_team': 'Hull-1', 'away_team': 'London-1'},
            {'gender': 'M', 'age_group': '3/4', 'date': '04/29/2023',
            'home_team': 'London-2', 'away_team': 'Kingston-4'},
            {'gender': 'F', 'age_group': '3/4', 'date': '04/01/2023',
            'home_team': 'London-2', 'away_team': 'London-3'},
            {'gender': 'F', 'age_group': '3/4', 'date': '04/01/2023',
            'home_team': 'Hanover-3', 'away_team': 'London-1'},
            {'gender': 'F', 'age_group': '3/4', 'date': '04/08/2023',
            'home_team': 'London-1', 'away_team': 'London-3'},
            {'gender': 'F', 'age_group': '3/4', 'date': '04/08/2023',
            'home_team': 'Hanover-1', 'away_team': 'London-2'},
            {'gender': 'F', 'age_group': '3/4', 'date': '04/22/2023',
            'home_team': 'Hanover-2', 'away_team': 'London-3'},
            {'gender': 'F', 'age_group': '3/4', 'date': '04/22/2023',
            'home_team': 'Kingston-2', 'away_team': 'London-2'},
            {'gender': 'F', 'age_group': '3/4', 'date': '04/22/2023',
            'home_team': 'London-1', 'away_team': 'Toronto-1'}
        ]

        file_name = join(dirname(__file__),'files' ,'valid_file.xlsx')
        results = read_master_spreadsheet(file_name, "london")

        self.assertEqual(referee_games, results['referee_games'])
        self.assertEqual(se_games, results['se_games'])
        self.assertEqual(results['rc'], 0)

    def test_missing_master_sheet(self):
        expected_results = {
            'se_games': [],
            'referee_games': [],
            'rc': 22
        }
        file_name = join(dirname(__file__),'files' ,'missing_master.xlsx')
        with self.assertLogs(level='ERROR') as cm:
            results = read_master_spreadsheet(file_name, "test town")
        self.assertEqual(cm.output,
                         [f"ERROR:root:Master sheet not found in {file_name}"])
        self.assertEqual(results, expected_results)

    def test_invalid_town(self):
        expected_results = {}
        file_name = join(dirname(__file__),'files' ,'valid_file.xlsx')
        results = read_master_spreadsheet(file_name, "test town")

        self.assertEqual(expected_results, {})