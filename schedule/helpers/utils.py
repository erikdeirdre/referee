"""Utilities used by other classes"""

class HttpError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code
