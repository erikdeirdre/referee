from os import environ
from sys import (argv, exit, stdout)
from dotenv import load_dotenv
from datetime import datetime
import pandas as pd
import logging
from helpers.utils import (get_arguments, get_environment,
                           load_translation_file)
from helpers.master_schedule import MasterSchedule
from helpers.town_schedule import TownSchedule

load_dotenv()

logging.basicConfig(stream=stdout,
                    level=int(environ['LOG_LEVEL']))

def main():
    logging.info("Starting Schedule Conversion")
    rc, args = get_arguments(argv[1:])
    if rc:
        exit(rc)

    logging.debug(f"Running scheduler with file, {args['town_file']} for town: {args['town'].title()}")
    rc, environment = get_environment()
    if rc:
        exit(rc)

    translations, rc = load_translation_file(environment['translation_file'])
    if rc:
        return rc

    try:
        fields = translations['fields'][args['town'].lower()]
    except KeyError:
        logging.error(f"No field translations found for {args['town']}")
        return 55

    try:
        age_groups = translations['age_groups']
    except KeyError:
        logging.error(f"No Team mappings found for {args['town']}")
        return 55

    master_schedule = MasterSchedule(environment['spreadsheet_id'],
                                     environment['range_name'])
    master_schedule.load_sheet()
    master_schedule.process_master_schedule(args['town'].lower())

    town_schedule = TownSchedule(args['town_file'], fields,
                                 args['town'].lower(), age_groups)

    town_schedule.read_town_spreadsheet()

    assignor_header = [
        'Game ID', 'Date', 'Start Time', 'Venue', 'Sub-Venue',
        'Age Group', 'League', 'Gender', 'Game Type',
        'Home Team', 'Away Team'
    ]
   
    panda_referee_schedule = pd.DataFrame.from_dict(master_schedule.referee_games)
    panda_town_schedule = pd.DataFrame.from_dict(town_schedule.game_times)

    panda_referee_schedule = pd.merge(
        panda_town_schedule, panda_referee_schedule, how='inner',
        on=['age_group', 'date', 'gender', 'home_team'],
        validate="1:1"
    )

    str_date = datetime.now().strftime('%Y%m%d%H%M')
    panda_referee_schedule.to_csv(args['output_file'],
        header=assignor_header, columns=['game_id',
        'date', 'time', 'venue', 'sub_venue', 'age_group', 'league',
        'gender', 'game_type', 'home_team', 'away_team'], index=False
    )
    logging.info(f"Completed Schedule Conversion for {args['town'].title()}")
    return 0

if __name__ == "__main__":
    exit(main())
