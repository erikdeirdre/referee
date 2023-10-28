import unittest
from os.path import (join, dirname)
from schedule.helpers.town_schedule import TownSchedule


class TestTownSchedule(unittest.TestCase):
    def test_get_town_games(self):
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

        town_schedule = TownSchedule(
            join(dirname(__file__), 'files' ,'town_file.xlsx'),
            fields, 'boston', age_groups)
        town_schedule.read_town_spreadsheet()
        self.assertEqual(town_schedule.game_times, expected_results)
