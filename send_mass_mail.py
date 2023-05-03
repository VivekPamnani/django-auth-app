import os

import django
import environ

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

import datetime

from django import db
from django.contrib.auth.models import User
from django.core.mail import send_mail, send_mass_mail
from django.utils import timezone

from configSolo.models import SiteConfiguration

db.connections.close_all()
db.close_old_connections()

env = environ.Env()
site_config = SiteConfiguration.objects.get()

# ! Remind EVERYONE to participote if they haven't.
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

# ! Message of non-payment.
# subject = "[Indian Mental Wellbeing Study] Apology for delay in payments."
# message_body = """
# <p> 
#     We apologize for the delay in payment of monetary compensation promised to you for participating in our study. We are working to resolve the issue and ask for your patience.
# </p>
# <p>
#     We would like to urge you to continue participating in the study, as it is a valuable contribution to science. Your participation is important to the success of the research and we appreciate your willingness to be a part of it.
# </p>
# <p>
#     However, we understand that this delay may have caused frustration, and if you choose to stop participating, you will still be compensated for the sessions that you have already completed. We understand that choosing to continue participating despite the delay may be a difficult decision, but please know that we would really appreciate if you do so.
# </p>
# <p>
#     Thank you for your understanding and your continued participation in the study.
# </p>
# """

# ! Message of stopping participation.
subject = "[Indian Mental Wellbeing Study] Thank you for your participation."
# We hope that you found the study interesting and that you learned something new about yourself.
message_body = f"""
<p>
    Thank you for your participation in the Indian Mental Wellbeing Study. We would like to inform you about the latest developments in the study. We have decided to revise the study design and will be conducting the study in a different manner. While we are revising the design, it is not a revamp of the study, but rather a change in the way we are conducting the study. 
</p>
<p>
    For this reason, you will not be able to continue participating in the study. However, you will still be compensated for the sessions that you have already completed. The website will be updated to reflect this change. It is because of your participation that we are able to conduct this study, and your data has provided insights into the mental well-being of the Indian population. We would like to thank you for your contribution to science. We hope that you will continue to support us in our research. 
    We hope that you found the study interesting and that you learned something new about yourself.
</p>
<p>
    With your response data and the data from the revised study, we will be able to better understand the mental well-being of the Indian population. We are currently working on a paper that will be published in a peer-reviewed journal. We will share the link to the paper with you once it is published. 
</p>
<p>
    We request you to please refer our website to your friends and family, so that they can participate in the revised study and help us in our research. New participants can register on: {site_config.site_url}/user/register/. 
</p>
"""

message_auto = '<p>Note that this is an automated email message. Please do not reply. If you have any questions, please contact us at <a href="mailto:vivek.pamnani@research.iiit.ac.in"></a></p>'

def should_send_email(user):
    if (
        user.username == 'admin' or
        user.is_active is False or
        user.participant.is_verified is False
    ):
        return False
    elif user.username.startswith('test'):
        return True
    
    print(f"Error deciding for user: {user.username}")
    return False

def auto_email():
    user_list = User.objects.all()
    from_email = str(env('SMTP_MAIL'))
    
    for user in user_list:
        if not should_send_email(user):
            continue
        
        message_greeting = f"<p>Hi, {user.username}! </p>"
        message_greeting = "<p>Dear participants, </p>"
        message_info = f"<p>Your username is {user.username}. If you forgot your password, follow this link: {site_config.site_url}/user/reset/</p>"
        
        message = message_greeting + message_body + message_info + message_auto + "<p>Regards, <br>IMWBS Team</p>"
        
        recipient = [user.email]
        
        user.participant.last_email = timezone.now()
        user.save()
        
        send_mail(
            subject=subject,
            message='',
            from_email=from_email,
            recipient_list=recipient,
            html_message=message,
        )
    
    db.connections.close_all()
    db.close_old_connections()

if __name__ == "__main__":
    print('Sending...')
    auto_email()