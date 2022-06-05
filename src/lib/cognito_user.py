#!/usr/bin/env python3
"""Boto3 user handler"""

import logging.config
import hashlib
import hmac
import base64
from http import HTTPStatus
import requests
import boto3
from flask import current_app
from src.config import db
from src.model.orm import Client
from .response import HttpResponse

log = logging.getLogger(__name__)


class CognitoUser:
    """Boto3 user handler class"""
    LOGIN_FIELDS = ["username", "password", "recaptcha"]
    SIGN_UP_FIELDS = ["username", "email", "password", "recaptcha"]

    @staticmethod
    def get_secret_hash(username):
        """Get cognito secret hash for user"""
        msg = username + current_app.config.get("COGNITO_APP_CLIENT_ID")
        dig = hmac.new(str(current_app.config.get("COGNITO_APP_CLIENT_SECRET")).encode("utf-8"),
                       msg=str(msg).encode("utf-8"), digestmod=hashlib.sha256).digest()
        secret = base64.b64encode(dig).decode()
        return secret

    @staticmethod
    def initiate_auth(username, password):
        """Login user using cognito"""
        try:
            client = boto3.client("cognito-idp",
                                  region_name=current_app.config.get("COGNITO_REGION"))
            resp = client.admin_initiate_auth(
                UserPoolId=current_app.config.get("COGNITO_USERPOOL_ID"),
                ClientId=current_app.config.get("COGNITO_APP_CLIENT_ID"),
                AuthFlow="ADMIN_NO_SRP_AUTH",
                AuthParameters={
                    "USERNAME": username,
                    "SECRET_HASH": CognitoUser.get_secret_hash(username),
                    "PASSWORD": password,
                },
                ClientMetadata={
                    "username": username,
                    "password": password,
                })
            return HttpResponse().success(HTTPStatus.OK, token=resp["AuthenticationResult"]["IdToken"])
        except client.exceptions.NotAuthorizedException:
            log.warning("The username or password is incorrect for: %s", username)
            return HttpResponse().failure(status=HTTPStatus.UNPROCESSABLE_ENTITY,
                                          error="The username or password is incorrect")
        except client.exceptions.UserNotConfirmedException:
            log.warning("User (%s) is not confirmed", username)
            return HttpResponse().failure(status=HTTPStatus.UNPROCESSABLE_ENTITY,
                                          error="User is not confirmed")
        except Exception as exception:
            log.error(exception)
            return HttpResponse().failure(status=HTTPStatus.BAD_REQUEST,
                                          error=str(exception).replace("\n", " "))

    @staticmethod
    def create_cognito_user(username, password, email):
        """Create cognito and db user"""
        client = boto3.client("cognito-idp", region_name=current_app.config.get("COGNITO_REGION"))
        try:
            client.sign_up(
                ClientId=current_app.config.get("COGNITO_APP_CLIENT_ID"),
                SecretHash=CognitoUser.get_secret_hash(username),
                Username=username,
                Password=password,
                UserAttributes=[
                    {
                        "Name": "email",
                        "Value": email
                    }
                ],
                ValidationData=[
                    {
                        "Name": "email",
                        "Value": email
                    },
                    {
                        "Name": "custom:username",
                        "Value": username
                    }
                ])
            CognitoUser.create_db_user(username, email)
        except client.exceptions.UsernameExistsException:
            log.warning("The username (%s) already exists", username)
            return HttpResponse().failure(status=HTTPStatus.UNPROCESSABLE_ENTITY,
                                          error="The username already exists")
        except client.exceptions.InvalidPasswordException:
            log.warning(
                "Password should be at least 8 characters in length, and contain uppercase lettters, lowercase letters, numbers and special characters")
            return HttpResponse().failure(status=HTTPStatus.UNPROCESSABLE_ENTITY,
                                          error="Password should be at least 8 characters in length, and contain uppercase lettters, lowercase letters, numbers and special characters")
        except client.exceptions.UserLambdaValidationException:
            log.warning("Email (%s) already exists", email)
            return HttpResponse().failure(status=HTTPStatus.UNPROCESSABLE_ENTITY,
                                          error="Email already exists")
        except Exception as exception:
            log.error(exception)
            return HttpResponse().failure(status=HTTPStatus.BAD_REQUEST,
                                          error=str(exception).replace("\n", " "))
        log.info("Successfully created user (%s)", username)
        return HttpResponse().success(status=HTTPStatus.CREATED,
                                      info="Please confirm your signup, check your email for the validation URL")

    @staticmethod
    def delete_cognito_user(username, access_token):
        """Delete cognito and db user"""
        client = boto3.client("cognito-idp", region_name=current_app.config.get("COGNITO_REGION"))
        try:
            client.delete_user(
                AccessToken=access_token)
            CognitoUser.delete_db_user(username)
        except client.exceptions.ResourceNotFoundException:
            log.warning("The user (%s) does not exist", username)
            return HttpResponse().failure(status=HTTPStatus.UNPROCESSABLE_ENTITY,
                                          error="The user does not exist")
        except Exception as exception:
            log.error(exception)
            return HttpResponse().failure(status=HTTPStatus.BAD_REQUEST,
                                          error=str(exception).replace("\n", " "))
        log.info("Successfully deleted user (%s)", username)
        return HttpResponse().success(status=HTTPStatus.OK,
                                      info="Successfully deleted cognito user")

    @staticmethod
    def confirm_signup(username):
        """Confirm cognito user"""
        client = boto3.client("cognito-idp", region_name=current_app.config.get("COGNITO_REGION"))
        try:
            client.admin_confirm_sign_up(
                UserPoolId=current_app.config.get("COGNITO_USERPOOL_ID"),
                Username=username)
        except client.exceptions.ResourceNotFoundException:
            log.warning("The user (%s) does not exist", username)
            return HttpResponse().failure(status=HTTPStatus.UNPROCESSABLE_ENTITY,
                                          error="The user does not exist")
        except Exception as exception:
            log.error(exception)
            return HttpResponse().failure(status=HTTPStatus.BAD_REQUEST,
                                          error=str(exception).replace("\n", " "))
        log.info("Successfully confirmed user (%s)", username)
        return HttpResponse().success(status=HTTPStatus.OK,
                                      info="Successfully confirmed cognito user")

    @staticmethod
    def create_db_user(username, email):
        """Create user in db"""
        log.info("Creating db user (%s)", username)
        try:
            db.session.add(Client(username=username, email=email))
            db.session.commit()
        except Exception as exception:
            log.error("Unable to create db user (%s): %s", username, exception)

    @staticmethod
    def delete_db_user(username):
        """Delete user in db"""
        log.info("Deleting db user (%s)", username)
        try:
            client = Client.query.get(username)
            db.session.delete(client)
            db.session.commit()
        except Exception as exception:
            log.error("Unable to delete db user (%s): %s", username, exception)

    @staticmethod
    def validate_recaptcha(token):
        """Validate hcaptcha"""
        url = "https://hcaptcha.com/siteverify"
        params = {"secret": current_app.config.get("HCAPTCHA_SECRET"),
                  "response": token, "sitekey": current_app.config.get("HCAPTCHA_SITE_KEY")}
        try:
            response = requests.post(url, data=params).json()
            return response["success"]
        except Exception as exception:
            log.warning("Unable to validate hcaptcha with token (%s): %s", token, exception)
            return False
