#!/usr/bin/env python3

"""Custom http response handler"""


class HttpResponse():
    """Custom http response class"""

    def _resp(self, status, **kwargs):
        data = {}
        error = ""
        for key, value in kwargs.items():
            if key == "error":
                error = value
            else:
                data.update({key: value})
        return {
            "status": status,
            "data": data,
            "error": error
        }

    def success(self, status, **kwargs):
        """Returns successful http request"""
        return self._resp("success", **kwargs), status.value

    def failure(self, status, **kwargs):
        """Returns failed http request"""
        return self._resp("failure", **kwargs), status.value
