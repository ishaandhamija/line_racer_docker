import logging

from django.db import models
from django.conf import settings
from random import randrange
from datetime import datetime

from master_process.api_requests import APIRequest
from master_process.common_utils import get_epoch_time
from master_process.constants import Constants
from master_process.exceptions import REDIS_EXCEPTIONS, DB_EXCEPTIONS, CONNECTION_EXCEPTIONS

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class LapMessage(models.Model):
    lap_number = models.IntegerField()
    slope1 = models.IntegerField()
    constant1 = models.IntegerField()
    slope2 = models.IntegerField()
    constant2 = models.IntegerField()
    lap_start_time = models.CharField(max_length=255)
    lap_end_time = models.CharField(max_length=255)
    lap_completion_time = models.BigIntegerField(null=True)
    process_id = models.CharField(max_length=255)

    @staticmethod
    def save_current_lap():
        """
        Function to save lap details to the database
        :return:
        """
        try:
            slope1, constant1, slope2, constant2, start_time, start_time_iso, lap_number, process_id = tuple(settings.REDIS_DB.mget(
                [
                    Constants.LAP_SLOPE_1,
                    Constants.LAP_CONSTANT_1,
                    Constants.LAP_SLOPE_2,
                    Constants.LAP_CONSTANT_2,
                    Constants.LAP_START_TIME,
                    Constants.LAP_START_TIME_ISO,
                    Constants.LAP_COUNT,
                    Constants.PROCESS_ID
                ]
            ))
            start_time = int(start_time)
            current_dt = datetime.now()
            lap_completion_time = get_epoch_time(current_dt) - start_time

            lap_message = LapMessage(lap_number=int(lap_number),
                                     slope1=slope1, constant1=constant1,
                                     slope2=slope2, constant2=constant2,
                                     lap_start_time=start_time_iso,
                                     lap_end_time=current_dt.isoformat(),
                                     lap_completion_time=lap_completion_time,
                                     process_id=process_id)
            lap_message.save()

        except REDIS_EXCEPTIONS as exc:
            logger.error('SaveCurrentLap: Error in redis connection - %s', exc)
            raise exc
        except DB_EXCEPTIONS as exc:
            logger.error('SaveCurrentLap: Error in db connection - %s', exc)
            raise exc

    @classmethod
    def send_new_message_to_racers(cls):
        """
        Function to decide the message to be sent to racers and send it
        :return:
        """
        try:
            curr_lap_count = settings.REDIS_DB.get(Constants.LAP_COUNT)
            curr_lap_count = int(curr_lap_count)
            if curr_lap_count == settings.NUMBER_OF_LAPS:
                cls.__send_kill_msgs()
                cls.__print_flow_summary()
                return

            settings.REDIS_DB.set(Constants.LAP_COUNT, curr_lap_count + 1)
            cls.__send_lap_msgs()

        except REDIS_EXCEPTIONS as exc:
            logger.error('SendNewMsgToRacers: Error in redis connection - %s', exc)
            raise exc
        except DB_EXCEPTIONS as exc:
            logger.error('SendNewMsgToRacers: Error in db connection - %s', exc)
            raise exc
        except CONNECTION_EXCEPTIONS as exc:
            logger.error('SendNewMsgToRacers: Error in request connection - %s', exc)
            raise exc

    @classmethod
    def __send_lap_msgs(cls):
        """
        Function to send lap messages to both the racers
        :return:
        """
        try:
            slope1 = randrange(1, 50)
            constant1 = randrange(1, 50)
            slope2 = randrange(1, 50)
            if slope1 == slope2:
                slope2 = slope2 + 1
            constant2 = randrange(1, 50)

            current_dt = datetime.now()

            settings.REDIS_DB.mset({
                Constants.LAP_SLOPE_1: slope1,
                Constants.LAP_CONSTANT_1: constant1,
                Constants.LAP_SLOPE_2: slope2,
                Constants.LAP_CONSTANT_2: constant2,
                Constants.LAP_START_TIME: get_epoch_time(current_dt),
                Constants.LAP_START_TIME_ISO: current_dt.isoformat()
            })

            APIRequest.request(Constants.POST, settings.RACER_1_BASE_URL + settings.LAP_MESSAGE_ENDPOINT, data={
                Constants.M1: slope1,
                Constants.C1: constant1,
                Constants.M2: slope2,
                Constants.C2: constant2,
            })

            APIRequest.request(Constants.POST, settings.RACER_2_BASE_URL + settings.LAP_MESSAGE_ENDPOINT, data={
                Constants.M1: slope1,
                Constants.C1: constant1,
                Constants.M2: slope2,
                Constants.C2: constant2,
            })

        except REDIS_EXCEPTIONS as exc:
            logger.error('SendLapMsgs: Error in redis connection - %s', exc)
            raise exc
        except CONNECTION_EXCEPTIONS as exc:
            logger.error('SendLapMsgs: Error in request connection - %s', exc)
            raise exc

    @classmethod
    def __send_kill_msgs(cls):
        """
        Function to send kill messages to both the racers
        :return:
        """
        try:
            APIRequest.request(Constants.POST, settings.RACER_1_BASE_URL + settings.KILL_MESSAGE_ENDPOINT, data={
                Constants.PROCESS_ID: str(settings.REDIS_DB.get(Constants.PROCESS_ID))
            })
            APIRequest.request(Constants.POST, settings.RACER_2_BASE_URL + settings.KILL_MESSAGE_ENDPOINT, data={
                Constants.PROCESS_ID: str(settings.REDIS_DB.get(Constants.PROCESS_ID))
            })

        except REDIS_EXCEPTIONS as exc:
            logger.error('SendKillMsgs: Error in redis connection - %s', exc)
            raise exc
        except CONNECTION_EXCEPTIONS as exc:
            logger.error('SendKillMsgs: Error in request connection - %s', exc)
            raise exc

    @classmethod
    def __print_flow_summary(cls):
        """
        Function to print all laps summary
        :return:
        """
        try:
            lap_msgs = LapMessage.objects.filter(process_id=settings.REDIS_DB.get(Constants.PROCESS_ID)) \
                .order_by('lap_completion_time')
            logger.info('lap_number - m1 - c1 - m2 - c2 - lap_start_time '
                        '- lap_end_time - lap_completion_time (in ms)')
            for lap_msg in lap_msgs:
                logger.info('%s - %s - %s - %s - %s - %s - %s - %s',
                            lap_msg.lap_number,
                            lap_msg.slope1, lap_msg.constant1,
                            lap_msg.slope2, lap_msg.constant2,
                            lap_msg.lap_start_time,
                            lap_msg.lap_end_time,
                            lap_msg.lap_completion_time / 1000)
            settings.REDIS_DB.delete(Constants.LAP_COUNT)
            settings.REDIS_DB.delete(Constants.PROCESS_ID)

        except REDIS_EXCEPTIONS as exc:
            logger.error('PrintFlowSummary: Error in redis connection - %s', exc)
            raise exc
        except DB_EXCEPTIONS as exc:
            logger.error('PrintFlowSummary: Error in request connection - %s', exc)
            raise exc
