import os
import django
import environ

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()


from django.core.mail import send_mail, send_mass_mail
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
    auto_note = '<p>Note that this is an automated email message. Please do not reply.</p>'
    amounts = ['0', '100', '300', '200', '200', '200', '200']
    datatuple = []
    from_email = str(env('SMTP_MAIL'))
    for user in user_list:
        if user.username == 'admin' or not user.participant.is_verified:
            continue
        rem_time = user.participant.last_visit + datetime.timedelta(days=14) - timezone.now()
        delta_last_email = (timezone.now() - user.participant.last_email)
        if user.participant.sessions_completed == 0 and delta_last_email > datetime.timedelta(days=365):
            subject = '[Indian Mental Wellbeing Study] Reminder to participate.'
            # message = "Hi, " + user.username + "! <br><br>We noticed you signed up on the website but haven't proceeded through. If you'd like to: <ol> <li>Learn about your mental well-being, </li><li>Contribute to science, and </li><li><b>Earn</b> up to ₹1200</li></ol> Please visit our website to participate: https://www.imwbs.org/user/login/" 
            message = "<p>Hi, " + user.username + "!</p> <p>We noticed you signed up on the website but haven't proceeded through.</p>If you'd like to: <ol> <li>Learn about your mental well-being, </li><li>Contribute to science, and </li><li><b>Earn</b> up to ₹1200</li></ol> Please visit our website to participate: https://www.imwbs.org/user/login/ <p>Your username is " + user.username + ". If you forgot your password, follow this link: https://www.imwbs.org/user/reset/</p>"
            recipient = [user.email]
            # datatuple.append([subject, message + auto_note, from_email, recipient])
            user.participant.last_email = timezone.now()
            user.save()
            send_mail('[Indian Mental Wellbeing Study] Reminder to participate.',
                '',
                from_email,
                recipient,
                html_message=message + auto_note,
                fail_silently=True)
    # send_mass_mail(datatuple, fail_silently=False)
    db.connections.close_all()
    db.close_old_connections()

if __name__ == "__main__":
    # print('Sending...')
    auto_email()