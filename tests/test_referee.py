from os.path import join, dirname
from datetime import datetime
import unittest
from referee import read_master_spreadsheet, get_age_gender, \
                    get_arguments, load_fields, process_row

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


class TestGetAgeGender(unittest.TestCase):
# expected format "Grade 3/4 Boys"
    def test_get_male(self):
        gender, age_group = get_age_gender("Grade 3/4 Boys")
        self.assertEqual(gender, 'M')
        self.assertEqual(age_group, '3/4')

    def test_get_female(self):
        gender, age_group = get_age_gender("Grade 3/4 Girls")
        self.assertEqual(gender, 'F')
        self.assertEqual(age_group, '3/4')



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



class TestLoadFields(unittest.TestCase):
    def test_valid_file(self):
        expected_fields = {
            'Field1': 'Field One @ High School', 'Field2': 'Field Two @ HS'
        }
        fields, rc = load_fields(join(dirname(__file__),'files' ,'test_fields.csv'))
        self.assertEqual(rc, 0)
        self.assertEqual(fields, expected_fields)

    def test_invalid_file(self):
        with self.assertLogs(level='INFO') as cm:
            fields, rc = load_fields('file_does_not_exist.csv')
        self.assertEqual(
            cm.output, ["ERROR:root:No such file or directory: file_does_not_exist.csv"]
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
            'gender': 'M', 'age_group': '3/4', 'date': '04/01/2023',
            'home_team': 'Boston-1', 'away_team': 'New York-2'
        }
        result = process_row(test_input)
        self.assertDictEqual(excepted_result, result)
