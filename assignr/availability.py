from sys import (argv, exit, stdout)
import requests
import logging
import pandas as pd
from dotenv import load_dotenv
from getopt import (getopt, GetoptError)
from datetime import (date, datetime)
from sys import (exit, stdout)
from os import environ, getcwd

load_dotenv()

def get_arguments(args):
    arguments = {
        'start_date': None, 'end_date': None
    }

    rc = 0
    USAGE='USAGE: availability.py -s <start-date> -e <end-date>' \
    ' FORMAT=MM/DD/YYYY'

    try:
        opts, args = getopt(args,"hs:e:",
                            ["start-date=","end-date="])
    except GetoptError:
        logging.error(USAGE)
        return 77, arguments

    for opt, arg in opts:
        if opt == '-h':
            logging.error(USAGE)
            return 99, arguments
        elif opt in ("-s", "--start-date"):
            arguments['start_date'] = arg
        elif opt in ("-e", "--end-date"):
            arguments['end_date'] = arg

    if arguments['start_date'] is None or arguments['end_date'] is None:
        logging.error(USAGE)
        return 99, arguments

    try:
        datetime.strptime(arguments['start_date'], "%m/%d/%Y").date()
    except ValueError:
        logging.error(f"Start Date value, {arguments['start_date']} is invalid")
        rc = 88
    try:
        datetime.strptime(arguments['end_date'], "%m/%d/%Y").date()
    except ValueError:
        logging.error(f"End Date value, {arguments['end_date']} is invalid")
        rc = 88

    return rc, arguments

def authenticate():
    form_data = {
        'client_secret': environ['CLIENT_SECRET'],
        'client_id': environ['CLIENT_ID'],
        'scope': environ['CLIENT_SCOPE'],
        'grant_type': 'client_credentials'
    }

    authenticate = requests.post(environ['AUTH_URL'], data=form_data)

    try:
        token = authenticate.json()['access_token']
    except (KeyError, TypeError):
        logging.error('Token not found')
        token = None

    return token

def get_requests(token, end_point, params=None):
    headers = {
        'accept': 'application/json',
        'authorization': f'Bearer {token}'
    }

    response = requests.get(f"{environ['BASE_URL']}{end_point}", headers=headers, params=params)
    return response.status_code, response.json()

def get_availability(token, user_id, start_dt, end_dt):
    availability = []
    params = {
        'user_id': user_id,
        'search[start_date]': start_dt,
        'search[end_date]': end_dt
    }

    status_code, response = get_requests(token, f'users/{user_id}/availability', params=params)

#    if status_code != 200:
#        logging.error(f'Failed return code: {status_code} for user: {user_id}')
#        return availability

    if status_code == 404:
        logging.warning(f'User: {user_id} has no availability')
        return availability
    
    try:
        availabilities = response['_embedded']['availability']
        for avail in availabilities:
            if avail['all_day']:
                availability.append({
                    'date': avail['date'],
                    'avail': 'ALL DAY'                 
                })
            else:
                availability.append({
                    'date': avail['date'],
                    'avail': f"{avail['start_time']} - {avail['end_time']}"                 
                })

    except KeyError as ke:
        logging.error(f"Key: {ke}, missing from Availability response")

    return availability

def get_referees():
    referees = []

    try:
        df = pd.read_csv(environ['FILE_NAME'])
    except KeyError:
        logging.error("FILE_NAME environment variable not found")
        return referees
    except FileNotFoundError:
        logging.error(f"{environ['FILE_NAME']} Not Found!")
        return referees

    for row in df.to_numpy():
        referees.append({
            'referee': f"{row[0]} {row[1]}",
            'id': row[2]
        })

    return referees

def main():
    try:
        LOG_LEVEL = environ['LOG_LEVEL']
    except KeyError:
        logging.error('LOG_LEVEL environment variable not found')
        exit(99)

    logging.basicConfig(stream=stdout,
                        level=int(LOG_LEVEL))

    rc, args = get_arguments(argv[1:])
    if rc:
        exit(rc)

    token = authenticate()
    if token is None:
        exit(88)

    referee_availability = []
    for referee in get_referees():
        response = get_availability(token, referee['id'], args['start_date'],
                                    args['end_date'])
        if response:
            for resp in response:
                print(f"{referee['referee']} - {resp['date']} - {resp['avail']}")
        else:
            print(f"{referee['referee']} isn't Available")

        referee_availability.append({
            'referee': referee['referee'],
            'availability': response
        })

    print(referee_availability)

if __name__ == "__main__":
    main()
