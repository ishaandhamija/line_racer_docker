import logging

from django.db import models
from django.conf import settings
from random import randrange

from master_process.api_requests import APIRequest
from master_process.common_utils import get_epoch_time
from master_process.constants import Constants


logger = logging.getLogger('MYAPP')


class LapMessage(models.Model):
    slope1 = models.IntegerField()
    constant1 = models.IntegerField()
    slope2 = models.IntegerField()
    constant2 = models.IntegerField()
    lap_completion_time = models.BigIntegerField(null=True)
    process_id = models.CharField(max_length=255)

    @staticmethod
    def save_current_lap():
        """
        Function to save lap details to the database
        :return:
        """
        slope1, constant1, slope2, constant2, start_time = tuple(settings.REDIS_DB.mget(
            [
                Constants.LAP_SLOPE_1,
                Constants.LAP_CONSTANT_1,
                Constants.LAP_SLOPE_2,
                Constants.LAP_CONSTANT_2,
                Constants.LAP_START_TIME,
            ]
        ))
        start_time = int(start_time)
        lap_completion_time = get_epoch_time() - start_time

        lap_message = LapMessage(slope1=slope1, constant1=constant1,
                                 slope2=slope2, constant2=constant2,
                                 lap_completion_time=lap_completion_time,
                                 process_id=settings.REDIS_DB.get(Constants.PROCESS_ID))
        lap_message.save()

    @classmethod
    def send_lap_msgs(cls):
        """
        Function to send lap messages to both the racers
        :return:
        """
        slope1 = randrange(1, 50)
        constant1 = randrange(1, 50)
        slope2 = randrange(1, 50)
        if slope1 == slope2:
            slope2 = slope2 + 1
        constant2 = randrange(1, 50)

        settings.REDIS_DB.mset({
            Constants.LAP_SLOPE_1: slope1,
            Constants.LAP_CONSTANT_1: constant1,
            Constants.LAP_SLOPE_2: slope2,
            Constants.LAP_CONSTANT_2: constant2,
            Constants.LAP_START_TIME: get_epoch_time()
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

    @classmethod
    def send_kill_msgs(cls):
        """
        Function to send kill messages to both the racers
        :return:
        """
        APIRequest.request(Constants.POST, settings.RACER_1_BASE_URL + settings.KILL_MESSAGE_ENDPOINT, data={
            Constants.PROCESS_ID: str(settings.REDIS_DB.get(Constants.PROCESS_ID))
        })
        APIRequest.request(Constants.POST, settings.RACER_2_BASE_URL + settings.KILL_MESSAGE_ENDPOINT, data={
            Constants.PROCESS_ID: str(settings.REDIS_DB.get(Constants.PROCESS_ID))
        })

    @classmethod
    def print_flow_summary(cls):
        """
        Function to print all laps summary
        :return:
        """
        lap_msgs = LapMessage.objects.filter(process_id=settings.REDIS_DB.get(Constants.PROCESS_ID)) \
            .order_by('lap_completion_time')
        for lap_msg in lap_msgs:
            print(lap_msg.slope1, '-', lap_msg.constant1, '-', lap_msg.slope2, '-', lap_msg.constant2, '-',
                  lap_msg.lap_completion_time)
        settings.REDIS_DB.delete(Constants.LAP_COUNT)
        settings.REDIS_DB.delete(Constants.PROCESS_ID)

    @classmethod
    def send_new_message_to_racers(cls):
        """
        Function to decide the message to be sent to racers and send it
        :return:
        """
        curr_lap_count = settings.REDIS_DB.get(Constants.LAP_COUNT)
        if curr_lap_count:
            curr_lap_count = int(curr_lap_count)
            if curr_lap_count == settings.NUMBER_OF_LAPS:
                cls.send_kill_msgs()
                cls.print_flow_summary()
                return
            else:
                settings.REDIS_DB.set(Constants.LAP_COUNT, curr_lap_count + 1)
        else:
            settings.REDIS_DB.set(Constants.LAP_COUNT, 1)

        cls.send_lap_msgs()
