import time
import logging

from django.conf import settings
from celery.decorators import task

from racer_process.api_requests import APIRequest
from racer_process.common_utils import add_one_unit_to_point
from racer_process.constants import Constants
from racer_process.exceptions import REDIS_EXCEPTIONS, CONNECTION_EXCEPTIONS

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)


@task()
def send_pos_msg(point_of_intersection, m, c, lap_id, server_port):
    try:
        while settings.REDIS_DB.get(server_port + '-' + Constants.CURRENT_LAP_ID) and\
                (settings.REDIS_DB.get(server_port + '-' + Constants.CURRENT_LAP_ID).decode() == lap_id):
            point_of_intersection = add_one_unit_to_point(point_of_intersection, m, c)
            time.sleep(0.05)
            APIRequest.request(Constants.POST, settings.MASTER_BASE_URL + settings.POS_MESSAGE_ENDPOINT, data={
                'updated_x_coordinate': point_of_intersection[0],
                'updated_y_coordinate': point_of_intersection[1],
                'server_port': server_port
            })
    except REDIS_EXCEPTIONS as exc:
        logger.error('SendPosMsgTask: Error in redis connection')
        raise exc
    except CONNECTION_EXCEPTIONS as exc:
        settings.REDIS_DB.delete(server_port + '-' + Constants.CURRENT_LAP_ID)
        logger.error('SendPosMsgTask: Error in request connection')
        raise exc
