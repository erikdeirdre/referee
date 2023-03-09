""" Main Module """
from sys import (exit, stdout)
from os import getenv
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from helpers.utils import HttpError

import logging

APP = Flask(__name__)
APP.config.from_pyfile('settings.py')

logging.basicConfig(stream=stdout,
                    level=APP.config['LOG_LEVEL'])

logging.info('Starting ...')

CORS(APP, resources={r"/*": {"origins": "*", "send_wildcard": "False"}})


@APP.errorhandler(HttpError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response

@APP.route('/api/health')
def health():
    return 'healthy'

@APP.route('/api/contact', methods=['POST'])
def contact():
    try:
        response = email_client.send_email(request.get_json(), "contact.html", True)
        resp = jsonify(response['message'])
        resp.status_code = response['code']
        return resp
    except Exception as e:
        resp = jsonify({"message": "Error processing Contact Form"})
        resp.status_code = 500
        logging.error(e)

@APP.route('/api/profile', methods=['POST'])
@require_auth(None)
def update_profile():
    try:
        profile = management_api.update_profile(json.loads(request.data))
        resp = jsonify(profile['message'])
        resp.status_code = profile['code']
    except Exception as e:
        resp = jsonify({ "message": f"{e}"})
        resp.status_code = 406

    return resp
