#!/usr/bin/env python3
"""Create all tables in db"""

import os
import sys
import logging
import argparse
import configparser
from config import app
from model.orm import db, Client

log = logging.getLogger(__name__)


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
    parser = argparse.ArgumentParser(description="Wayback Download website and api.")
    parser.add_argument("-e", "--env", default="dev",
                        help="select an environment to launch in (dev, prod)")
    args = parser.parse_args()
    if args.env.lower() not in ["dev", "prod"]:
        log.error("Invalid environment selected")
        sys.exit(1)
    return args.env.lower()


def run(env):
    """Runtime configuration of flask"""
    conf = get_conf(env)
    app.config['SQLALCHEMY_ECHO'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://%s:%s@%s/%s" % \
                                            (conf["db"]["username"], conf["db"]["password"], conf["db"]["host"],
                                             conf["db"]["name"])
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    with app.app_context():
        db.create_all()
        db.session.add(Client(username="nicolas", email="temp@onintime.com"))
        db.session.commit()


if __name__ == "__main__":
    run(get_env())
