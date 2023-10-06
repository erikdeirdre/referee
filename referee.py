from sys import (argv, exit, stdout)
from os import getenv
from os.path import exists
from getopt import (getopt, GetoptError)
from datetime import (datetime, date, time)
from posixpath import split
import json
import pandas as pd

import logging

# Default to info
LOG_LEVEL = getenv("LOG_LEVEL") or 20

logging.basicConfig(stream=stdout,
                    level=LOG_LEVEL)

def load_translations(file_name):

    translations = {}

    try:
        with open(file_name, mode ='r')as file:
            translations = json.load(file)
        return translations, 0
    except FileNotFoundError as fe:
        logging.error(f"{fe.strerror}: {fe.filename}")
        return translations, 66

def get_age_gender(field):
    age_group_gender = field.split(' ')
    if age_group_gender[-1][:1] == 'B':
        return 'M', age_group_gender[1]
    return 'F', age_group_gender[1]

def process_row(row):
    gender, age_group = get_age_gender(row[0])
    try:        
        game_date = row[2].strftime("%m/%d/%Y")
    except AttributeError as ae:
        logging.error("Invalid date value ... make sure all dates are formatted as 'Date'")
        return None

    game_info = {
        'gender': gender,
        'age_group': age_group,
        'date': game_date,
        'home_team': f"{row[3]}-{row[4]}",
        'away_team': f"{row[5]}-{row[6]}"
    }
             
    return game_info
    

def read_master_spreadsheet(file_name, town_team):
    coaches_games = []
    referee_games = []
    try:
        df = pd.read_excel(io=file_name, sheet_name='Master')
    except ValueError:
        logging.error(f"Master sheet not found in {file_name}")
        return {
            'se_games': coaches_games,
            'referee_games': referee_games,
            'rc': 22
        }

    for row in df.values:
        if row[3].lower() == town_team:
            game_data = process_row(row)
            coaches_games.append(game_data)
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
            coaches_games.append(game_data)

    return {
        'coaches_games': coaches_games,
        'referee_games': referee_games,
        'rc': 0
    }

def get_gender_division(field_key, mapping):
    try:
        gender = mapping[field_key]['gender']
        division = mapping[field_key]['division']
        return gender, division
    except KeyError as ke:
        logging.error(f"Coach KeyError: {field_key}")
        return None, None

def get_town_games(rows, age_group, translations, town_name):
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
                        field_name = str(row[lookup['field']]).lower()
                        location = translations['fields'][town_name][field_name]
                        gender, team_nbr = get_gender_division(
                            row[lookup['dates'][col]].lower(),
                            translations['team_mappings'][town_name][age_group]
                        )
                        if gender:
                            game_times.append({
                                'date': col,
                                'time': row[lookup['time']].strftime("%I:%M %p"),
                                'location': location,
                                'age_group': age_group,
                                'gender': gender,
                                'home_team': f"{town_name.title()} {team_nbr}"
                            })
        except IndexError:
            logging.error(f"IndexError reported for {row}")
        except KeyError as ke:
            logging.error(f"KeyError: {ke} for {row}. An IndexError was probably reported as well")

    return game_times

def read_town_spreadsheet(file_name, town_name, translations):
    df = pd.ExcelFile(file_name)

    game_times = []

    for sheet in df.book.worksheets:
        if sheet.title in ('7TH_8TH', '5TH_6TH', '3RD_4TH') and \
           sheet.sheet_state == 'visible':
            if '7TH' in sheet.title:
                age_group = '7/8'
            elif '5TH' in sheet.title:
                age_group = '5/6'
            else:
                age_group = '3/4'
            game_times += get_town_games(df.parse(sheet.title).values,
                                         age_group,
                                         translations, town_name)

    return game_times

def get_arguments(args):
    arguments = {
        'master_file': None, 'town_file': None, 'town': None,
        'se_file': None, 'output_file': None, 'field_file': None
    }

    USAGE='USAGE: referee.py -m <master schedule file> -s <town schedule file>'
    '-t <town> -f <field conversion file> -e <sport engine file>'

    try:
        opts, args = getopt(args,"hm:t:s:x:e:",
                            ["master-file=","town-file=","town=","translations=",
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
        elif opt in ("-x", "--translations"):
            arguments['translation_file'] = arg
        elif opt in ("-e", "--se-file"):
            arguments['se_file'] = arg
    if arguments['town'] is None or arguments['town_file'] is None or \
       arguments['master_file']is None or arguments['translation_file'] is None:
        logging.error(USAGE)
        return 99, arguments
    
    return 0, arguments

def main():

    rc, args = get_arguments(argv[1:])
    if rc:
        exit(rc)

    translations, rc = load_translations(args['translation_file'])
    if rc:
        exit(rc)

    master_schedule = read_master_spreadsheet(args['master_file'],
                                              args['town'].lower())
    if master_schedule['rc']:
        exit(master_schedule['rc'])

    town_schedule = read_town_spreadsheet(
        args['town_file'],
        args['town'].lower(),
        translations
    )

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
