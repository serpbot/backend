#!/usr/bin/env python3

import logging
from uuid import uuid4
import validators
from http import HTTPStatus
from flask import _request_ctx_stack
from sqlalchemy import and_
from src.lib.response import HttpResponse
from src.model.orm import db, Website, Keyword
from src.lib.flask_cognito import cognito_auth_header_required_api

log = logging.getLogger(__name__)

WEBSITE_LIMIT = 5

@cognito_auth_header_required_api
def get_website(id):
    """
    Get website details handler
    """
    try:
        website = Website.query.get(id)
        if website is not None and website.username == _request_ctx_stack.top.cogauth_username:
            keywords = []
            for keyword in website.keywords:
                keywords.append(keyword.name)
            temp_website = website.to_dict()
            temp_website["keywords"] = keywords
            temp_website["numKeywords"] = len(keywords)
            return HttpResponse().success(status=HTTPStatus.OK, website=temp_website)
        else:
            return HttpResponse().failure(status=HTTPStatus.NOT_FOUND, error="Website does not exist")
    except Exception as exception:
        log.error("Unable to fetch website (%s): %s", id, exception)
        return HttpResponse().failure(status=HTTPStatus.INTERNAL_SERVER_ERROR, error="Unable to process the request")


@cognito_auth_header_required_api
def get_all_websites():
    websites = []
    try:
        for website in Website.query.filter(Website.username == _request_ctx_stack.top.cogauth_username):
            keywords = []
            for keyword in website.keywords:
                keywords.append(keyword.name)
            temp_website = website.to_dict()
            temp_website["keywords"] = keywords
            temp_website["numKeywords"] = len(keywords)
            websites.append(temp_website)
        return HttpResponse().success(status=HTTPStatus.OK, websites=websites)
    except Exception as exception:
        log.error("Unable to fetch websites: %s", exception)
        return HttpResponse().failure(status=HTTPStatus.INTERNAL_SERVER_ERROR, error="Unable to process the request")


@cognito_auth_header_required_api
def add_website(body):
    try:
        if validators.domain(body["domain"]):
            # Check if domain already exist
            domain = Website.query.filter(and_(Website.domain == body["domain"], Website.username == _request_ctx_stack.top.cogauth_username)).one_or_none()
            if domain is None:
                # Check if limit is reached
                num_websites = Website.query.filter(Website.username == _request_ctx_stack.top.cogauth_username).count()
                if num_websites >= WEBSITE_LIMIT:
                    return HttpResponse().failure(status=HTTPStatus.UNPROCESSABLE_ENTITY, error="Reached website limit (%s)" % (WEBSITE_LIMIT))

                keywords = []
                for keyword in {k for k in body["keywords"]}:
                    if keyword == "":
                        return HttpResponse().failure(status=HTTPStatus.UNPROCESSABLE_ENTITY,
                                                      error="Keyword cannot be blank")
                    keywords.append(Keyword(id=uuid4(), name=keyword))
                db.session.add(Website(id=uuid4(), domain=body["domain"], username=_request_ctx_stack.top.cogauth_username,
                                       keywords=keywords))
                db.session.commit()
                return HttpResponse().success(status=HTTPStatus.OK)
            else:
                return HttpResponse().failure(status=HTTPStatus.UNPROCESSABLE_ENTITY, error="Domain already exist")
        else:
            return HttpResponse().failure(status=HTTPStatus.UNPROCESSABLE_ENTITY, error="Invalid domain provided")
    except Exception as exception:
        log.error("Unable to add website: %s", exception)
        return HttpResponse().failure(status=HTTPStatus.INTERNAL_SERVER_ERROR, error="Unable to process the request")


@cognito_auth_header_required_api
def delete_website(id):
    try:
        website = Website.query.get(id)
        if website.username == _request_ctx_stack.top.cogauth_username:
            db.session.delete(Website.query.get(id))
            db.session.commit()
            return HttpResponse().success(status=HTTPStatus.OK)
        else:
            return HttpResponse().failure(status=HTTPStatus.FORBIDDEN,
                                          error="User does not have access to provided resource")
    except Exception as exception:
        log.error("Unable to delete website (%s): %s", id, exception)
        return HttpResponse().failure(status=HTTPStatus.INTERNAL_SERVER_ERROR, error="Unable to process the request")


@cognito_auth_header_required_api
def update_website(id, body):
    try:
        # Get list of keywords
        website = Website.query.get(id)
        if website is None:
            return HttpResponse().failure(HTTPStatus.NOT_FOUND, error="Website does not exist")
        elif website.username == _request_ctx_stack.top.cogauth_username:
            # Remove unwanted keywords
            temp_keywords = []
            for keyword in website.keywords:
                temp_keywords.append(keyword.name)
                if keyword.name not in body["keywords"]:
                    db.session.delete(keyword)

            # Add missing keywords
            for keyword in body["keywords"]:
                if keyword == "":
                    return HttpResponse().failure(status=HTTPStatus.UNPROCESSABLE_ENTITY,
                                                  error="Keyword cannot be blank")
                if keyword not in temp_keywords:
                    db.session.add(Keyword(id=uuid4(), name=keyword, websiteId=website.id))
            db.session.commit()
            return HttpResponse().success(HTTPStatus.OK)
        else:
            return HttpResponse().failure(status=HTTPStatus.FORBIDDEN,
                                          error="User does not have access to provided resource")
    except Exception as exception:
        log.error("Unable to update website (%s): %s", id, exception)
        return HttpResponse().failure(status=HTTPStatus.INTERNAL_SERVER_ERROR, error="Unable to process the request")
