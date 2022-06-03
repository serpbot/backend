#!/usr/bin/env python3
"""Configure flask app"""

import os
import sys
import secrets
import connexion
from flask_sqlalchemy import SQLAlchemy

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)) + "/..")
from src.lib.flask_cognito import CognitoAuth

connex_app  = connexion.App(__name__, specification_dir="./swagger/")
app = connex_app.app

cogauth = CognitoAuth()
db = SQLAlchemy()
