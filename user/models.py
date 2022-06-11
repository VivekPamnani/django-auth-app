from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import datetime
# Create your models here.

class participant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    visit_time_1 = models.DateTimeField(default=datetime.datetime(1000,1,1,0,0,0))
    visit_time_2 = models.DateTimeField(default=datetime.datetime(1000,1,1,0,0,0))
    visit_time_3 = models.DateTimeField(default=datetime.datetime(1000,1,1,0,0,0))
    visit_time_4 = models.DateTimeField(default=datetime.datetime(1000,1,1,0,0,0))
    visit_time_5 = models.DateTimeField(default=datetime.datetime(1000,1,1,0,0,0))
    visit_time_6 = models.DateTimeField(default=datetime.datetime(1000,1,1,0,0,0))
    last_visit = models.DateTimeField(default=datetime.datetime(1000,1,1,0,0,0))
    sessions_completed = models.IntegerField(default=0)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        participant.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if instance.is_superuser == 0: instance.participant.save()