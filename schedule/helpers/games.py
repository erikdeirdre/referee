from os import getenv
import requests

import logging

logger = logging.getLogger(__name__)

def get_master_games(url):
    """API call to retrieve the master game schedule."""

    logger.debug(url)
