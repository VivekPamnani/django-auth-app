from dataclasses import dataclass
from email.policy import default
from logging import exception
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.views import generic
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
import datetime
from django.utils import timezone
import user
from user.models import codes
import shortuuid
import pytz
import json
from verify_email.email_handler import send_verification_email
from django.core.mail import send_mail

def index(request):
    return HttpResponse("this is the index page")

def instructions(request):
    return render(request, 'user/instructions.html')

def user_init(user):
    user.participant.sessions_completed = 0
    user.save()

def user_new_visit(user):
    user.participant.sessions_completed += 1
    t = timezone.now()
    user.participant.last_visit = t
    ob = codes.objects.create(otp=shortuuid.ShortUUID().random(length=12), session_num=user.participant.sessions_completed)
    if (user.participant.sessions_completed==1):
        user.participant.visit_time_1 = t
    elif (user.participant.sessions_completed==2):
        user.participant.visit_time_2 = t
    elif (user.participant.sessions_completed==3):
        user.participant.visit_time_3 = t
    elif (user.participant.sessions_completed==4):
        user.participant.visit_time_4 = t
    elif (user.participant.sessions_completed==5):
        user.participant.visit_time_5 = t
    elif (user.participant.sessions_completed==6):
        user.participant.visit_time_6 = t
    else:
        return HttpResponse("Something went wrong.")
    user.save()
    return ob.otp

def verify_email(request):
    try:
        entered_code = request.POST['code']
    except:
        return render(request, 'user/verification.html', context={'left': request.session['attempts_left']})
    else:
        user = get_object_or_404(User, username=request.session['verif_user'])
        if(request.session['verif_code'] == entered_code):
            user.participant.is_verified = True
            user.save()
            del request.session['verif_user']
            del request.session['verif_code']
            del request.session['attempts_left']
            return HttpResponse("Your account has been verified! Click here to proceed to the instructions: " + '<a href="/user/instructions"}>Continue.</a>')
        else:
            if(request.session['attempts_left'] > 1):
                request.session['attempts_left'] -= 1
                return render(request, 'user/verification.html', context={'left': request.session['attempts_left']})
            else:
                del request.session['verif_user']
                del request.session['verif_code']
                del request.session['attempts_left']
                user.delete()
                return HttpResponse('Sorry, too many wrong attempts! Click here to proceed to the registration page to try again: ' + '<a href="/user/register">Register</a>')

def register(request):
    try:
        entered_username = request.POST['username']
        entered_email = request.POST['email']
        entered_pwd = request.POST['password']
        # user = User.objects.create_user(entered_username, entered_email, entered_pwd)
    except:
        return render(request, 'user/registration.html')
    else:
        verification_code = shortuuid.ShortUUID(alphabet="0123456789").random(length=4)
        msg = "Please enter the following OTP to verify your email: " + str(verification_code)
        send_mail('Verify your email address for participation.',
            msg,
            'vivek.pamnani.iiit.research@outlook.com',
            [entered_email],
            fail_silently=True)
        user = User.objects.create_user(entered_username, entered_email, entered_pwd)
        request.session['verif_code'] = verification_code
        request.session['verif_user'] = user.username
        request.session['attempts_left'] = 3
        return redirect('user:verify')
    #     user.save()
    #     user_init(user)
    # user = authenticate(request, username=entered_username, password=entered_pwd)
    # if user is not None:
    #     login(request, user=user)
    #     return redirect("/user/home/")
    # else:
    #     return HttpResponse("Something went wrong.")

def signin(request):
    try:
        entered_username = request.POST['username']
        # entered_email = request.POST['email']
        entered_pwd = request.POST['password']
    except:
        return render(request, 'user/login.html', context={'err_msg': ''})
    else:
        user = authenticate(request, username=entered_username, password=entered_pwd)
        if user is not None:
            login(request, user=user)
            return HttpResponseRedirect('/user/home')
        else:
            return render(request, 'user/login.html', context={'err_msg': 'Invalid username or password.'})

def signout(request):
    logout(request)
    return redirect('/user/login/')

def home(request):
    if request.user.is_authenticated and request.user.participant.is_verified:
        user = request.user
        progress_percentage = user.participant.sessions_completed / 6 * 100
        leftnum = user.participant.sessions_completed - 3 if user.participant.sessions_completed > 3 else 0
        rightnum = user.participant.sessions_completed if user.participant.sessions_completed < 3 else 3
        rem_time = user.participant.last_visit.replace(microsecond=0) + datetime.timedelta(days=14) - timezone.now().replace(microsecond=0)
        # rem_time = rem_time.replace(microsecond=0)
        # if(rem_time <= datetime.timedelta()):
        #     rem_time = datetime.timedelta()
        return render(request,
                    'user/dashboard.html',
                    context={
                        'user': user,
                        'percentage': int(progress_percentage),
                        'leftnum': leftnum,
                        'rightnum': rightnum,
                        'earned': 200 * user.participant.sessions_completed,
                        'remtime': rem_time if user.participant.sessions_completed != 0 else str(datetime.timedelta())
                    })
    else:
        return redirect('/user/login')

def directions(request):
    if request.user.is_authenticated and request.user.participant.is_verified:
        user = request.user
        rem_time = user.participant.last_visit.replace(microsecond=0) + datetime.timedelta(days=14) - timezone.now().replace(microsecond=0)
        if(rem_time > datetime.timedelta()):
            return HttpResponse("Sorry you would have to wait %s until your next attempt." % rem_time)
        else:
            return render(request, 'user/directions.html')
    else:
        return redirect('/user/login')

def log_visit(request):
    if request.user.is_authenticated and request.user.participant.is_verified:
        # return HttpResponse(json.dumps([i.email for i in User.objects.all()]), content_type="application/json")
        user = request.user
        utc = pytz.UTC
        old = user.participant.last_visit
        # dt = datetime.datetime.strptime(str(old), '%Y-%m-%d %H:%M:%S')
        windback = timezone.now() - datetime.timedelta(days=14)
        last_time = old#.replace(tzinfo=utc)
        wind_time = windback#.replace(tzinfo=utc)
        rem_time = last_time + datetime.timedelta(days=14) - timezone.now()
        if(rem_time > datetime.timedelta()):
            return HttpResponse('Sorry, you cannot attempt the experiment more than once in two weeks. Time until next attempt: %s' % rem_time)
        else:
            if user.participant.sessions_completed < 6:
                otp = user_new_visit(user)
                if request.method == "GET":
                    return HttpResponseRedirect(reverse('user:visit_success', args=(), kwargs={'otp': otp}))
            else:
                return HttpResponse("You have completed all of your sessions and thus cannot attempt further tests. We thank you for your participation!")
    else:
        return redirect('/user/login/')

def visit_success(request, otp):
    if request.user.is_authenticated and request.user.participant.is_verified:
        user = request.user
        if(user.participant.sessions_completed==1):
            return render(request, 'user/attempt.html', {
                'user': user,
                'otp' : otp,
                'url' : "https://www.psytoolkit.org/c/3.4.0/survey?s=ZYQWa"
            })
        elif(user.participant.sessions_completed==2):
            return render(request, 'user/attempt.html', {
                'user': user,
                'otp' : otp,
                'url' : "https://www.psytoolkit.org/c/3.4.0/survey?s=W6bf8"
            })

        elif(user.participant.sessions_completed==3):
            return render(request, 'user/attempt.html', {
                'user': user,
                'otp' : otp,
                'url' : "https://www.psytoolkit.org/c/3.4.0/survey?s=uBY8M"
            })

        elif(user.participant.sessions_completed==4):
            return render(request, 'user/attempt.html', {
                'user': user,
                'otp' : otp,
                'url' : "https://www.psytoolkit.org/c/3.4.0/survey?s=jeph9"
            })

        elif(user.participant.sessions_completed==5):
            return render(request, 'user/attempt.html', {
                'user': user,
                'otp' : otp,
                'url' : "https://www.psytoolkit.org/c/3.4.0/survey?s=gZxRf"
            })

        elif(user.participant.sessions_completed==6):
            return render(request, 'user/attempt.html', {
                'user': user,
                'otp' : otp,
                'url' : "https://www.psytoolkit.org/c/3.4.0/survey?s=e4STN"
            })
        else:
            return HttpResponse("Something went wrong.")
            # return render(request, 'user/attempt.html', {
            #     'user': user,
            #     'otp' : otp,
            #     'url' : "https://www.flipkart.com"
            # })
    else:
        return redirect('/user/login/')


def welcome(request):
    return render(request, 'user/welcome.html')

def consent(request):
    return render(request, 'user/consent.html')