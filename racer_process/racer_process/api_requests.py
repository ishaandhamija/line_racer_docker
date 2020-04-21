import requests
import logging


logger = logging.getLogger('MYAPP')


class RequestException(BaseException):
    def __init__(self, code):
        self.code = code


class APIRequest(object):

    @classmethod
    def request(cls, request_type, url, params=None, data=None, raise_exception=False,
                return_error=False, log_payload=True, log_params=True):
        try:
            request = requests.Session()
            logger.info('APIRequest: %s %s', request_type, url)
            if params and log_params:
                logger.info('APIRequest: QueryParams - %s', params)
            if data and log_payload:
                logger.info('APIRequest: Payload - %s', data)
            response = request.request(
                request_type,
                url,
                params=params,
                json=data
            )
            logger.info('APIRequest.send: Response<%s> - %s', response.status_code, response.content)
            if response.status_code in [200, 201]:
                return response.json()
            elif return_error and response.status_code == 400:
                return response.json()
            if raise_exception:
                logger.info("Error response %s", response.content)
                raise RequestException(response.status_code)
        except Exception as e:
            logger.exception('APIRequest.send: exception - ')
            if raise_exception:
                raise e
        return None
