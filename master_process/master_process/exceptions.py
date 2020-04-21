from redis.exceptions import ResponseError
from requests.exceptions import ConnectionError, HTTPError, Timeout
from django.db import DatabaseError, OperationalError, InternalError, IntegrityError, DataError


class RequestException(BaseException):
    def __init__(self, code):
        self.code = code


# Possible Exceptions
REDIS_EXCEPTIONS = (ConnectionError, ResponseError)
DB_EXCEPTIONS = (DatabaseError, OperationalError, InternalError, IntegrityError, DataError)
CONNECTION_EXCEPTIONS = (ConnectionError, HTTPError, Timeout, RequestException)
