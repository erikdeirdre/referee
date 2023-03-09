from sys import (argv, exit)
from os.path import exists
from getopt import (getopt, GetoptError)
from datetime import (datetime, date, time)
from posixpath import split
import csv
import pandas as pd


def load_fields(file_name):

    fields = {}

    with open(file_name, mode ='r')as file:
        csv_file = csv.DictReader(file)

        for line in csv_file:
            fields[line['id']] = line['description']

    return fields

def get_games(rows, home_team):
    games = []
    found_games = False

    for row in rows.values:
        if isinstance(row[2], str):
            if found_games and home_team in row[2].lower():
                games.append({
                    'game_date': row[1],
                    'home_team': f"{row[2].title()}-{int(row[3])}",
                    'away_team': f"{row[4].title()}-{int(row[5])}"
                })
            elif 'home team' in row[2].lower() and \
                'away team' in row[4].lower():
                found_games = True

    return games

def read_master_spreadsheet(file_name, home_team):
    games = []
    df = pd.ExcelFile(file_name)
    for sheet in df.book.worksheets:
        if sheet.sheet_state == 'visible':
            rows = df.parse(sheet.title)
            if not rows.empty:
                game_result = get_games(rows, home_team)
                if len(rows) and "team template" in rows.columns[0].lower() and \
                    "bracket" in rows.values[0][0].lower() and \
                    "age group" in rows.values[0][2].lower() and \
                    len(game_result) > 0:
                    age_group_gender = rows.values[0][4].split(' ')
                    if age_group_gender[-1][:1] == 'B':
                        gender = 'M'
                    else:
                        gender = 'F'
                    for game in game_result:
                        games.append({
                            'game_nbr': '',
                            'game_level': '',
                            'game_description': '',
                            'crew_size': '',
                            'crew_description': '',
                            'notes': '',
                            'gender': gender,
                            'age_group': age_group_gender[1],
                            'date': game['game_date'].strftime("%m/%d/%Y"),
                            'home_team': game['home_team'],
                            'away_team': game['away_team']               
                        })

    return games

def read_town_spreadsheet(file_name, town_name, fields):
    df = pd.ExcelFile(file_name)
    lookup = {
        'field': 0,
        'time': 0,
        'dates': {}
    }
    game_times = []

    for sheet in df.book.worksheets:
        if sheet.sheet_state == 'visible' and \
            sheet.title in ('7TH_8TH', '5TH_6TH'):
            found_schedule = False
            if '7TH' in sheet.title:
                age_group = '7/8'
            if '5TH' in sheet.title:
                age_group = '5/6' 
            for row in df.parse(sheet.title).values:
                if "Division" in row and "Field" in row and "Time" in row:
                    found_schedule = True
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
                    if found_schedule and isinstance(row[lookup['time']], time):
                        for col in lookup['dates'].keys():
                            if isinstance(row[lookup['dates'][col]], str) and \
                                'NO GAMES' not in row[lookup['dates'][col]]:
                                gender_team = row[lookup['dates'][col]].split('-')
                                if gender_team[0].strip() == "B":
                                    gender = "M"
                                else:
                                    gender = "F"
                                game_times.append({
                                    'date': col,
                                    'time': row[lookup['time']].strftime("%I:%M %p"),
                                    'location': fields[row[lookup['field']]],
                                    'age_group': age_group,
                                    'gender': gender,
                                    'home_team': f"{town_name.title()}-{gender_team[1].strip()}"
                                })
                except IndexError:
                    print(row)

    return game_times

def main():
    master_file = None
    town_file = None
    town = None
    USAGE='referee.py -m <master schedule file> -s <town schedule file>'
    '-t <town> -f <field conversion file> -o <output file name>'

    try:
        opts, args = getopt(argv[1:],"hm:t:s:o:f:",
                            ["master-file=","town-file=","town=", "output=", "fields="])
    except GetoptError:
        print(USAGE)
        exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print(USAGE)
            exit(3)
        elif opt in ("-m", "--master-file"):
            master_file = arg
        elif opt in ("-s", "--town-file"):
            town_file = arg
        elif opt in ("-t", "--town"):
            town = arg.lower()
        elif opt in ("-o", "--output"):
            output_file = arg
        elif opt in ("-f", "--fields"):
            field_file = arg
    if town is None or town_file is None or master_file is None or \
        field_file is None or output_file is None:
        print(USAGE)
        exit(3)

    master_schedule = pd.DataFrame(read_master_spreadsheet(master_file, town))

    fields = load_fields(field_file)

    town_times = pd.DataFrame(read_town_spreadsheet(town_file, town, fields))

    header = [
        'GameNum', 'GameDate', 'GameTime', 'GameAge', 'GameLevel',
        'Gender', 'Location', 'HomeTeam', 'AwayTeam',
        'GameDescription', 'CrewSize', 'CrewDescription', 'Notes'
    ]

    master_schedule['age_group'] = master_schedule['age_group'].astype(str)
    master_schedule['home_team'] = master_schedule['home_team'].astype(str)
    master_schedule['gender'] = master_schedule['gender'].astype(str)
#    master_schedule['date'] = master_schedule['date'].astype('datetime64[ns]')

    town_times['age_group'] = town_times['age_group'].astype(str)
    town_times['home_team'] = town_times['home_team'].astype(str)
    town_times['gender'] = town_times['gender'].astype(str)
#    town_times['date'] = town_times['date'].astype('datetime64[ns]')   

    town_schedule = pd.merge(master_schedule, town_times, how='inner',
                             on=['age_group', 'date', 'gender', 'home_team'])

    town_schedule.to_excel(output_file, header=header, columns=['game_nbr',
                            'date','time', 'age_group', 'game_level',
                            'gender', 'location', 'home_team', 'away_team',
                            'game_description', 'crew_size', 'crew_description',
                            'notes'], index=False)

if __name__ == "__main__":
    main()
