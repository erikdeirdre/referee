from sys import (argv, exit, stdout)
from os import getenv
from os.path import exists
from getopt import (getopt, GetoptError)
from datetime import (datetime, date, time)
from posixpath import split
import csv
import pandas as pd

import logging

# Default to info
LOG_LEVEL = getenv("LOG_LEVEL") or 20

logging.basicConfig(stream=stdout,
                    level=LOG_LEVEL)

def load_fields(file_name):

    fields = {}

    try:
        with open(file_name, mode ='r')as file:
            csv_file = csv.DictReader(file)

            for line in csv_file:
                fields[line['id']] = line['description']

        return fields, 0
    except FileNotFoundError as fe:
        logging.error(f"{fe.strerror}: {fe.filename}")
        return fields, 66

def get_age_gender(field):
    age_group_gender = field.split(' ')
    if age_group_gender[-1][:1] == 'B':
        return 'M', age_group_gender[1]
    return 'F', age_group_gender[1]

def process_row(row):
    gender, age_group = get_age_gender(row[0])
    try:
        game_dt = row[2].strftime("%m/%d/%Y")
    except ValueError:
        logging.Error(f"Invalid Date for {row}")
        game_dt = f"Invalid Date format: {row[2]}"
    
    game_info = {
        'gender': gender,
        'age_group': age_group,
        'game_date': game_dt,
        'home_team': f"{row[3]}-{row[4]}",
        'away_team': f"{row[5]}-{row[6]}"
    }
             
    return game_info
    

def read_master_spreadsheet(file_name, town_team):
    se_games = []
    referee_games = []
    try:
        df = pd.read_excel(io=file_name, sheet_name='Master')
    except ValueError:
        logging.error(f"Master sheet not found in {file_name}")
        return {
            'se_games': se_games,
            'referee_games': referee_games,
            'rc': 22
        }

#    columns = df.columns.ravel()
    for row in df.values:
        if row[3].lower() == town_team:
            game_data = process_row(row)
            se_games.append(game_data)
            referee_games.append({
                'game_nbr': '',
                'game_level': '',
                'game_description': '',
                'crew_size': '',
                'crew_description': '',
                'notes': '',
                'gender': game_data['gender'],
                'age_group': game_data['age_group'],
                'date': game_data['game_date'],
                'home_team': game_data['home_team'],
                'away_team': game_data['away_team']                  
            })
        elif row[5].lower() == town_team:
            game_data = process_row(row)
            referee_games.append({
                'game_nbr': '',
                'game_level': '',
                'game_description': '',
                'crew_size': '',
                'crew_description': '',
                'notes': '',
                'gender': game_data['gender'],
                'age_group': game_data['age_group'],
                'date': game_data['game_date'],
                'home_team': game_data['home_team'],
                'away_team': game_data['away_team']                  
            })

    return {
        'se_games': se_games,
        'referee_games': referee_games,
        'rc': 0
    }

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
            sheet.title in ('7TH_8TH', '5TH_6TH', '3RD_4TH', '1ST_2ND'):
            found_schedule = False
            if '7TH' in sheet.title:
                age_group = '7/8'
            elif '5TH' in sheet.title:
                age_group = '5/6'
            elif '3RD_4TH' in sheet.title:
                age_group = '3/4'
            else:
                age_group = '1/2'
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

def get_arguments(args):
    arguments = {
        'master_file': None, 'town_file': None, 'town': None,
        'se_file': None, 'output_file': None, 'field_file': None
    }

    USAGE='USAGE: referee.py -m <master schedule file> -s <town schedule file>'
    '-t <town> -f <field conversion file> -o <output file name> -e <sport engine file>'

    try:
        opts, args = getopt(args,"hm:t:s:o:f:e:",
                            ["master-file=","town-file=","town=", "output=", "fields=",
                             "se-file="])
    except GetoptError:
        logging.error(USAGE)
        return 77, arguments

    for opt, arg in opts:
        if opt == '-h':
            logging.error(USAGE)
            return 99, arguments
        elif opt in ("-m", "--master-file"):
            arguments['master_file'] = arg
        elif opt in ("-s", "--town-file"):
            arguments['town_file'] = arg
        elif opt in ("-t", "--town"):
            arguments['town'] = arg.lower()
        elif opt in ("-o", "--output"):
            arguments['output_file'] = arg
        elif opt in ("-f", "--fields"):
            arguments['field_file'] = arg
        elif opt in ("-e", "--se-file"):
            arguments['se_file'] = arg
    if arguments['town'] is None or arguments['town_file'] is None or \
       arguments['master_file']is None or arguments['field_file'] is None or \
       arguments['output_file'] is None:
        logging.error(USAGE)
        return 99, arguments
    
    return 0, arguments

def main():

    rc, args = get_arguments(argv[1:])
    if rc:
        exit(rc)

    fields, rc = load_fields(args['field_file'])
    if rc:
        exit(rc)

    master_schedule = read_master_spreadsheet(args['master_file'],
                                              args['town'])
    if master_schedule['rc']:
        exit(master_schedule['rc'])

    town_times = pd.DataFrame(read_town_spreadsheet(args['town_file'],
                                                    args['town'], fields))

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

    town_schedule.to_excel(args['output_file'], header=header, columns=['game_nbr',
                            'date','time', 'age_group', 'game_level',
                            'gender', 'location', 'home_team', 'away_team',
                            'game_description', 'crew_size', 'crew_description',
                            'notes'], index=False)

if __name__ == "__main__":
    main()
