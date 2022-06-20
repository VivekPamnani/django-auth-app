from django.core.mail import send_mail
import datetime
from django.utils import timezone
from django.contrib.auth.models import User

def auto_email():
    user_list = User.objects.all()
    to_addr = []
    for user in user_list:
        if user.username != 'admin' and user.participant.is_verified:
            rem_time = user.participant.last_visit + datetime.timedelta(days=14) - timezone.now()
            delta_last_email = (timezone.now() - user.participant.last_email)
            if(delta_last_email > datetime.timedelta(days=14)):
                if(rem_time <= datetime.timedelta()):
                    to_addr.append(user.email)
                    user.participant.last_email = timezone.now()
    # to_addr = [i.email for i in user_list]
    send_mail('testing django auto-mail', 
        'message', 
        'vivek.pamnani.iiit.research@outlook.com', 
        to_addr,
        fail_silently=True)

if __name__ == "__main__":
    auto_email()