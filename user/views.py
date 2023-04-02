import datetime
import json
from dataclasses import dataclass
from email.policy import default
from logging import exception
from random import shuffle
from sqlite3 import IntegrityError, OperationalError

import environ
import pytz
import shortuuid
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db import IntegrityError, OperationalError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views import generic
from verify_email.email_handler import send_verification_email

import user
from user.models import codes

env = environ.Env()

def index(request):
    return HttpResponse("this is the index page")

def instructions(request):
    return render(request, 'user/instructions.html')

def user_init(user):
    user.participant.sessions_completed = 0
    user.save()

def user_new_visit(user, ref):
    user.participant.sessions_completed += 1
    t = timezone.now()
    user.participant.last_visit = t
    ob = codes.objects.create(otp=shortuuid.ShortUUID().random(length=12), session_num=user.participant.sessions_completed, ref=ref)
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
            try: 
                user.participant.ref = request.session['ref']
            except KeyError:
                user.participant.ref = 'keyError'
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
        entered_age = request.POST['age']
        # user = User.objects.create_user(entered_username, entered_email, entered_pwd)
    except:
        return render(request, 'user/registration.html', context={'err_msg': ''})
    else:
        # if(int(entered_age)<int(env('AGE_CUTOFF'))):
        if(int(entered_age) < 18):
            return render(request, 'user/registration.html', context={'err_msg': "Sorry, you must be at least " + env('AGE_CUTOFF') + " years old to continue."})
        verification_code = shortuuid.ShortUUID(alphabet="0123456789").random(length=4)
        msg = "Please enter the following OTP to verify your email: " + str(verification_code)
        send_mail('Verify your email address for participation.',
            msg,
            str(env('SMTP_MAIL')),
            [entered_email],
            fail_silently=True)
        try: 
            user = User.objects.create_user(entered_username, entered_email, entered_pwd)
        except IntegrityError:
            # template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            # message = template.format(type(ex).__name__, ex.args)
            # return HttpResponse(message)
            return render(request, 'user/registration.html', context={'err_msg': 'That username already exists! If you have already created an account, please log in instead.'})
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

def reset_pwd(request, got_name=0, verified=0):
    try:
        got_name = request.session['got_name']
    except KeyError:
        got_name = 0
    try:
        verified = request.session['verified']
    except KeyError:
        verified = 0
    try:
        forgot_username = request.session['forgot_username']
    except KeyError:
        forgot_username = ''

    if(got_name!=1 and verified!=1):
        try:
            entered_username = request.POST['username']
        except:
            return render(request, 'user/reset.html', context={'err_msg': '', 'verified': 0, 'got_name': 0})
        else:
            verification_code = shortuuid.ShortUUID(alphabet="0123456789").random(length=4)
            request.session['verif_code'] = verification_code
            msg = "Please enter the following OTP to verify your email: " + str(verification_code)
            forgot_user = get_object_or_404(User, username=entered_username)

            if forgot_user is not None:
                request.session['forgot_username'] = entered_username
                send_mail('Verify your email address for password reset.',
                    msg,
                    str(env('SMTP_MAIL')),
                    [forgot_user.email],
                    fail_silently=True)
                request.session['got_name'] = 1
                request.session['verified'] = 0
                return render(request, 'user/reset.html', context={'err_msg': "OK, mail has been sent to " + str(forgot_user.email) + "!", 'verified': 0, 'got_name': 1})
                # reset_pwd(request, 1, 0)
            else: 
                del request.session['forgot_username']
                del request.session['got_name']
                del request.session['verified']
                return HttpResponse('Error. Try again: ' + '<a href="/user/reset"}>Reset.</a>')
    
    elif(got_name==1 and verified!=1):
        try:
            entered_code = request.POST['code']
        except:
            return render(request, 'user/reset.html', context={'err_msg': 'Please enter the code.', 'verified': 0, 'got_name': 1})
        else:
            if entered_code == request.session['verif_code']:
                del request.session['verif_code']
                request.session['got_name'] = 1
                request.session['verified'] = 1
                return render(request, 'user/reset.html', context={'err_msg': '', 'verified': 1, 'got_name': 1})
                # reset_pwd(request, 1, 1)
            else:
                del request.session['forgot_username']
                del request.session['got_name']
                del request.session['verified']
                return HttpResponse('Error verifying. Try again: ' + '<a href="/user/reset"}>Reset.</a>')

    elif(got_name==1 and verified==1):
        try:
            entered_pwd = request.POST['password']
            confirm_pwd = request.POST['confirm_password']
        except:
            return render(request, 'user/reset.html', context={'err_msg': 'Please enter your new password.', 'verified': 1, 'got_name': 1})
        else:
            if entered_pwd == confirm_pwd:
                forgot_user = get_object_or_404(User, username=request.session['forgot_username'])
                forgot_user.set_password(entered_pwd)
                forgot_user.save()
                del request.session['forgot_username']
                del request.session['got_name']
                del request.session['verified']
                return HttpResponse("Hurray! Your password is reset! Click here to log in: " + "<a href='/user/login'}>Login.</a>")
            else:
                return render(request, 'user/reset.html', context={'err_msg': 'Passwords do not match.', 'verified': 1, 'got_name': 1})

def signin(request):
    # if env('MAINTENANCE_MODE') == 1:
    #     return HttpResponse('This website is now in maintenance mode.')
    try:
        entered_username = request.POST['username']
        # entered_email = request.POST['email']
        entered_pwd = request.POST['password']
    except:
        return render(request, 'user/login.html', context={'err_msg': ''})
    else:
        try:
            user = authenticate(request, username=entered_username, password=entered_pwd)
        except OperationalError:
            return render(request, 'user/login.html', context={
                'err_msg': 'There seems to be an error. Have you tried registering first?',
                'maintenance': ''
                })
        if user is not None:
            login(request, user=user)
            return HttpResponseRedirect('/user/home')
        else:
            return render(request, 'user/login.html', context={
                'err_msg': 'Incorrect password, please try again.',
                'maintenance': ''
                })

def signout(request):
    logout(request)
    return redirect('/user/login/')

def home(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('adminDash:adminDash')
    try:
        err_msg = request.session['proceed_err']
        del request.session['proceed_err']
    except KeyError:
        err_msg = ''
    if request.user.is_authenticated:
        if request.user.participant.is_verified:
            user = request.user
            sess_completed = user.participant.sessions_completed
            progress_percentage = sess_completed / 6 * 100
            leftnum = sess_completed - 3 if sess_completed > 3 else 0
            rightnum = sess_completed if sess_completed < 3 else 3
            rem_time = user.participant.last_visit.replace(microsecond=0) + datetime.timedelta(days=13,hours=20) - timezone.now().replace(microsecond=0)
            # rem_time = rem_time.replace(microsecond=0)
            # if(rem_time <= datetime.timedelta()):
            #     rem_time = datetime.timedelta()
            amounts = [0,100,400,600,800,1000,1200]
            last_vis = user.participant.last_visit
            over_time = last_vis.replace(microsecond=0) + datetime.timedelta(days=20,hours=4) - timezone.now().replace(microsecond=0)
            if(over_time < datetime.timedelta() and sess_completed != 0):
                time_until_next = "N/A"
            elif(rem_time > datetime.timedelta()):
                days, seconds = rem_time.days, rem_time.seconds
                hours = (seconds // 3600)
                minutes = (seconds % 3600) // 60
                seconds = seconds % 60
                time_until_next = str(days) + " days, " + str(hours) + " hours, and " + str(minutes) + " minutes"
                # time_until_next = rem_time
            else:
                time_until_next = datetime.timedelta()
                days, seconds = time_until_next.days, time_until_next.seconds
                hours = (seconds // 3600)
                minutes = (seconds % 3600) // 60
                seconds = seconds % 60
                time_until_next = str(days) + " days, " + str(hours) + " hours, and " + str(minutes) + " minutes"
                if sess_completed == 0: 
                    last_vis = "Never"
            return render(request,
                        'user/dashboard.html',
                        context={
                            'user': user,
                            'percentage': int(progress_percentage),
                            'leftnum': leftnum,
                            'rightnum': rightnum,
                            'earned': amounts[sess_completed],
                            'remtime': time_until_next,
                            'err_msg': err_msg,
                            'last_vis': last_vis,
                            'colorTested': user.participant.is_colorTested
                        })
        else:
            return HttpResponse("There seems to be something wrong with your registration. Please register using a different email or contact us via email at vivek.pamnani@research.iiit.ac.in")
    else:
        return redirect('/user/login')

def directions(request):
    if request.user.is_authenticated and request.user.participant.is_verified:
        user = request.user
        last_vis = user.participant.last_visit
        sess_completed = user.participant.sessions_completed
        rem_time = last_vis.replace(microsecond=0) + datetime.timedelta(days=13,hours=20) - timezone.now().replace(microsecond=0)
        over_time = last_vis.replace(microsecond=0) + datetime.timedelta(days=20,hours=4) - timezone.now().replace(microsecond=0)
        if(user.participant.is_colorBlind):
            request.session['proceed_err'] = str("It seems that either you have not taken the color test or you were detected as color blind. \n If you haven't, a 'Color Test' button should appear below for you to take the test.")
            return redirect('/user/home')
        if(over_time < datetime.timedelta() and sess_completed != 0):
            request.session['proceed_err'] = str("Sorry, it has been more than 20 days since your last visit. You can no longer participate in this study.\nThank you for your contribution to science!")
            # return HttpResponse("Sorry you would have to wait %s until your next attempt." % rem_time)
            return redirect('/user/home')
        elif(rem_time > datetime.timedelta()):
            request.session['proceed_err'] = str("Sorry, you will have to wait %s until your next session." % rem_time)
            # return HttpResponse("Sorry you would have to wait %s until your next attempt." % rem_time)
            return redirect('/user/home')
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
        windback = timezone.now() - datetime.timedelta(days=13,hours=20)
        last_time = old#.replace(tzinfo=utc)
        wind_time = windback#.replace(tzinfo=utc)
        rem_time = last_time + datetime.timedelta(days=13,hours=20) - timezone.now()
        if(rem_time > datetime.timedelta()):
            return HttpResponse('Sorry, you cannot attempt the experiment more than once in two weeks. Time until next attempt: %s' % rem_time)
        else:
            if user.participant.sessions_completed < 6:
                ref = user.participant.ref
                otp = user_new_visit(user, ref)
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
                'url' : "https://www.psytoolkit.org/c/3.4.2/survey?s=fpcam"
            })
        elif(user.participant.sessions_completed==2):
            return render(request, 'user/attempt.html', {
                'user': user,
                'otp' : otp,
                'url' : "https://www.psytoolkit.org/c/3.4.2/survey?s=W6bf8"
            })

        elif(user.participant.sessions_completed==3):
            return render(request, 'user/attempt.html', {
                'user': user,
                'otp' : otp,
                'url' : "https://www.psytoolkit.org/c/3.4.2/survey?s=uBY8M"
            })

        elif(user.participant.sessions_completed==4):
            return render(request, 'user/attempt.html', {
                'user': user,
                'otp' : otp,
                'url' : "https://www.psytoolkit.org/c/3.4.2/survey?s=jeph9"
            })

        elif(user.participant.sessions_completed==5):
            return render(request, 'user/attempt.html', {
                'user': user,
                'otp' : otp,
                'url' : "https://www.psytoolkit.org/c/3.4.2/survey?s=gZxRf"
            })

        elif(user.participant.sessions_completed==6):
            return render(request, 'user/attempt.html', {
                'user': user,
                'otp' : otp,
                'url' : "https://www.psytoolkit.org/c/3.4.2/survey?s=e4STN"
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
    if request.method == "GET":
        ref = request.GET.get('ref', '')
        if ref == '':
            ref = 'noref'
        request.session['ref'] = ref

    elif request.method == "POST":
        try:
            entered_email = request.POST['email']
        except:
            return HttpResponse("There was an issue processing the entered email. Are you sure you entered correctly?" + '<a href="/user/welcome"}>Try again.</a>')
        else: 
            try:
                ref = request.session['ref']
            except KeyError:
                ref = 'err'
            msg_greet = "Hi " + entered_email.split('@')[0] + "! <br><br> Thank you for showing an interest in our research. You have received this email because you opted for it on our welcome page. To know more about the study, simply click the link below. "
            msg_link = "Here is the link to participate in the study: https://www.imwbs.org/user/welcome/?ref=" + ref
            msg_req = "Please note that the study requires you to have a laptop/desktop with a physical keyboard. iPads will not work."
            auto_note = '<br><br>Note that this is an automated email message. Please do not reply.'
            send_mail('[Indian Mental Wellbeing Study] Link for participation',
                '',
                str(env('SMTP_MAIL')),
                [entered_email],
                html_message=msg_greet + "<br>" + msg_link + "<br><br>" + msg_req + "<br><br>" + auto_note,
                fail_silently=True)
                
    return render(request, 'user/welcome.html')

def consent(request):
    return render(request, 'user/consent.html')

def ishihara(request):
    # don't allow if not registered
    if not (request.user.is_authenticated and request.user.participant.is_verified):
        return redirect('/user/login')

    # don't allow if already given
    if request.user.participant.is_colorTested:
        return redirect('/user/home')

    protan_images = [
        '5_protan',
        '7_protan', 
        '8_protan'
    ]
    deuteran_images = [
        '2_deuteran',
        '8_deuteran', 
        '9_deuteran'
    ]
    tritan_images = [
        '3_tritan_2',
        '7_tritan', 
        '8_tritan'
    ]
    images = protan_images + deuteran_images + tritan_images
    shuffle(images)
    image_row_tuples = [images[i:i+3] for i in range(0, len(images), 3)]

    protan_scores = [0] * len(protan_images)
    deuteran_scores = [0] * len(deuteran_images)
    tritan_scores = [0] * len(tritan_images)
    score = 0

    if request.method == 'POST':
        try:
            protan_scores = [int(int(request.POST[img])==int(img[0])) for img in protan_images]
            deuteran_scores = [int(int(request.POST[img])==int(img[0])) for img in deuteran_images]
            tritan_scores = [int(int(request.POST[img])==int(img[0])) for img in tritan_images]
        except:
            return HttpResponse('There was an error processing your request. ' + str(type(protan_scores[0])))
        else:
            score = sum(protan_scores + deuteran_scores + tritan_scores)

        if score <= 7:
            request.user.participant.is_colorBlind = True
        else:
            request.user.participant.is_colorBlind = False

        request.user.participant.is_colorTested = True
        request.user.save()
        return redirect('/user/home')

    return render(request, 'user/ishihara.html', context={
        'score': score, 
        'image_row_tuples': image_row_tuples, 
        })