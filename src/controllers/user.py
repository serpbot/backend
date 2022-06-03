#!/usr/bin/env python3

import logging
from http import HTTPStatus
from flask import current_app
from src.lib.response import HttpResponse
from src.lib.cognito_user import CognitoUser

log = logging.getLogger(__name__)


def login(body):
    """Handle login event"""
    response = validate_input(body, CognitoUser.LOGIN_FIELDS)
    if response is not None:
        return response
    return CognitoUser.initiate_auth(body["username"], body["password"])


def signup(body):
    """Handle signup event"""
    response = validate_input(body, CognitoUser.SIGN_UP_FIELDS)
    if response is not None:
        return response
    return CognitoUser.create_cognito_user(body["username"], body["password"], body["email"])


def validate_input(body, fields):
    """Validate input from various events"""
    for field in fields:
        if not body.get(field):
            return HttpResponse().failure(status=HTTPStatus.UNPROCESSABLE_ENTITY,
                                          error="Missing field: %s" % (field))
        if body.get(field) == "":
            return HttpResponse().failure(status=HTTPStatus.UNPROCESSABLE_ENTITY,
                                          error="Field (%s) is blank" % (field))
    if current_app.config.get("TESTING"):
        return None
    # if CognitoUser.validate_recaptcha(body["recaptcha"]):
    #     return None
    return None
