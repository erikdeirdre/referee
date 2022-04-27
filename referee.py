from datetime import datetime
from email import header
from posixpath import split
import re
import csv
import pandas as pd
from pandas_ods_reader import read_ods


def load_fields(file_name):

    fields = {}

    with open(file_name, mode ='r')as file:
        csv_file = csv.DictReader(file)

        for line in csv_file:
            fields[line['id']] = line['description']

    return fields

def read_master_spreadsheet(file_name):
    sheet_index = 2
    games = []
    df = read_ods(file_name, sheet_index )
    for value in df.values:
        if 'hanover' in value[3].lower():
            gender = value[0].split()[-1]
            age_group = value[0].replace(gender, '').rstrip()
            games.append({
                'game_nbr': '',
                'game_level': '',
                'game_description': '',
                'crew_size': '',
                'crew_description': '',
                'notes': '',
                'gender': gender[:1],
                'age_group': age_group,
                'date': value[2],
                'home_team': f"{value[3].upper()}-{int(value[4])}",
                'away_team': f"{value[5].upper()}-{int(value[6])}"
            })

    return games

def read_town_spreadsheet(town_name, file_name, fields):
    game_times = []
    sheet_index = 8
    df = read_ods(file_name, sheet_index )

    col_start = 4

    for col in range(col_start, df.columns.size):
        try:
            date_check = datetime.strptime(df.columns[col],
                                            '%Y-%m-%d')
        except (ValueError, TypeError):
            print(f"{df.columns[col]} is invalid, Needs to be"
                  f" formatted as 'YYYY-MM-DD'")
            print("Please correct, and run this again")

    for row in df.values:
        for col in range(col_start, df.columns.size):
            if row[col] is not None and \
               re.fullmatch('[A-Z,a-z] - [1-9]', row[col]):
                split_field = row[col].split(' - ')
                game_times.append(
                    {
                        'date': df.columns[col],
                        'time': row[2],
                        'location': f"{fields[row[1]]}",
                        'age_group': row[0],
                        'gender': split_field[0],
                        'home_team': f"{town_name}-{split_field[1]}"
                    }
                )
    return game_times

def main():
    fields = load_fields('fields.csv')
    town_times = pd.DataFrame(read_town_spreadsheet(
        'HANOVER','/home/pwhite/Downloads/Spring_2022_homeschedule.ods',
        fields))
    master_schedule = pd.DataFrame(
        read_master_spreadsheet('/home/pwhite/Downloads/Spring2022Schedule.ods'))

    header = ['GameNum', 'GameDate', 'GameTime', 'GameAge', 'GameLevel',
                    'Gender', 'Location', 'HomeTeam', 'AwayTeam',
                    'GameDescription', 'CrewSize', 'CrewDescription', 'Notes']
    town_schedule = pd.merge(master_schedule, town_times, how='inner',
                             on=['age_group', 'date', 'gender', 'home_team'])

    town_schedule.to_excel('result.xlsx', header=header, columns=['game_nbr',
                            'date','time', 'age_group', 'game_level',
                            'gender', 'location', 'home_team', 'away_team',
                            'game_description', 'crew_size', 'crew_description',
                            'notes'], index=False)


if __name__ == "__main__":
    main()
