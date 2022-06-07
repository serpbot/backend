#!/usr/bin/env python3

import logging
from http import HTTPStatus
from flask import current_app, _request_ctx_stack
from src.lib.response import HttpResponse
from src.lib.cognito_user import CognitoUser
from src.lib.flask_cognito import cognito_auth_header_required_api
from src.model.orm import Client, db

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
    if CognitoUser.validate_recaptcha(body["recaptcha"]):
         return None
    return HttpResponse().failure(status=HTTPStatus.UNPROCESSABLE_ENTITY,
                                  error="Invalid captcha provided")

@cognito_auth_header_required_api
def update_user(body):
    if "notifications" in body and isinstance(body["notifications"], bool):
        client = Client.query.get(_request_ctx_stack.top.cogauth_username)
        client.notifications = body["notifications"]
        db.session.commit()
        return HttpResponse().success(status=HTTPStatus.OK)
    else:
        return HttpResponse().failure(status=HTTPStatus.UNPROCESSABLE_ENTITY,
                                      error="Field (notifications) is invalid")