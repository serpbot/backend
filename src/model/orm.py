#!/usr/bin/env python3
"""SQLAlchemy db model"""

from sqlalchemy_serializer import SerializerMixin
from src.config import db


class Client(db.Model, SerializerMixin):
    """Client table in db"""
    __tablename__ = "clients"
    username = db.Column(db.String(255), primary_key=True)
    email = db.Column(db.String(255), nullable=False)

    websites = db.relationship("Website")


class Website(db.Model, SerializerMixin):
    """Website table in db"""
    __tablename__ = "websites"
    id = db.Column(db.String(255), primary_key=True)
    domain = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(255), db.ForeignKey("clients.username"), nullable=False)

    keywords = db.relationship("Keyword")


class Keyword(db.Model, SerializerMixin):
    """Website table in db"""
    __tablename__ = "keywords"
    id = db.Column(db.String(255), primary_key=True)
    websiteId = db.Column(db.String(255), db.ForeignKey("websites.id"))
    name = db.Column(db.String(255), nullable=False)


class Trend(db.Model, SerializerMixin):
    """Statistics table in db"""
    __tablename__ = "trends"
    id = db.Column(db.String(255), primary_key=True)
    keyword = db.Column(db.String(255), db.ForeignKey("keywords.id"))
    position = db.Column(db.Integer, nullable=False)
    engine = db.Column(db.String(255), nullable=False)
    date = db.Column(db.Date, nullable=False)
