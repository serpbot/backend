#!/usr/bin/env python3
"""Initialize flask app"""

import os
import sys
import configparser
import argparse
from swagger_ui_bundle import swagger_ui_3_path
import logging
import logging.config
import yaml
from http import HTTPStatus
from flask_cors import CORS
from connexion.exceptions import BadRequestProblem
from src.lib.response import HttpResponse

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)) + "/..")
from src.config import connex_app, app, db, cogauth

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "logging.yaml"), "r") as f:
    log_cfg = yaml.safe_load(f.read())
    logging.config.dictConfig(log_cfg)
log = logging.getLogger(__name__)


def run(env):
    """Start flask server in dev mode"""
    conf = get_conf(env)
    connex_app = create_app(env)[1]
    log.info("Starting in %s mode", env)
    connex_app.run(host="0.0.0.0", port=5000, debug=conf["swagger"]["debug"] == "True")


def bad_request_handler(error):
    return HttpResponse().failure(HTTPStatus.BAD_REQUEST, error=error.detail)


def create_app(env):
    """Runtime configuration of flask"""
    conf = get_conf(env)
    app.config["TESTING"] = False
    app.config["SITEMAP_INCLUDE_RULES_WITHOUT_PARAMS"] = True
    app.config["SITEMAP_IGNORE_ENDPOINTS"] = ["_openapi_json", "_openapi_yaml"]
    app.config["SITEMAP_URL_SCHEME"] = "https"
    app.config["SQLALCHEMY_ECHO"] = False
    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://%s:%s@%s/%s" % \
                                            (conf["db"]["username"], conf["db"]["password"], conf["db"]["host"],
                                             conf["db"]["name"])
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQS_NAME"] = conf["sqs"]["name"]
    app.config["SQS_REGION"] = conf["sqs"]["region"]
    app.config["COGNITO_REGION"] = "us-west-2"
    app.config["COGNITO_USERPOOL_ID"] = conf["cognito"]["userpool_id"]
    app.config["COGNITO_APP_CLIENT_ID"] = conf["cognito"]["app_client_id"]
    app.config["COGNITO_APP_CLIENT_SECRET"] = conf["cognito"]["app_client_secret"]
    app.config["COGNITO_CHECK_TOKEN_EXPIRATION"] = True
    app.config["COGNITO_JWT_HEADER_NAME"] = "Authorization"
    app.config["COGNITO_JWT_HEADER_PREFIX"] = "Bearer"
    app.config["RECAPTCHA_HEADER_NAME"] = "Recaptcha"
    app.config["HCAPTCHA_SECRET"] = conf["hcaptcha"]["secret"]
    app.config["HCAPTCHA_SITE_KEY"] = conf["hcaptcha"]["site_key"]
    app.config["CONTACT_EMAIL"] = conf["contact"]["email"]
    connex_app.add_api("serpbot.yaml", options={"swagger_ui": conf["swagger"]["ui"] == "True", "swagger_path": swagger_ui_3_path})
    connex_app.add_error_handler(BadRequestProblem, bad_request_handler)
    db.init_app(app)
    cogauth.init_app(app)
    CORS(app)
    return app, connex_app


def get_conf(env):
    """Get config object from file"""
    config = configparser.ConfigParser()
    basedir = os.path.abspath(os.path.dirname(__file__))
    if env == "prod":
        config.read(basedir + "/conf/prod.ini")
    else:
        config.read(basedir + "/conf/dev.ini")
    return config


def get_env():
    """Get environment to run in"""
    parser = argparse.ArgumentParser(description="Serpbot api.")
    parser.add_argument("-e", "--env", default="dev",
                        help="select an environment to launch in (dev, prod)")
    args = parser.parse_args()
    if args.env.lower() not in ["dev", "prod"]:
        log.error("Invalid environment selected")
        sys.exit(1)
    return args.env.lower()


if __name__ == "__main__":
    run(get_env())
else:
    app = create_app("prod")[0]
