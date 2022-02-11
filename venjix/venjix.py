#!/usr/bin/python3

import os

from flask import Flask, Response, Blueprint, jsonify, request

from flask import current_app
from functools import wraps
import subprocess
import logging
import requests
from dotenv import load_dotenv
from typing import Tuple
from slugify import slugify
from threading import Thread

bp = Blueprint("venjix", __name__)
load_dotenv()

AUTH_SECRET = os.getenv("VENJIX_AUTH_SECRET", default="53CR3T")
SCRIPT_DIR = os.getenv("SCRIPT_DIR", default="scripts")
SCRIPT_LIST = os.listdir(SCRIPT_DIR)


def bootstrap():
    for s in SCRIPT_LIST:
        if s != slugify(s):
            logging.error("ERROR: {0} is not a valid script name, remove all special characters".format(s))


def create_response(response_txt: str, script_name: str, status: int):
    response_json = {"script_name": script_name, "response": response_txt}
    response = jsonify(response_json)
    response.status_code = status
    return response


def parse_request_data(request_data) -> Tuple[str, str]:
    script_input = request_data.get("args", "")
    callback = request_data.get("callback", "")
    return script_input, callback


def get_script_path(script) -> str:
    script_path = slugify(script)
    if script_path not in SCRIPT_LIST:
        return ""
    return os.path.abspath(os.path.join(SCRIPT_DIR, script_path))


def call_back(callback_uri: str, payload) -> int:
    try:
        r = requests.post(callback_uri, json=payload)
        logging.info("callback : {0}".format(r.status_code))
        return r.status_code
    except Exception:
        logging.exception("callback: '{}' failed".format(callback_uri))
        return 500


def call_async(script_path, request_data) -> int:
    script_input, callback_uri = parse_request_data(request_data)
    logging.debug("CALL: {0}".format(script_path))
    proc = subprocess.run(script_path, encoding="ascii", input=script_input, capture_output=True)
    if proc.stdout:
        logging.info(proc.stdout)
    if proc.stderr:
        logging.warning(proc.stderr)
    if callback_uri != "":
        callback_payload = {"returncode": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr}
        call_back(callback_uri=callback_uri, payload=callback_payload)
    return


def login(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        authorization_header = request.headers.get("Authorization", "")
        authorization_bearer = authorization_header.split("Bearer ")
        if len(authorization_bearer) > 1 and authorization_bearer[1] == AUTH_SECRET:
            return f(*args, **kwargs)
        if current_app.debug:
            logging.warn("Login disabled in Debug mode")
            return f(*args, **kwargs)
        resp = Response()
        return resp, 401

    return decorated


@bp.route("/")
@login
def endpoints():
    return jsonify(SCRIPT_LIST)


@bp.route("/<script>", methods=["POST"])
@login
def script(script):
    request_data = request.get_json() if request.content_type == "application/json" else request.args.to_dict()
    script_path = get_script_path(script)
    if script_path == "":
        return create_response(response_txt="script not Found", status=404, script_name=script)

    try:
        thread = Thread(target=call_async, args=(script_path, request_data))
        thread.start()
        return create_response(response_txt="script started", status=200, script_name=script)
    except Exception:
        logging.exception("starting script: '{}' failed".format(script))
        return create_response(response_txt="starting script failed", status=500, script_name=script)


if __name__ == "__main__":
    bootstrap()
    app = Flask(__name__)
    app.register_blueprint(bp)
    app.run(debug=True)
