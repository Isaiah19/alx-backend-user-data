#!/usr/bin/env python3
"""
Route module for the API
"""
from os import getenv
from api.v1.views import app_views
from flask import Flask, jsonify, abort, request
from flask_cors import (CORS, cross_origin)
import os


app = Flask(__name__)
app.register_blueprint(app_views)
CORS(app, resources={r"/api/v1/*": {"origins": "*"}})
auth = os.getenv('AUTH_TYPE')


def get_auth():
    """ all auth classes getter """
    from api.v1.auth.auth import Auth
    from api.v1.auth.basic_auth import BasicAuth
    from api.v1.auth.session_auth import SessionAuth
    from api.v1.auth.session_exp_auth import SessionExpAuth
    from api.v1.auth.session_db_auth import SessionDBAuth

    auth_repo = {
        'auth': Auth,
        'basic_auth': BasicAuth,
        'session_auth': SessionAuth,
        'session_exp_auth': SessionExpAuth,
        'session_db_auth': SessionDBAuth
    }

    return auth_repo


if auth:
    try:
        auth = get_auth()[auth]()
    except Exception:
        auth = None


@app.before_request
def filter():
    """ checks if auth is enabled """
    if auth is None:
        return
    path = request.path
    excluded_paths = [
        '/api/v1/status/',
        '/api/v1/unauthorized/',
        '/api/v1/forbidden/',
        '/api/v1/auth_session/login/'
    ]
    if auth.require_auth(path, excluded_paths) is False:
        return

    if auth.authorization_header(request) is None \
            and auth.session_cookie(request) is None:
        abort(401)

    curr_user = auth.current_user(request)
    if curr_user is None:
        abort(403)

    request.current_user = curr_user


@app.errorhandler(404)
def not_found(error) -> str:
    """ Not found handler
    """
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(401)
def not_authorized(error) -> str:
    """ Not authorized handler
    """
    return jsonify({"error": "Unauthorized"}), 401


@app.errorhandler(403)
def forbidden(error) -> str:
    """ forbidden action handler
    """
    return jsonify({"error": "Forbidden"}), 403


if __name__ == "__main__":
    host = getenv("API_HOST", "0.0.0.0")
    port = getenv("API_PORT", "5000")
    app.run(host=host, port=port, debug=True)
