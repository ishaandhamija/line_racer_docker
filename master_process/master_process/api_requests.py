import requests
import logging

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from master_process.exceptions import CONNECTION_EXCEPTIONS, RequestException

logging.basicConfig()
logger = logging.getLogger('MASTER_APP')
logger.setLevel(logging.INFO)


class APIRequest(object):

    @classmethod
    def _requests_retry_session(cls,
                                retries,
                                backoff_factor=0.3,
                                status_forcelist=(500, 502, 504),
                                session=None,
                                ):
        session = session or requests.Session()
        retry = Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

    @classmethod
    def request(cls, request_type, url, params=None, data=None,
                return_error=False, log_payload=True, log_params=True):
        try:
            request = requests.Session()
            logger.info('APIRequest: %s %s', request_type, url)
            if params and log_params:
                logger.info('APIRequest: QueryParams - %s', params)
            if data and log_payload:
                logger.info('APIRequest: Payload - %s', data)
            request = cls._requests_retry_session(retries=10, session=request)
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
            logger.error("Error response %s", response.content)
            raise RequestException(response.status_code)
        except CONNECTION_EXCEPTIONS as exc:
            logger.exception('APIRequest.send: exception - %s', exc)
            raise exc
