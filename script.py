import os
import django
import environ

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()


from django.core.mail import send_mail
import datetime
from django.utils import timezone
from django.contrib.auth.models import User
from django import db
db.connections.close_all()
db.close_old_connections()

env = environ.Env()

def auto_email():
    user_list = User.objects.all()
    to_addr = []
    body = []
    auto_note = '<br><br>Note that this is an automated email message. Please do not reply.'
    amounts = ['0', '100', '300', '200', '200', '200', '200']
    for user in user_list:
        if user.username != 'admin' and user.participant.is_verified:
            rem_time = user.participant.last_visit + datetime.timedelta(days=14) - timezone.now()
            delta_last_email = (timezone.now() - user.participant.last_email)
            # if(delta_last_email > datetime.timedelta(days=14)):
            #     if(rem_time <= datetime.timedelta() and user.participant.sessions_completed < 6):
            #         to_addr.append(user.email)
            #         body.append("Hi, " + user.username + "! <br><br>This is an email reminder for the follow-up survey. You have completed " + str(user.participant.sessions_completed) + " out of 6 sessions. Your reward for completing your next session is ₹" + amounts[user.participant.sessions_completed+1] + "! Please visit the website to earn and participate: https://www.imwbs.org/user/login/")
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
            #     body.append("Hi, " + user.username + "! <br><br>This is an email reminder for the upcoming follow-up session. You have completed " + str(user.participant.sessions_completed) + " out of 6 sessions. Your reward for completing your next session is ₹" + amounts[user.participant.sessions_completed+1] + "! Please visit the website AFTER 2 days to earn and participate: https://www.imwbs.org/user/login/ . We suggest you block your calendar about 2 days from now for a 30 minute slot.")
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
                user.participant.sessions_completed < 6 and
                delta_last_email > datetime.timedelta(days=1)
            ):
                to_addr.append(user.email)
                body.append("Hi, " + user.username + "! <br><br>This is an email reminder for the upcoming follow-up session. You have completed " + str(user.participant.sessions_completed) + " out of 6 sessions. Your reward for completing your next session is ₹" + amounts[user.participant.sessions_completed+1] + "! Please visit the website TOMORROW to earn and participate: https://www.imwbs.org/user/login/")
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
                user.participant.sessions_completed < 6 and
                delta_last_email > datetime.timedelta(hours=3)
            ):
                to_addr.append(user.email)
                body.append("Hi, " + user.username + "! <br><br>This is an email reminder for the upcoming follow-up session. You have completed " + str(user.participant.sessions_completed) + " out of 6 sessions. Your reward for completing your next session is ₹" + amounts[user.participant.sessions_completed+1] + "! Please visit the website any time TODAY to earn and participate: https://www.imwbs.org/user/login/")
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
                user.participant.sessions_completed < 6 and
                delta_last_email > datetime.timedelta(hours=23)
            ):
                to_addr.append(user.email)
                body.append("Hi, " + user.username + "! <br><br>This is an email reminder for the missed follow-up session. You have completed " + str(user.participant.sessions_completed) + " out of 6 sessions. Your reward for completing your next session is ₹" + amounts[user.participant.sessions_completed+1] + "! Please visit the website any time TODAY to earn and participate: https://www.imwbs.org/user/login/")
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
                user.participant.sessions_completed < 6 and
                delta_last_email > datetime.timedelta(hours=23)
            ):
                to_addr.append(user.email)
                body.append("Hi, " + user.username + "! <br><br>This is an email reminder for the missed follow-up session. You have completed " + str(user.participant.sessions_completed) + " out of 6 sessions. Your reward for completing your next session is ₹" + amounts[user.participant.sessions_completed+1] + "! Please visit the website any time TODAY to earn and participate: https://www.imwbs.org/user/login/")
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
            #     user.participant.sessions_completed < 6 and
            #     delta_last_email > datetime.timedelta(hours=23)
            # ):
            #     to_addr.append(user.email)
            #     body.append("Hi, " + user.username + "! <br><br>This is an email reminder for the missed follow-up session. You have completed " + str(user.participant.sessions_completed) + " out of 6 sessions. Your reward for completing your next session is ₹" + amounts[user.participant.sessions_completed+1] + "! Please visit the website any time TODAY to earn and participate: https://www.imwbs.org/user/login/")
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
                user.participant.sessions_completed < 6 and
                delta_last_email > datetime.timedelta(hours=23)
            ):
                to_addr.append(user.email)
                body.append("Hi, " + user.username + "! <br><br>This is an email reminder for the missed follow-up session. You have completed " + str(user.participant.sessions_completed) + " out of 6 sessions. Your reward for completing your next session is ₹" + amounts[user.participant.sessions_completed+1] + "! Please visit the website any time TODAY to earn and participate: https://www.imwbs.org/user/login/")
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
                user.participant.sessions_completed < 6 and
                delta_last_email > datetime.timedelta(hours=23)
            ):
                to_addr.append(user.email)
                body.append("Hi, " + user.username + "! <br><br>This is an email reminder for the missed follow-up session. You have completed " + str(user.participant.sessions_completed) + " out of 6 sessions. Your reward for completing your next session is ₹" + amounts[user.participant.sessions_completed+1] + "! Please visit the website any time TODAY to earn and participate: https://www.imwbs.org/user/login/ . Note that is the last email reminder from our side.")
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