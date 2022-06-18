import json
from http import HTTPStatus
from flask import _request_ctx_stack

from sqlalchemy import and_, func
from datetime import datetime, timedelta
from src.lib.flask_cognito import cognito_auth_header_required_api, log
from src.lib.response import HttpResponse
from src.model.orm import Website, Trend

MAX_RANK = 100


@cognito_auth_header_required_api
def get_trend_for_website(website_id, engine, period):
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

                if period == "30d":
                    thirty_days_ago = (datetime.today() - timedelta(days=30)).date()
                    trends = Trend.query.filter(Trend.keyword == keyword.id, Trend.engine == engine,
                                                Trend.date > thirty_days_ago).order_by(
                        Trend.date).all()
                elif period == "7d":
                    seven_days_ago = (datetime.today() - timedelta(days=7)).date()
                    trends = Trend.query.filter(Trend.keyword == keyword.id, Trend.engine == engine,
                                                Trend.date > seven_days_ago).order_by(
                        Trend.date).all()
                elif period == "all":
                    trends = Trend.query.filter(Trend.keyword == keyword.id, Trend.engine == engine).order_by(
                        Trend.date).all()
                else:
                    return HttpResponse().failure(status=HTTPStatus.UNPROCESSABLE_ENTITY,
                                                  error="Invalid period selected. Must be one of: 7d, 30d, all")

                for trend in trends:
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
                    rank = -1
                    for tempTrend in tempTrends[keyword]:
                        # Keyword has rank associated to it on this specific day
                        if str(date) in tempTrend:
                            # Keep track of the rank
                            rank = tempTrend[str(date)] if tempTrend[str(date)] != -1 else MAX_RANK
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
