from django.core.mail import send_mail
import datetime
from django.utils import timezone
from django.contrib.auth.models import User

def auto_email():
    # myfile = open("test.txt", "a")
    # myfile.write("\nexec\n")
    user_list = User.objects.all()
    to_addr = []
    body = []
    for user in user_list:
        if user.username != 'admin' and user.participant.is_verified:
            rem_time = user.participant.last_visit + datetime.timedelta(days=14) - timezone.now()
            delta_last_email = (timezone.now() - user.participant.last_email)
            if(delta_last_email > datetime.timedelta(days=14)):
                if(rem_time <= datetime.timedelta() and user.participant.sessions_completed < 6):
                    to_addr.append(user.email)
                    body.append("Hi, " + user.username + "! This is an email reminder for the follow-up survey. You have completed " + str(user.participant.sessions_completed) + " out of 6 sessions. Please visit the website to earn and participate: http://covidresearch.pythonanywhere.com/user/login/")
                    user.participant.last_email = timezone.now()
                    user.save()
    # to_addr = [i.email for i in user_list]
    # myfile.write(",".join(to_addr))
    # myfile.write("\n")
    # myfile.write("\n".join(body))
    for addr in to_addr:
        send_mail('Reminder for your next session.', 
            body[to_addr.index(addr)], 
            'vivek.pamnani.iiit.research@outlook.com', 
            [addr],
            fail_silently=True)

    # myfile.close()

if __name__ == "__main__":
    auto_email()