""" Main Module """
from sys import (exit, stdout)
from os import getenv, path
import json
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from flask_cors import CORS
from helpers.utils import HttpError

import logging

APP = Flask(__name__)
APP.config.from_pyfile('settings.py')

logging.basicConfig(stream=stdout,
                    level=APP.config['LOG_LEVEL'])

logging.info('Starting ...')

CORS(APP, resources={r"/*": {"origins": "*", "send_wildcard": "False"}})

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in APP.config['ALLOWED_EXTENSIONS']

def check_file(request, ke, upload_dir):
    try:
        temp_file = request.files[ke]
        if temp_file.filename == '':
            msg = f"{ke} schedule file missing"
            resp = jsonify({"message": msg})
            resp.status_code = 500
            logging.error(msg)
            return None, resp
    except KeyError:
        msg = f"Missing {ke} file"
        resp = jsonify({"message": msg})
        resp.status_code = 500
        logging.error(msg)
        return None, resp

    if allowed_file(temp_file.filename):
        filename = secure_filename(temp_file.filename)
        temp_name = path.join(upload_dir, filename)
        try:
            temp_file.save(temp_name)
        except Exception as e:
            msg = f"{e.strerror}, {temp_name}"
            resp = jsonify({"message": msg})
            resp.status_code = 500
            logging.error(msg)
            return None, resp
    else:
        msg = f"Invalid File extension for {temp_file.filename}. Accepted type is 'xlsx'."
        resp = jsonify({"message": msg})
        resp.status_code = 500
        logging.error(msg)
        return None, resp  

    return temp_file, None
        
@APP.errorhandler(HttpError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response

@APP.route('/health')
def health():
    return 'healthy'

@APP.route('/', methods=['GET'])
def main_page():
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data action="http://localhost:5000/upload">
      <input type=file name=main>
      <input type=file name=team>
      <input type=submit value=Upload>
    </form>
    '''

@APP.route('/upload', methods=['POST'])
def upload_main_file():
    if request.method == 'POST':
        main_file, resp = check_file(request, 'main', APP.config['UPLOAD_FOLDER'])
        if main_file is None:
            return resp
        
        team_file, resp = check_file(request, 'team', APP.config['UPLOAD_FOLDER'])
        if team_file is None:
            return resp
        
        if main_file.filename == team_file.filename:
            msg = "Main schedule and Team schedule are the same name."
            resp = jsonify({"message": msg})
            resp.status_code = 500
            logging.error(msg)
            return resp

        print('process file')          
