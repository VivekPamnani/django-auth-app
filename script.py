import os

import django
import environ

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()


import datetime

from django import db
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils import timezone
from configSolo.models import SiteConfiguration

MAX_SESSIONS = settings.USER_MAX_SESSIONS
SESSION_INTERVAL_DAYS = settings.USER_SESSION_INTERVAL_DAYS
SESSION_INTERVAL_DAYS_MAX = settings.USER_SESSION_INTERVAL_DAYS_MAX
SESSION_LINKS = settings.USER_SESSION_LINKS
SESSION_AMOUNTS = settings.USER_SESSION_AMOUNTS

db.connections.close_all()
db.close_old_connections()

env = environ.Env()
site_url = SiteConfiguration.objects.get().site_url

def auto_email():
    user_list = User.objects.all()
    to_addr = []
    body = []
    auto_note = '<br><br>Note that this is an automated email message. Please do not reply.'
    amounts = SESSION_AMOUNTS
    for user in user_list:
        if user.username != 'admin' and user.participant.is_verified and user.is_active:
            rem_time = user.participant.last_visit + datetime.timedelta(days=SESSION_INTERVAL_DAYS) - timezone.now()
            delta_last_email = (timezone.now() - user.participant.last_email)
            # if(delta_last_email > datetime.timedelta(days=14)):
            #     if(rem_time <= datetime.timedelta() and user.participant.sessions_completed < 6):
            #         to_addr.append(user.email)
            #         body.append("Hi, " + user.username + "! <br><br>This is an email reminder for the follow-up survey. You have completed " + str(user.participant.sessions_completed) + " out of 6 sessions. Your reward for completing your next session is ₹" + SESSION_AMOUNTS[user.participant.sessions_completed+1] + "! Please visit the website to earn and participate: {site_url}")
            #         user.participant.last_email = timezone.now()
            #         user.save()
            #         send_mail('Reminder for your next session.',
            #             '',
            #             'covid.research.iiit@gmail.com',
            #             [to_addr[-1]],
            #             html_message=body[-1] + auto_note,
            #             fail_silently=True)

            # # 2 DAYS BEFORE
            # if( rem_time <= datetime.timedelta(days=2) and
            #     rem_time >= datetime.timedelta(days=1) and
            #     user.participant.sessions_completed < 6 and
            #     delta_last_email > datetime.timedelta(days=2)
            # ):
            #     to_addr.append(user.email)
            #     body.append(f"Hi, {user.username}! <br><br>This is an email reminder for the upcoming follow-up session. You have completed {user.participant.sessions_completed} out of {MAX_SESSIONS} sessions. Your reward for completing your next session is ₹{SESSION_AMOUNTS[user.participant.sessions_completed+1]}! Please visit the website AFTER 2 days to earn and participate: {site_url} . We suggest you block your calendar about 2 days from now for a 30 minute slot.")
            #     user.participant.last_email = timezone.now()
            #     user.save()
            #     send_mail('[Indian Mental Wellbeing Study] Your next session is 2 days away.',
            #         '',
            #         str(env('SMTP_MAIL')),
            #         [to_addr[-1]],
            #         html_message=body[-1] + auto_note,
            #         fail_silently=True)

            # 1 DAY BEFORE
            if( rem_time <= datetime.timedelta(days=1) and
                rem_time >= datetime.timedelta() and
                user.participant.sessions_completed < MAX_SESSIONS and
                delta_last_email > datetime.timedelta(days=1)
            ):
                to_addr.append(user.email)
                body.append(f"Hi, {user.username}! <br><br>This is an email reminder for the upcoming follow-up session. You have completed {user.participant.sessions_completed} out of {MAX_SESSIONS} sessions. Your reward for completing your next session is ₹{SESSION_AMOUNTS[user.participant.sessions_completed+1]}! Please visit the website TOMORROW to earn and participate: {site_url} . We suggest you block your calendar for a 30 minute slot tomorrow. <p>You username is :{user.username}.<p>")
                user.participant.last_email = timezone.now()
                user.save()
                send_mail('[Indian Mental Wellbeing Study] Your next session is tomorrow.',
                    '',
                    str(env('SMTP_MAIL')),
                    [to_addr[-1]],
                    html_message=body[-1] + auto_note,
                    fail_silently=True)

            # 3 HOURS BEFORE
            if( rem_time <= datetime.timedelta(hours=3) and
                rem_time >= datetime.timedelta() and
                user.participant.sessions_completed < MAX_SESSIONS and
                delta_last_email > datetime.timedelta(hours=3)
            ):
                to_addr.append(user.email)
                body.append(f"Hi, {user.username}! <br><br>This is an email reminder for the upcoming follow-up session. You have completed {user.participant.sessions_completed} out of {MAX_SESSIONS} sessions. Your reward for completing your next session is ₹{SESSION_AMOUNTS[user.participant.sessions_completed+1]}! Please visit the website TODAY to earn and participate: {site_url} . <p>You username is :{user.username}.<p>")
                user.participant.last_email = timezone.now()
                user.save()
                send_mail('[Indian Mental Wellbeing Study] Your next session is TODAY.',
                    '',
                    str(env('SMTP_MAIL')),
                    [to_addr[-1]],
                    html_message=body[-1] + auto_note,
                    fail_silently=True)

            # 1 DAY AFTER
            if( rem_time < datetime.timedelta(hours=-20) and
                rem_time > datetime.timedelta(days=-1, hours=-20) and
                user.participant.sessions_completed < MAX_SESSIONS and
                delta_last_email > datetime.timedelta(hours=23)
            ):
                to_addr.append(user.email)
                body.append(f"Hi, {user.username}! <br><br>This is an email reminder for the missed follow-up session. You have completed {user.participant.sessions_completed} out of {MAX_SESSIONS} sessions. Your reward for completing your next session is ₹{SESSION_AMOUNTS[user.participant.sessions_completed+1]}! Please visit the website any time TODAY to earn and participate: {site_url} <p>You username is :{user.username}.<p>")
                user.participant.last_email = timezone.now()
                user.save()
                send_mail('[Indian Mental Wellbeing Study] Your next session is TODAY.',
                    '',
                    str(env('SMTP_MAIL')),
                    [to_addr[-1]],
                    html_message=body[-1] + auto_note,
                    fail_silently=True)

            # 2 DAYS AFTER
            if( rem_time < datetime.timedelta(days=-1, hours=-20) and
                rem_time > datetime.timedelta(days=-2, hours=-20) and
                user.participant.sessions_completed < MAX_SESSIONS and
                delta_last_email > datetime.timedelta(hours=23)
            ):
                to_addr.append(user.email)
                body.append(f"Hi, {user.username}! <br><br>This is an email reminder for the missed follow-up session. You have completed {user.participant.sessions_completed} out of {MAX_SESSIONS} sessions. Your reward for completing your next session is ₹{SESSION_AMOUNTS[user.participant.sessions_completed+1]}! Please visit the website any time TODAY to earn and participate: {site_url} <p>You username is :{user.username}.<p>")
                user.participant.last_email = timezone.now()
                user.save()
                send_mail('[Indian Mental Wellbeing Study] Your next session is TODAY.',
                    '',
                    str(env('SMTP_MAIL')),
                    [to_addr[-1]],
                    html_message=body[-1] + auto_note,
                    fail_silently=True)

            # # 3 DAYS AFTER
            # if( rem_time < datetime.timedelta(days=-2, hours=-20) and
            #     rem_time > datetime.timedelta(days=-3, hours=-20) and
            #     user.participant.sessions_completed < MAX_SESSIONS and
            #     delta_last_email > datetime.timedelta(hours=23)
            # ):
            #     to_addr.append(user.email)
            #     body.append(f"Hi, {user.username}! <br><br>This is an email reminder for the missed follow-up session. You have completed {user.participant.sessions_completed} out of {MAX_SESSIONS} sessions. Your reward for completing your next session is ₹{SESSION_AMOUNTS[user.participant.sessions_completed+1]}! Please visit the website any time TODAY to earn and participate: {site_url} <p>You username is :{user.username}.<p>")
            #     user.participant.last_email = timezone.now()
            #     user.save()
            #     send_mail('[Indian Mental Wellbeing Study] Your next session is TODAY.',
            #         '',
            #         str(env('SMTP_MAIL')),
            #         [to_addr[-1]],
            #         html_message=body[-1] + auto_note,
            #         fail_silently=True)

            # 4 DAYS AFTER
            if( rem_time < datetime.timedelta(days=-3, hours=-20) and
                rem_time > datetime.timedelta(days=-4, hours=-20) and
                user.participant.sessions_completed < MAX_SESSIONS and
                delta_last_email > datetime.timedelta(hours=23)
            ):
                to_addr.append(user.email)
                body.append(f"Hi, {user.username}! <br><br>This is an email reminder for the missed follow-up session. You have completed {user.participant.sessions_completed} out of {MAX_SESSIONS} sessions. Your reward for completing your next session is ₹{SESSION_AMOUNTS[user.participant.sessions_completed+1]}! Please visit the website any time TODAY to earn and participate: {site_url} <p>You username is :{user.username}.<p>")
                user.participant.last_email = timezone.now()
                user.save()
                send_mail('[Indian Mental Wellbeing Study] Your next session is TODAY.',
                    '',
                    str(env('SMTP_MAIL')),
                    [to_addr[-1]],
                    html_message=body[-1] + auto_note,
                    fail_silently=True)

            # 5 DAYS AFTER
            if( rem_time < datetime.timedelta(days=-4, hours=-20) and
                rem_time > datetime.timedelta(days=-5, hours=-20) and
                user.participant.sessions_completed < MAX_SESSIONS and
                delta_last_email > datetime.timedelta(hours=23)
            ):
                to_addr.append(user.email)
                body.append(f"Hi, {user.username}! <br><br>This is an email reminder for the missed follow-up session. You have completed {user.participant.sessions_completed} out of {MAX_SESSIONS} sessions. Your reward for completing your next session is ₹{SESSION_AMOUNTS[user.participant.sessions_completed+1]}! Please visit the website any time TODAY to earn and participate: {site_url} . Note that is the last email reminder from our side. <p>You username is :{user.username}.<p>")
                user.participant.last_email = timezone.now()
                user.save()
                send_mail('[Indian Mental Wellbeing Study] Your next session is TODAY.',
                    '',
                    str(env('SMTP_MAIL')),
                    [to_addr[-1]],
                    html_message=body[-1] + auto_note,
                    fail_silently=True)
    db.connections.close_all()
    db.close_old_connections()

if __name__ == "__main__":
    # print('Sending...')
    auto_email()