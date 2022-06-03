#!/usr/bin/env python3
"""SQLAlchemy db model"""

from src.config import db


class Client(db.Model):
    """Client table in db"""
    __tablename__ = "clients"
    username = db.Column(db.String(255), primary_key=True)
    email = db.Column(db.String(255), nullable=False)

    websites = db.relationship("Website")

    @property
    def serialized(self):
        """Serializes client object"""
        return {
            "username": self.username,
            "email": self.email,
            "websites": self.websites
        }


class Website(db.Model):
    """Website table in db"""
    __tablename__ = "websites"
    id = db.Column(db.String(255), primary_key=True)
    domain = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(255), db.ForeignKey("clients.username"), nullable=False)

    keywords = db.relationship("Keyword")

    @property
    def serialized(self):
        """Serializes client object"""
        return {
            "id": self.id,
            "domain": self.domain,
            "keywords": self.keywords
        }


class Keyword(db.Model):
    """Website table in db"""
    __tablename__ = "keywords"
    id = db.Column(db.String(255), primary_key=True)
    websiteId = db.Column(db.String(255), db.ForeignKey("websites.id"))
    name = db.Column(db.String(255), nullable=False)

    website = db.relationship("Website", viewonly=True)

    @property
    def serialized(self):
        """Serializes client object"""
        return {
            "id": self.id,
            "name": self.name,
            "latest": self.latest,
            "best": self.best
        }


class Trend(db.Model):
    """Statistics table in db"""
    __tablename__ = "trends"
    id = db.Column(db.String(255), primary_key=True)
    keyword = db.Column(db.String(255), db.ForeignKey("keywords.id"))
    position = db.Column(db.Integer, nullable=False)
    engine = db.Column(db.String(255), nullable=False)
    date = db.Column(db.Date, nullable=False)

    @property
    def serialized(self):
        """Serializes client object"""
        return {
            "id": self.id,
            "keyword": self.keyword,
            "position": self.position,
            "engine": self.engine,
            "date": self.date
        }
