#!/usr/bin/python3

import os

from flask import Flask, Response, jsonify, request, redirect
from functools import wraps
import json
import subprocess
from typing import Tuple
from slugify import slugify
from threading import Thread


app = Flask(__name__)

AUTH_SECRET = os.getenv('VENJIX_AUTH_SECRET', default="53CR3T")
SCRIPT_DIR  = os.getenv('SCRIPT_DIR', default="scripts")
SCRIPT_LIST = os.listdir(SCRIPT_DIR)


def get_script_input(args) -> str:
  return json.dumps(args.to_dict(), indent = 2)


def get_script_path(script) -> str:
  script_path = slugify(script)
  if script_path not in SCRIPT_LIST:
    return ""
  return os.path.abspath(os.path.join(SCRIPT_DIR, script_path))


def call_async(script_path, script_input) -> int:
  proc = subprocess.run(
    script_path,
    encoding='ascii',
    input=script_input,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
  )
  if proc.returncode == 0:
    print(proc.stdout)
    return 200

  print(proc.stdout + proc.stderr)
  return 500


def login(f):
  @wraps(f)
  def decorated(*args, **kwargs):
    authorization_header = request.headers.get('Authorization')
    if authorization_header and (authorization_header == AUTH_SECRET):
      return f(*args, **kwargs)
    if app.debug:
      return f(*args, **kwargs)

    resp = Response()
    return resp, 401
  return decorated

@app.route('/')
@login
def endpoints():
  return jsonify(SCRIPT_LIST)

@app.route('/<script>', methods = ['POST'])
@login
def script(script):
  script_input = request.get_json() if request.content_type == 'application/json' else get_script_input(request.args)
  script_path  = get_script_path(script)
  if script_path == "":
    return Response(response='Script not Found', status=500, mimetype="text/plain")

  # status, body = call_async(script_path, script_input)
  try:
    thread = Thread(target=call_async, args=(script_path, script_input))
    thread.daemon = True
    thread.start()
    return Response(response='Script started', status=200, mimetype="text/plain")
  except:
    import traceback
    traceback.print_exc()
    return Response(response='Starting script failed', status=500, mimetype="text/plain")


if __name__ == "__main__":
  app.run(debug=True)
