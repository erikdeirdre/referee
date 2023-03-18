import unittest
from datetime import datetime
from referee import process_row

class TestGetGames(unittest.TestCase):
    def test_valid_game(self):
        test_input = [
            'Grade 3/4 Boys', 'Test League',
            datetime.strptime('2023-04-01','%Y-%m-%d'),
            'Boston', 1, 'New York', 2
        ]
        excepted_result = {
            'gender': 'M', 'age_group': '3/4', 'game_date': '04/01/2023',
            'home_team': 'Boston-1', 'away_team': 'New York-2'
        }
        result = process_row(test_input)
        self.assertEqual(excepted_result, result)
