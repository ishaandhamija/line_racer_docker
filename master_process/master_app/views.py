import logging

from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from master_app.models import LapMessage
from master_process.common_utils import distance_between_points
from master_process.constants import Constants
from master_process.exceptions import REDIS_EXCEPTIONS, DB_EXCEPTIONS, CONNECTION_EXCEPTIONS

logging.basicConfig()
logger = logging.getLogger('MASTER_APP')
logger.setLevel(logging.INFO)


class PosMsgView(APIView):

    def post(self, request):
        try:
            updated_x_coordinate = request.data.get('updated_x_coordinate')
            updated_y_coordinate = request.data.get('updated_y_coordinate')
            server_port = request.data.get('server_port')

            redis_key_prefix = None
            if server_port == settings.RACER_1_PORT:
                redis_key_prefix = settings.RACER_2_PORT
            elif server_port == settings.RACER_2_PORT:
                redis_key_prefix = settings.RACER_1_PORT

            if redis_key_prefix is not None:
                self.__check_other_port_redis_keys(redis_key_prefix, server_port,
                                                   updated_x_coordinate, updated_y_coordinate)

            return Response(
                data={
                    "success": True
                },
                status=status.HTTP_200_OK
            )
        except REDIS_EXCEPTIONS as exc:
            logger.error('PosMessageView: Error in redis connection - %s', exc)
        except DB_EXCEPTIONS as exc:
            logger.error('PosMessageView: Error in db connection - %s', exc)
        except CONNECTION_EXCEPTIONS as exc:
            logger.error('PosMessageView: Error in request connection - %s', exc)

        return Response(
            data={
                "success": False,
                "message": "Internal Server Error"
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    def __process_both_coordinates(self, x1, y1, x2, y2):
        """
        Function to process the coordinates from racer 1
        and racer 2 if they are more then 10 units apart
        :param x1: x coordinate of racer 1 point
        :param y1: y coordinate of racer 1 point
        :param x2: x coordinate of racer 2 point
        :param y2: y coordinate of racer 2 point
        :return:
        """
        dist = distance_between_points(x1, y1, x2, y2)
        if dist > 10:
            if settings.REDIS_DB.get(Constants.LAP_START_TIME_ISO):
                LapMessage.save_current_lap()
            LapMessage.send_new_message_to_racers()

    def __check_other_port_redis_keys(self, redis_key_prefix, server_port, updated_x_coordinate, updated_y_coordinate):
        """
        Function to check if pos message is received from both the racers
        :param redis_key_prefix:
        :param server_port:
        :param updated_x_coordinate:
        :param updated_y_coordinate:
        :return:
        """
        try:
            other_port_x, other_port_y = settings.REDIS_DB.mget(
                [
                    redis_key_prefix + Constants.X_COORDINATE_SUFFIX,
                    redis_key_prefix + Constants.Y_COORDINATE_SUFFIX
                ]
            )
            if other_port_x and other_port_y and updated_x_coordinate == float(other_port_x):
                settings.REDIS_DB.delete(redis_key_prefix + Constants.X_COORDINATE_SUFFIX)
                settings.REDIS_DB.delete(redis_key_prefix + Constants.Y_COORDINATE_SUFFIX)
                self.__process_both_coordinates(updated_x_coordinate, updated_y_coordinate,
                                                float(other_port_x), float(other_port_y))
            else:
                settings.REDIS_DB.mset({
                    server_port + Constants.X_COORDINATE_SUFFIX: updated_x_coordinate,
                    server_port + Constants.Y_COORDINATE_SUFFIX: updated_y_coordinate
                })

        except REDIS_EXCEPTIONS as exc:
            logger.error('CheckOtherPortRedisKeys: Error in redis connection - %s', exc)
            raise exc
