import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()


from django.core.mail import send_mail
import datetime
from django.utils import timezone
from django.contrib.auth.models import User

def auto_email():
    user_list = User.objects.all()
    to_addr = []
    body = []
    for user in user_list:
        if user.username != 'admin' and user.participant.is_verified:
            rem_time = user.participant.last_visit + datetime.timedelta(days=14) - timezone.now()
            delta_last_email = (timezone.now() - user.participant.last_email)
            # if(delta_last_email > datetime.timedelta(days=14)):
                # if(rem_time <= datetime.timedelta() and user.participant.sessions_completed < 6):
                #     to_addr.append(user.email)
                #     body.append("Hi, " + user.username + "! This is an email reminder for the follow-up survey. You have completed " + str(user.participant.sessions_completed) + " out of 6 sessions. Please visit the website to earn and participate: http://covidresearch.pythonanywhere.com/user/login/")
                #     user.participant.last_email = timezone.now()
                #     user.save()
                #     send_mail('Reminder for your next session.', 
                #         body[-1], 
                #         'covid.research.iiit@gmail.com', 
                #         [to_addr[-1]],
                #         fail_silently=True)
            if(rem_time <= datetime.timedelta(days=2) and user.participant.sessions_completed < 6 and delta_last_email > datetime.timedelta(days=2)):
                to_addr.append(user.email)
                body.append("Hi, " + user.username + "! This is an email reminder for the upcoming follow-up session. You have completed " + str(user.participant.sessions_completed) + " out of 6 sessions. Please visit the website AFTER 2 days to earn and participate: http://covidresearch.pythonanywhere.com/user/login/")
                user.participant.last_email = timezone.now()
                user.save()
                send_mail('Your next session is 2 days away.', 
                    body[-1], 
                    'covid.research.iiit@gmail.com', 
                    [to_addr[-1]],
                    fail_silently=True)

            if(rem_time <= datetime.timedelta(days=1) and user.participant.sessions_completed < 6 and delta_last_email > datetime.timedelta(days=1)):
                to_addr.append(user.email)
                body.append("Hi, " + user.username + "! This is an email reminder for the upcoming follow-up session. You have completed " + str(user.participant.sessions_completed) + " out of 6 sessions. Please visit the website TOMORROW to earn and participate: http://covidresearch.pythonanywhere.com/user/login/")
                user.participant.last_email = timezone.now()
                user.save()
                send_mail('Your next session is tomorrow.', 
                    body[-1], 
                    'covid.research.iiit@gmail.com', 
                    [to_addr[-1]],
                    fail_silently=True)

            if(rem_time <= datetime.timedelta(hours=2) and user.participant.sessions_completed < 6 and delta_last_email > datetime.timedelta(days=14)):
                to_addr.append(user.email)
                body.append("Hi, " + user.username + "! This is an email reminder for the upcoming follow-up session. You have completed " + str(user.participant.sessions_completed) + " out of 6 sessions. Please visit the website any time TODAY to earn and participate: http://covidresearch.pythonanywhere.com/user/login/")
                user.participant.last_email = timezone.now()
                user.save()
                send_mail('Your next session is TODAY.', 
                    body[-1], 
                    'covid.research.iiit@gmail.com', 
                    [to_addr[-1]],
                    fail_silently=True)                    

if __name__ == "__main__":
    # print('Sending...')
    auto_email()