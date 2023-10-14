import requests
import logging
import pandas as pd
from dotenv import load_dotenv
from sys import (exit, stdout)
from os import environ

load_dotenv()

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
    except KeyError:
        logging.error('Token not found')
        token = None

    return token

def get_requests(token, end_point, params=None):
    headers = {
        'accept': 'application/json',
        'authorization': f'Bearer {token}'
    }

    response = requests.get(f"{environ['BASE_URL']}{end_point}", headers=headers, params=params)
    return response.json()

def get_availability(token, user_id, start_dt, end_dt):
    availability = []
    params = {
        'user_id': user_id,
        'search[start_date]': start_dt,
        'search[end_date]': end_dt
    }

    response = get_requests(token, f'users/{user_id}/availability', params=params)
    if 'message' in response:
        logging.debug(f'User: {user_id} has no availability')
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
        logging.error(ke)

    return availability

def get_referees():
    referees = []
    try:
        df = pd.read_csv(environ['FILE_NAME'])
    except ValueError:
        logging.error(f"Master sheet not found in {environ['FILE_NAME']}")
        return referees
    except KeyError:
        logging.error("FILE_NAME environment variable not found")
        return referees
    except FileNotFoundError as fe:
        logging.error(f"{fe.strerror}: {fe.filename}")
        return referees

    for row in df.values:
        referees.append({
            'referee': f"{row[0]} {row[1]}",
            'id': row[2]
        })

    return referees

try:
    LOG_LEVEL = environ['LOG_LEVEL']
except KeyError:
    logging.error('LOG_LEVEL environment variable not found')
    exit(99)

logging.basicConfig(stream=stdout,
                    level=int(LOG_LEVEL))

token = authenticate()
if token is None:
    exit(88)

referee_availability = []
for referee in get_referees():
    response = get_availability(token, referee['id'], '10/14/2023', '10/30/2023')
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
