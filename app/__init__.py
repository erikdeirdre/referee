""" Main Module """
from os import environ
from sys import (exit, stdout)
from flask import Flask
from flask_cors import CORS
from flask_graphql import GraphQLView
import logging

APP = Flask(__name__)
CORS(APP)
APP.config.from_pyfile('settings.py')

logging.basicConfig(stream=stdout,
                    level=APP.config['LOG_LEVEL'])

logging.info('Starting ...')

from .schema import SCHEMA

@APP.route('/')
def health():
    return 'healthy'


APP.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view(
        'graphql',
        schema=SCHEMA,
        graphiql=APP.config['GRAPHIQL'],
    )
)
