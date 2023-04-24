import datetime
from email.policy import default

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

class participant(models.Model):
    def __str__(self):
        return self.user.username + ": " + self.user.email
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    visit_time_1 = models.DateTimeField(default=datetime.datetime(1000,1,1,0,0,0))
    visit_time_2 = models.DateTimeField(default=datetime.datetime(1000,1,1,0,0,0))
    visit_time_3 = models.DateTimeField(default=datetime.datetime(1000,1,1,0,0,0))
    visit_time_4 = models.DateTimeField(default=datetime.datetime(1000,1,1,0,0,0))
    visit_time_5 = models.DateTimeField(default=datetime.datetime(1000,1,1,0,0,0))
    visit_time_6 = models.DateTimeField(default=datetime.datetime(1000,1,1,0,0,0))
    last_visit = models.DateTimeField(default=datetime.datetime(1000,1,1,0,0,0))
    last_email = models.DateTimeField(default=datetime.datetime(1000,1,1,0,0,0))
    sessions_completed = models.IntegerField(default=0)
    is_verified = models.BooleanField(default=False)
    is_eligible = models.IntegerField(default=0) # 0 = not screened, 1 = eligible, 2 = ineligible
    is_colorBlind = models.BooleanField(default=True)
    is_colorTested = models.BooleanField(default=False)
    longitudinal_enrollment_status = models.IntegerField(default=0) # 0 = unproposed, 1 = opt in, 2 = opt out
    ref = models.CharField(default='noref', max_length=30)
    # cloudresearch_aid = models.CharField(default='', max_length=30)

class waitlist(models.Model):
    def __str__(self) -> str:
        return self.user.username
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.IntegerField(default=0)
    covid_history = models.BooleanField(default=False)

class codes(models.Model):
    def __str__(self):
        return str(self.otp)
        # return str(self.otp) + "; " + str(self.session_num) + "; " + str(self.is_paid)
    otp = models.CharField(max_length=12)
    session_num = models.IntegerField(default=0)
    is_paid = models.BooleanField(default=False)
    is_complete = models.BooleanField(default=False)
    ref = models.CharField(default='noref', max_length=30)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        long_enroll = 0 if settings.USER_LONGITUDINAL_OPT_IN is True else 1
        participant.objects.create(user=instance, longitudinal_enrollment_status=long_enroll)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if instance.is_superuser == 0: 
        instance.participant.save()