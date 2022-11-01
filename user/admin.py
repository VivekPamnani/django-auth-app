from django.contrib import admin

# Register your models here.
from .models import participant, codes

@admin.action(description='Mark paid')
def mark_paid(modeladmin, request, queryset):
    queryset.update(is_paid=True)

@admin.action(description='Mark tested and not color blind')
def mark_notBlind(modeladmin, request, queryset):
    queryset.update(is_colorBlind=False, is_colorTested=True)

class CodesAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'is_paid', 'session_num']
    # ordering = ['title']
    actions = [mark_paid]

class ParticipantsAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'sessions_completed', 'last_visit', 'last_email', 'ref']
    actions = [mark_notBlind]

admin.site.register(participant, ParticipantsAdmin)
admin.site.register(codes, CodesAdmin)