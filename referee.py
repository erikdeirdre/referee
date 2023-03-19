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

    game_info = {
        'gender': gender,
        'age_group': age_group,
        'date': row[2].strftime("%m/%d/%Y"),
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
                'date': game_data['date'],
                'home_team': game_data['home_team'],
                'away_team': game_data['away_team']                  
            })
        elif row[5].lower() == town_team:
            game_data = process_row(row)
            se_games.append(game_data)

    return {
        'se_games': se_games,
        'referee_games': referee_games,
        'rc': 0
    }

def get_town_games(rows, age_group, fields, town_name):
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
            logging.error(f"IndexError reported for {row}")
        except KeyError as ke:
            logging.error(f"KeyError: {ke} for {row}. An IndexError was probably reported as well")

    return game_times

def read_town_spreadsheet(file_name, town_name, fields):
    df = pd.ExcelFile(file_name)

    game_times = []

    for sheet in df.book.worksheets:
        if sheet.title in ('7TH_8TH', '5TH_6TH', '3RD_4TH', '1ST_2ND') and \
           sheet.sheet_state == 'visible':
            if '7TH' in sheet.title:
                age_group = '7/8'
            elif '5TH' in sheet.title:
                age_group = '5/6'
            elif '3RD' in sheet.title:
                age_group = '3/4'
            else:
                age_group = '1/2'
            game_times += get_town_games(df.parse(sheet.title).values,
                                         age_group, fields, town_name)

    return game_times

def get_arguments(args):
    arguments = {
        'master_file': None, 'town_file': None, 'town': None,
        'se_file': None, 'output_file': None, 'field_file': None
    }

    USAGE='USAGE: referee.py -m <master schedule file> -s <town schedule file>'
    '-t <town> -f <field conversion file> -e <sport engine file>'

    try:
        opts, args = getopt(args,"hm:t:s:f:e:",
                            ["master-file=","town-file=","town=","fields=",
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
        elif opt in ("-f", "--fields"):
            arguments['field_file'] = arg
        elif opt in ("-e", "--se-file"):
            arguments['se_file'] = arg
    if arguments['town'] is None or arguments['town_file'] is None or \
       arguments['master_file']is None or arguments['field_file'] is None:
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
                                              args['town'].lower())
    if master_schedule['rc']:
        exit(master_schedule['rc'])

    town_schedule = read_town_spreadsheet(args['town_file'],
                                       args['town'].lower(),
                                       fields)

    referee_header = [
        'GameNum', 'GameDate', 'GameTime', 'GameAge', 'GameLevel',
        'Gender', 'Location', 'HomeTeam', 'AwayTeam',
        'GameDescription', 'CrewSize', 'CrewDescription', 'Notes'
    ]

    se_header = [
        'start_date', 'start_time', 'end_date', 'end_time', 'title',
        'description', 'location', 'location_url', 'all_day_event',
        'event_type', 'tags', 'team1_id', 'team1_division_id',
        'team1_is_home', 'team2_id', 'team2_division_id', 'team2_name', 
        'custom_opponent', 'event_id', 'game_id', 'affects_standings',
        'points_win', 'points_loss', 'points_tie', 'points_ot_win',
        'points_ot_loss', 'division_override'
    ]

    print(se_header)
    
    panda_referee_schedule = pd.DataFrame.from_dict(master_schedule['referee_games'])
    panda_town_schedule = pd.DataFrame.from_dict(town_schedule)

    panda_referee_schedule = pd.merge(
        panda_town_schedule, panda_referee_schedule, how='inner',
        on=['age_group', 'date', 'gender', 'home_team']
    )

    panda_referee_schedule.to_excel(
        'referee_schedule.xlsx', header=referee_header, columns=['game_nbr',
        'date','time', 'age_group', 'game_level', 'gender',
        'location', 'home_team', 'away_team', 'game_description',
        'crew_size', 'crew_description', 'notes'], index=False
    )

if __name__ == "__main__":
    main()
