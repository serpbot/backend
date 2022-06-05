#!/usr/bin/env python3
"""Initialize flask app"""

import os
import sys
from swagger_ui_bundle import swagger_ui_3_path
import logging
from http import HTTPStatus
from flask_cors import CORS
from connexion.exceptions import BadRequestProblem

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)) + "/..")
from src.lib.response import HttpResponse
from src.config import connex_app, app, db, cogauth

log = logging.getLogger(__name__)


def run():
    """Start flask server in dev mode"""
    connex_app = create_app()[1]
    log.info("Starting server")
    connex_app.run(host="0.0.0.0", port=5000, debug=os.environ.get("SWAGGER_DEBUG"))


def bad_request_handler(error):
    return HttpResponse().failure(HTTPStatus.BAD_REQUEST, error=error.detail)


def create_app():
    """Runtime configuration of flask"""
    app.config["TESTING"] = False
    app.config["SITEMAP_INCLUDE_RULES_WITHOUT_PARAMS"] = True
    app.config["SITEMAP_IGNORE_ENDPOINTS"] = ["_openapi_json", "_openapi_yaml"]
    app.config["SITEMAP_URL_SCHEME"] = "https"
    app.config["SQLALCHEMY_ECHO"] = False
    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://%s:%s@%s/%s" % \
                                            (os.environ.get("DATABASE_USERNAME"),
                                             os.environ.get("DATABASE_PASSWORD"),
                                             os.environ.get("DATABASE_HOST"),
                                             os.environ.get("DATABASE_NAME"))
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQS_NAME"] = os.environ.get("SQS_NAME")
    app.config["SQS_REGION"] = os.environ.get("SQS_REGION")
    app.config["COGNITO_REGION"] = os.environ.get("COGNITO_REGION")
    app.config["COGNITO_USERPOOL_ID"] = os.environ.get("COGNITO_USERPOOL_ID")
    app.config["COGNITO_APP_CLIENT_ID"] = os.environ.get("COGNITO_APP_CLIENT_ID")
    app.config["COGNITO_APP_CLIENT_SECRET"] = os.environ.get("COGNITO_APP_CLIENT_SECRET")
    app.config["COGNITO_CHECK_TOKEN_EXPIRATION"] = True
    app.config["COGNITO_JWT_HEADER_NAME"] = "Authorization"
    app.config["COGNITO_JWT_HEADER_PREFIX"] = "Bearer"
    app.config["RECAPTCHA_HEADER_NAME"] = "Recaptcha"
    app.config["HCAPTCHA_SECRET"] = os.environ.get("HCAPTCHA_SECRET")
    app.config["HCAPTCHA_SITE_KEY"] = os.environ.get("HCAPTCHA_SITE_KEY")
    app.config["CONTACT_EMAIL"] = os.environ.get("CONTACT_EMAIL")
    connex_app.add_api("serpbot.yaml", options={"swagger_ui": os.environ.get("SWAGGER_UI") == "True", "swagger_path": swagger_ui_3_path})
    connex_app.add_error_handler(BadRequestProblem, bad_request_handler)
    db.init_app(app)
    cogauth.init_app(app)
    CORS(app)
    return app, connex_app


if __name__ == "__main__":
    run()
else:
    app = create_app()[0]
