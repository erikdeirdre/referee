""" Graphql Address Schema Module """
from os import getenv
import requests

import logging

from graphene import (String, ObjectType, Connection)
from .helpers import TotalCount

USPS_URL = getenv('USPS_URL',
                       "https://secure.shippingapis.com/ShippingAPI.dll")
USPS_USERID = getenv('USPS_USERID')


logger = logging.getLogger(__name__)

def get_master_games(url):
    """API call to retrieve the master game schedule."""
    url = f'{USPS_URL}?API=CityStateLookup&XML=<CityStateLookupRequest USERID="{USPS_USERID}">' \

    logger.debug(url)

    results = requests.get(url)
    if results.status_code == 200:
        response = xmltodict.parse(results.text)["CityStateLookupResponse"]["ZipCode"]
        if 'Error' in response:
            logger.error(f"Error processing {url}")
            return {'error': response['Error']['Description']}
        logger.debug(f"Successfully process url, {url}.")
        return {'url': url}
    else:
        logger.error(f"Error processing url: {url}")
        return None
