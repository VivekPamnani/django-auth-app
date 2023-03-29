from django.conf import settings


def user_settings(request):
    return {
        'MAX_SESSIONS': settings.USER_MAX_SESSIONS,
        'SESSION_INTERVAL_DAYS': settings.USER_SESSION_INTERVAL_DAYS,
        'SESSION_INTERVAL_DAYS_MAX': settings.USER_SESSION_INTERVAL_DAYS_MAX,
        'SESSION_LINKS': settings.USER_SESSION_LINKS,
        'SESSION_AMOUNTS': settings.USER_SESSION_AMOUNTS,
        'MAX_AMOUNT': sum(settings.USER_SESSION_AMOUNTS),
    }