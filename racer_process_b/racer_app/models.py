from django.db import models


class LapMessage(models.Model):
    slope1 = models.IntegerField()
    constant1 = models.IntegerField()
    slope2 = models.IntegerField()
    constant2 = models.IntegerField()
    lap_completion_time = models.BigIntegerField(null=True)
    process_id = models.CharField(max_length=255)

    class Meta:
        db_table = 'master_app_lapmessage'
