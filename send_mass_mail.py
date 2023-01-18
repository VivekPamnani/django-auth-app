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

## Remind EVERYONE to participote if they haven't.
# subject = "[Indian Mental Wellbeing Study] Reminder to participate."
# message_body = """
# <p> 
#     We noticed you signed up on the website but haven't proceeded through.
# </p>
# If you'd like to: 
# <ol>
#     <li>Learn about your mental well-being, </li>
#     <li>Contribute to science, and </li>
#     <li><b>Earn</b> up to ₹1200</li>
# </ol> 
# Please visit our website to participate: https://www.imwbs.org/user/home/ 
# """

## Message of non-payment.
subject = "[Indian Mental Wellbeing Study] Apology for delay in payments."
message_body = """
<p> 
    We apologize for the delay in payment of monetary compensation promised to you for participating in our study. We are working to resolve the issue and ask for your patience.
</p>
<p>
    We would like to urge you to continue participating in the study, as it is a valuable contribution to science. Your participation is important to the success of the research and we appreciate your willingness to be a part of it.
</p>
<p>
    However, we understand that this delay may have caused frustration, and if you choose to stop participating in the study, you will still be compensated for the sessions that you have already completed. We understand that this may be a difficult decision, but please know that we respect your right to do so.
</p>
<p>
    Thank you for your understanding and your continued participation in the study.
</p>
"""

message_auto = '<p>Note that this is an automated email message. Please do not reply.</p>'

def auto_email():
    user_list = User.objects.all()
    to_addr = []
    body = []
    amounts = ['0', '100', '300', '200', '200', '200', '200']
    datatuple = []
    from_email = str(env('SMTP_MAIL'))
    for user in user_list:
        if user.username == 'admin' or not user.participant.is_verified:
            continue
        rem_time = user.participant.last_visit + datetime.timedelta(days=14) - timezone.now()
        delta_last_email = (timezone.now() - user.participant.last_email)
        # if user.participant.sessions_completed == 0 and delta_last_email > datetime.timedelta(days=365):
        if True:
            message_greeting = "<p>Hi, " + user.username + "! </p>"
            message_greeting = "<p>Dear participants, </p>"
            # message_body = 
            message_info = "<p>Your username is " + user.username + ". If you forgot your password, follow this link: https://www.imwbs.org/user/reset/</p>"
            # message_auto = 
            message = message_greeting + message_body + message_info + message_auto + "<p>Regards, <br>IMWBS Team</p>"
            recipient = [user.email]
            # datatuple.append([subject, message + auto_note, from_email, recipient])
            user.participant.last_email = timezone.now()
            user.save()
            send_mail(subject,
                '',
                from_email,
                recipient,
                html_message=message,
                fail_silently=True)
    # send_mass_mail(datatuple, fail_silently=False)
    db.connections.close_all()
    db.close_old_connections()

if __name__ == "__main__":
    # print('Sending...')
    auto_email()