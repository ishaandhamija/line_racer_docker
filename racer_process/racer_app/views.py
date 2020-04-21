from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from uuid import uuid4

from racer_app.models import LapMessage
from racer_process.common_utils import line_intersection
from racer_process.celery_tasks import send_pos_msg
from racer_process.constants import Constants


@api_view(http_method_names=['POST'])
def lap_message(request):
    m1 = request.data.get(Constants.M1)
    c1 = request.data.get(Constants.C1)
    m2 = request.data.get(Constants.M2)
    c2 = request.data.get(Constants.C2)

    point_of_intersection = line_intersection(m1, c1, m2, c2)

    m, c = None, None
    if request.META[Constants.SERVER_PORT] == settings.RACER_1_PORT:
        m, c = m1, c1
    elif request.META[Constants.SERVER_PORT] == settings.RACER_2_PORT:
        m, c = m2, c2

    if m and c:
        lap_id = str(uuid4())
        settings.REDIS_DB.set(request.META[Constants.SERVER_PORT] + '-' + Constants.CURRENT_LAP_ID, lap_id)
        send_pos_msg.delay(point_of_intersection, m, c, lap_id, request.META[Constants.SERVER_PORT])

    return Response(
        data={
            "success": True
        },
        status=status.HTTP_200_OK
    )


@api_view(http_method_names=['POST'])
def kill_message(request):
    settings.REDIS_DB.delete(request.META[Constants.SERVER_PORT] + '-' + Constants.CURRENT_LAP_ID)

    process_id = request.data.get(Constants.PROCESS_ID)
    lap_msgs = LapMessage.objects.filter(process_id=process_id)

    for lap_msg in lap_msgs:
        print(lap_msg.slope1, '-', lap_msg.constant1, '-', lap_msg.slope2, '-', lap_msg.constant2)

    return Response(
        data={
            "success": True
        },
        status=status.HTTP_200_OK
    )
