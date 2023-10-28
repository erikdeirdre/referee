from datetime import (date, time)
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class TownSchedule():
    def __init__(self, file_name, fields, town_name, age_groups) -> None:
        self.fields = fields
        self.file_name = file_name
        self.town_name = town_name
        self.age_groups = age_groups
        self.game_times = []


    def read_town_spreadsheet(self) -> None:
        df = pd.ExcelFile(self.file_name)

        for sheet in df.book.worksheets:
            if sheet.title.lower() in list(self.age_groups.keys()) and \
                sheet.sheet_state == 'visible':
                age_group = self.age_groups[sheet.title.lower()]
                self.game_times += self.get_town_games(
                    df.parse(sheet.title).values, age_group)

    def get_town_games(self, rows, age_group):
    # lookup is used to map a field to a column number. This allows
    # for the fields to be in different column in each sheet.
        lookup = {
            'field': 0,
            'time': 0,
            'dates': {}
        }
        game_times = []
        found_games = False

        for row in rows:
            if "Division" in row and "Field" in row and "Time" in row:
                found_games = True
                col_cnt = 0
                for col in row:
                    if isinstance(col, str):
                        if 'field' in col.lower():
                            lookup['field'] = col_cnt
                        if 'time' in col.lower():
                            lookup['time'] = col_cnt
                    if isinstance(col, date):
                        lookup['dates'][col.strftime("%m/%d/%Y")] = col_cnt
                    col_cnt += 1

            try:
                if found_games and isinstance(row[lookup['time']], time):
                    for col in lookup['dates'].keys():
                        if isinstance(row[lookup['dates'][col]], str) and \
                            'NO GAME' not in row[lookup['dates'][col]] and \
                            'BYE' not in row[lookup['dates'][col]]:
                            gender_team = row[lookup['dates'][col]].split()
                            if gender_team[0].strip() == "B":
                                gender = "Boys"
                            else:
                                gender = "Girls"
                            game_times.append({
                                'date': col,
                                'time': row[lookup['time']].strftime("%I:%M %p"),
                                'venue': self.fields[row[lookup['field']]]['venue'],
                                'sub_venue': self.fields[row[lookup['field']]]['sub-venue'],
                                'age_group': age_group,
                                'gender': gender,
                                'home_team': f"{self.town_name.title()}-{gender_team[2].strip()}"
                            })
            except IndexError:
                logging.error(f"IndexError reported for {row}")
            except KeyError as ke:
                logging.error(f"KeyError: {ke} for {row}. An IndexError was probably reported as well")

        return game_times
