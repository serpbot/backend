#!/usr/bin/env python3
"""Create all tables in db"""

import os
import logging
from config import app
from model.orm import db, Client

log = logging.getLogger(__name__)


def run():
    """Runtime configuration of flask"""
    app.config['SQLALCHEMY_ECHO'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://%s:%s@%s/%s" % \
                                            (os.environ.get("DATABASE_USERNAME"),
                                             os.environ.get("DATABASE_PASSWORD"),
                                             os.environ.get("DATABASE_HOST"),
                                             os.environ.get("DATABASE_NAME"))
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    with app.app_context():
        db.create_all()
        db.session.add(Client(username="nicolas", email="temp@onintime.com"))
        db.session.commit()


if __name__ == "__main__":
    run()
