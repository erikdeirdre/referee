"""Utilities used by other classes"""
from getopt import (getopt, GetoptError)
from os.path import exists
from os import environ
import json
import logging

logger = logging.getLogger(__name__)

def load_translation_file(file_name):
    translation_contents = {}
    try:
        with open(file_name, mode ='r') as file:
            translation_contents = json.load(file)
        return translation_contents, 0

    except FileNotFoundError as fe:
        logging.error(f"{fe.strerror}: {fe.filename}")
        return translation_contents, 66

def get_environment():
    error = 0
    environment = {}

    try:
        environment['spreadsheet_id'] = environ['MASTER_SCHEDULE_ID']
    except KeyError:
        logging.error('MASTER_SCHEDULE_ID environment variable is missing')
        error = 66

    try:
        environment['range_name'] = environ['RANGE_NAME']
    except KeyError:
        logging.error('RANGE_NAME environment variable is missing')
        error = 66

    try:
        environment['translation_file'] = environ['TRANSLATION_FILE']
    except KeyError:
        logging.warning('TRANSLATION_FILE environment variable is missing, using default')
        environment['translation_file'] = 'files/translations.json'

    try:
        environment['output_file_prefix'] = environ['OUTPUT_FILE_PREFIX']
    except KeyError:
        logging.warning('OUTPUT_FILE_PREFIX environment variable is missing, using default')
        environment['output_file_prefix'] = 'schedule'

    try:
        environment['credentials'] = environ['GOOGLE_APPLICATION_CREDENTIALS']
    except KeyError:
        logging.error('GOOGLE_APPLICATION_CREDENTIALS environment variable is missing')
        error = 66
  
    return error, environment

def get_arguments(args):
    arguments = {
        'town_file': None, 'town': None
    }

    USAGE='USAGE: schedule.py -s <town schedule file> -t <town>'

    try:
        opts, args = getopt(args,"hs:t:",
                            ["town-file=","town="])
    except GetoptError:
        logging.error(USAGE)
        return 77, arguments

    for opt, arg in opts:
        if opt == '-h':
            logging.error(USAGE)
            return 99, arguments
        elif opt in ("-s", "--town-file"):
            arguments['town_file'] = arg
        elif opt in ("-t", "--town"):
            arguments['town'] = arg.lower()
    if arguments['town'] is None or arguments['town_file'] is None:
        logging.error(USAGE)
        return 99, arguments
    
    return 0, arguments
