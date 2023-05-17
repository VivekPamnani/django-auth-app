from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from solo.models import SingletonModel


class SiteConfiguration(SingletonModel):
    site_name = models.CharField(max_length=255, default='Indian Mental Wellbeing Study')
    # maintenance_mode = models.BooleanField(default=False)
    covid_count = models.IntegerField(default=0)
    suspect_count = models.IntegerField(default=0)
    noise_count = models.IntegerField(default=0)
    control_count = models.IntegerField(default=0)
    group_ratio = models.JSONField(default=dict)
    current_target = models.IntegerField(default=0)

    site_url = models.TextField(default='127.0.0.1:8000')


    def __str__(self):
        return "Site Configuration"

    class Meta:
        verbose_name = "Site Configuration"

@receiver(post_save, sender=SiteConfiguration)
def validate_site_configuration(sender, instance, created, **kwargs):
    print("Validating SiteConfiguration...")
    print(f"Sender: {sender}")
    print(f"Instance: {instance}")
    print(f"Created: {created}")

    if not created:
        return

    # * Validate keys
    instance.group_ratio = {
        'covid': 0.0,
        'suspect': 0.0,
        'noise': 0.0,
        'control': 0.0
    }
    try:
        for k, v in instance.group_ratio.items():
            instance.group_ratio[k] = round(settings.USER_GROUP_RATIO[k], 2)
    except Exception as e:
        instance.delete()
        raise Exception(f"""
            Error: Could not create SiteConfiguration instance.
            Details: {e}
            Please set USER_GROUP_RATIO in settings.py. It should be a dict with keys ['covid', 'suspect', 'noise', 'control'] and values that add up to 1.0.
        """)
    
    # * Validate values
    total_v = 0
    for k, v in instance.group_ratio.items():
        total_v += v
    if total_v != 1.0:
        orig_control = instance.group_ratio['control']
        new_control = round(1 - (total_v - orig_control), 2)
        if new_control < 0.0:
            instance.delete()
            raise Exception(f"""
                Error: Group ratios did not add up to 1.0.
                Could not fix this automatically.
                Please check the ratios in models.py and try again.
            """)
        instance.group_ratio['control'] = new_control
        print(f"""
            Warning: Group ratios did not add up to 1.0.
            Ratio for control group has been changed from {orig_control} -> {new_control}.
            You can adjust this in the admin panel.
        """)

    # * Validate noise group ratio
    if instance.group_ratio['noise'] != 0.0:
        print(f"""
            Warning: Noise group ratio is {instance.group_ratio['noise']}, but should be 0.0.
            You can adjust this in the admin panel.
            If this want intentional, please ignore this message.
        """)
    
    instance.save()