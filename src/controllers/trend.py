import json
from http import HTTPStatus
from flask import _request_ctx_stack
from sqlalchemy import and_

from src.lib.flask_cognito import cognito_auth_header_required_api, log
from src.lib.response import HttpResponse
from src.model.orm import Website,  Trend

@cognito_auth_header_required_api
def get_trend_for_website(website_id, engine):
    try:

        website = Website.query.get(website_id)
        if website is None or website.username != _request_ctx_stack.top.cogauth_username:
            return HttpResponse().failure(status=HTTPStatus.NOT_FOUND, error="Website does not exist")
        if engine != "google" and engine != "bing":
            return HttpResponse().failure(status=HTTPStatus.NOT_FOUND, error="Engine does not exist")
        
        tempTrends = {}
        result = {"keywords": [], "labels": []}
        if website is not None:
            for keyword in website.keywords:
                if keyword.name not in tempTrends:
                    tempTrends[keyword.name] = []
                for trend in Trend.query.filter_by(keyword=keyword.id).filter_by(engine=engine).order_by(Trend.date).all():
                    if trend.date not in result["labels"]:
                        result["labels"].append(trend.date)
                    tempTrends[keyword.name].append({str(trend.date): trend.position})

            result["labels"].sort()

            # Initialize the result object with the keywords fetched for this domain
            for keyword in tempTrends:
                result["keywords"].append({"label": keyword, "data": []})

            # Iterate through all dates found for all keywords for this domain
            for date in result["labels"]:
                # Iterate through the keywords to check if their rank has been fetched on this specific date
                for keyword in tempTrends:
                    rank = 0
                    for tempTrend in tempTrends[keyword]:
                        # Keyword has rank associated to it on this specific day
                        if str(date) in tempTrend:
                            # Keep track of the rank
                            rank = tempTrend[str(date)]
                            break
                    for idx, data in enumerate(result["keywords"]):
                        # Write the rank to the correct keyword in the result object
                        if data["label"] == keyword:
                            result["keywords"][idx]["data"].append(rank)
                            break


            return HttpResponse().success(status=HTTPStatus.OK, trend=result)
        else:
            return HttpResponse().failure(status=HTTPStatus.NOT_FOUND, error="Website does not exist")
    except Exception as exception:
        log.error("Unable to fetch website (%s): %s", id, exception)
        return HttpResponse().failure(status=HTTPStatus.INTERNAL_SERVER_ERROR, error="Unable to process the request")