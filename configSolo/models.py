from django.db import models
from solo.models import SingletonModel


class SiteConfiguration(SingletonModel):
    # site_name = models.CharField(max_length=255, default='Site Name')
    # maintenance_mode = models.BooleanField(default=False)
    control_count = models.IntegerField(default=0)
    covid_count = models.IntegerField(default=0)
    current_target = models.IntegerField(default=0)
    control_ratio = models.FloatField(default=0.2)

    def __str__(self):
        return "Site Configuration"

    class Meta:
        verbose_name = "Site Configuration"