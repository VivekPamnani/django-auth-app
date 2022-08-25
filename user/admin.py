from django.contrib import admin

# Register your models here.
from .models import participant, codes

admin.site.register(participant)
admin.site.register(codes)