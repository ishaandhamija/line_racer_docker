import math

from datetime import datetime


def distance_between_points(x1, y1, x2, y2):
    """
    Function to calculate distance
    :param x1: x-coordinate of point 1
    :param y1: y-coordinate of point 1
    :param x2: x-coordinate of point 2
    :param y2: y-coordinate of point 2
    :return: distance between the points
    """
    return math.sqrt(math.pow(x2 - x1, 2) + math.pow(y2 - y1, 2) * 1.0)


def get_epoch_time(dt_obj=None):
    """
    Function to compute epoch time
    :param dt_obj: datetime object
    :return: epoch time in microseconds
    """
    if not dt_obj:
        dt_obj = datetime.now()
    return int((dt_obj - datetime(1970, 1, 1)).total_seconds()*1000000)
