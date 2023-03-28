import datetime
import functools
import json
from dataclasses import dataclass
from email.policy import default
from logging import exception
from random import shuffle
from sqlite3 import IntegrityError, OperationalError
from urllib.parse import urlencode

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

def get_url(base_url, params: dict[str, str]):
    """
    f"{base_url}?{urlencode(params)}"
    """
    return f"{base_url}?{urlencode(params)}"

def index(request):
    return redirect('user:home')

def instructions(request):
    return render(request, 'user/instructions_single.html')

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
            return redirect(f"{reverse('user:error')}?err=verif-success")
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
        # * Check if age is above cutoff
        # if(int(entered_age)<int(env('AGE_CUTOFF'))):
        if(int(entered_age) < 18):
            return render(request, 'user/registration.html', context={'err_msg': "Sorry, you must be at least " + env('AGE_CUTOFF') + " years old to continue."})

        # * Check if email already exists
        count_existing = User.objects.filter(email=entered_email).count()
        try:
            allowed_emails = env('ALLOWED_EMAILS').split(',')
        except:
            allowed_emails = []
            print("Error")
        print(allowed_emails)
        if(count_existing > 0 and entered_email not in allowed_emails):
            return render(request, 'user/registration.html', context={'err_msg': 'That email already exists! If you have already created an account, please log in instead.'})
        
        # * Create user if username does not exist, else return error
        try: 
            user = User.objects.create_user(entered_username, entered_email, entered_pwd)
        except IntegrityError:
            # template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            # message = template.format(type(ex).__name__, ex.args)
            # return HttpResponse(message)
            return render(request, 'user/registration.html', context={'err_msg': 'That username already exists! If you have already created an account, please log in instead.'})


        verification_code = shortuuid.ShortUUID(alphabet="0123456789").random(length=4)
        msg = "Please enter the following OTP to verify your email: " + str(verification_code)
        send_mail('Verify your email address for participation.',
            msg,
            str(env('SMTP_MAIL')),
            [entered_email],
            fail_silently=True)
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

def forgot_username(request):
    try:
        entered_email = request.POST['email']
    except:
        return render(request, 'user/forgot_name.html', context={'err_msg': ''})
    else:
        multiple_found = False
        try:
            user = User.objects.get(email=entered_email)
        except User.DoesNotExist:
            return render(request, 'user/forgot_name.html', context={'err_msg': 'No user with that email exists!'})
        except User.MultipleObjectsReturned:
            multiple_found = True
            matching_users = User.objects.filter(email=entered_email)
        finally:
            if multiple_found is False:
                msg = "Your username is: " + user.username
            else:
                msg = "Multiple users with that email exist. The associated usernames are: \n"
                for u in matching_users:
                    msg += u.username + "\n"
            send_mail('Your username for the study.',
                msg,
                str(env('SMTP_MAIL')),
                [entered_email],
                fail_silently=True)
            return redirect(f'{reverse("user:error")}?err=uname-sent')
            return HttpResponse("Your username has been sent to your email address. Click here to proceed to the login page: " + '<a href="/user/login">Login</a>')


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
                return redirect(f"{reverse('user:error')}?err=pwd-reset-success")
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
            return redirect('user:home')
        else:
            return render(request, 'user/login.html', context={
                'err_msg': 'Incorrect username or password, please try again.',
                'maintenance': ''
                })

def signout(request):
    logout(request)
    return redirect('user:login')

def screening_required_decorator(colorBlind=True, eligible=True):
    def screening_required(func):
        @functools.wraps(func)
        def wrapper(request, *args, **kwargs):
            # ! A check failing means that the corresponding variable is True.
            # print("Calling function " + func.__name__ + " with screening checks.")
            # if colorBlind is True:
            #     print("\tColorblindness check is enabled...")
            # if eligible is True:
            #     print("\tEligibility check is enabled...")

            check_login = request.user.is_authenticated is False or request.user.participant.is_verified is False
            if check_login is False:
                check_colorBlind = colorBlind and request.user.participant.is_colorBlind is True
                check_eligible = eligible and request.user.participant.is_eligible != 1
            else:
                # * If the user is not logged in, then further checks are irrelevant.
                check_colorBlind = True
                check_eligible = True
            
            # print("\tCheck login: " + str(check_login))
            # if colorBlind is True:
            #     print("\tCheck colorblindness: " + str(check_colorBlind))
            # if eligible is True:
            #     print("\tCheck eligibility: " + str(check_eligible))
            
            # * If any of the checks fail, redirect to home page. The home page will redirect to the appropriate page.
            if check_login or check_colorBlind or check_eligible:
                # print("Check failed. Redirecting to home page.")
                return redirect('user:home')
            # print("Check passed. Proceeding to function " + func.__name__ + ".")
            return func(request, *args, **kwargs)
        return wrapper
    return screening_required
    

def error(request):
    try:
        if request.method == "GET":
            params = request.GET
    except:
        return redirect('/user/msg/?err=unknown')
    err = params.get('err', '')
    rem_time = params.get('rem_time', '')
    type = 'negative'
    title_color = {
        'negative': '#EF4444',
        'positive': '#047857',
    }

    err_context = {
        'msg': '',
        'title': '',
        'title_color': '',
    }

    if err == 'not-eligible':
        err_context['msg'] = 'You are not eligible to participate in this study.'
    elif err == 'not-verified':
        err_context['msg'] = 'There seems to be something wrong with your registration. Please register using a different email or contact us.'
    elif err == 'too-soon':
        err_context['msg'] = 'You cannot attempt the experiment more than once in two weeks. Please wait ' + str(rem_time) + ' before you can participate again.'
    elif err == 'colorblind':
        err_context['msg'] = 'You seem to be color blind. Please contact us if you would like to participate in this study.'
    elif err == 'verif-success':
        err_context['msg'] = f'Your account has been verified! Click the button below to proceed to the instructions: <p><a class="btn btn-primary" style="width: 25%; min-width: 200px;" href={redirect_url}>Continue.</a></p>'
        err_context['title'] = 'Success!'
        err_context['title_color'] = title_color['positive']
        redirect_url = reverse('user:instructions')
    elif err == 'pwd-reset-success':
        err_context['msg'] = f'Your password has been reset! Click the button below to proceed to the login page: <p><a class="btn btn-primary" style="width: 25%; min-width: 200px;" href={redirect_url}>Continue.</a></p>'
        err_context['title'] = 'Hurray!'
        err_context['title_color'] = title_color['positive']
        redirect_url = reverse('user:login')
    elif err == 'uname-sent':
        err_context['msg'] = f'Your username has been sent to your email! Click the button below to proceed to the login page: <p><a class="btn btn-primary" style="width: 25%; min-width: 200px;" href={redirect_url}>Login</a></p>'
        err_context['title'] = 'Username sent!'
        err_context['title_color'] = title_color['positive']
        redirect_url = reverse('user:login')
    elif err == 'long-signup':
        err_context['msg'] = f"Thank you for your interest in our study. We will contact you shortly. Meanwhile, you can click the button below to return to the home page: <p><a class='btn btn-primary' style='width: 25%; min-width: 200px;' href={redirect_url}>Return to home page</a></p>"
        err_context['title'] = 'Thank you for your interest!'
        err_context['title_color'] = title_color['positive']
        redirect_url = reverse('user:home')
    elif err == 'long-reject':
        err_context['msg'] = f"Thank you for you participation. You will not be contacted for the follow-up study. You may now close this tab."
        err_context['title'] = 'Thank you for your participation!'
        err_context['title_color'] = title_color['positive']

        
    else:
        err_context['msg'] = 'An error has occurred. Please try again.'
    
    return render(request, 'user/error.html', context=err_context)

def deprecated_screen(request):
    # * If the user is already eligible, redirect to home page.
    if request.user.participant.is_eligible == 1:
        return redirect('user:home')
    
    try:
        entered_age = int(request.POST['age'])
        speak_english = int(request.POST['english'])
        covid_test = int(request.POST['covid_test'])
        covid_symptoms = int(request.POST['covid_symptoms'])
    except:
        return render(request, 'user/screen.html', context={'err_msg': '', 'eligible': request.user.participant.is_eligible})
    else:
        checks: dict[str, bool] = {
            'age': False,
            'english': False,
            'covid_test': False,
            'covid_symptoms': False
        }

        if entered_age >= 18 and entered_age <= 60:
            checks['age'] = True
        if speak_english == 1:
            checks['english'] = True
        if covid_test == 1:
            checks['covid_test'] = True
        if covid_symptoms == 1:
            checks['covid_symptoms'] = True

        if sum(checks.values()) == len(checks):
            request.user.participant.is_eligible = 1
            request.user.participant.save()
            return redirect('user:home')
        else:
            request.user.participant.is_eligible = 2
            request.user.participant.save()
            return render(request, 'user/screen.html', context={'err_msg': '', 'eligible': request.user.participant.is_eligible})

def screen_logic(request, is_eligible: int = 0):
    try:
        entered_age = int(request.POST['age'])
        speak_english = int(request.POST['english'])
        covid_test = int(request.POST['covid_test'])
        covid_symptoms = int(request.POST['covid_symptoms'])
    except:
        raise ValueError('Invalid input.')
        return render(request, 'user/screen.html', context={'err_msg': '', 'eligible': is_eligible})
    else:
        checks: dict[str, bool] = {
            'age': False,
            'english': False,
            'covid_test': False,
            'covid_symptoms': False
        }

        if entered_age >= 18 and entered_age <= 60:
            checks['age'] = True
        if speak_english == 1:
            checks['english'] = True
        if covid_test == 1:
            checks['covid_test'] = True
        if covid_symptoms == 1:
            checks['covid_symptoms'] = True

        if sum(checks.values()) == len(checks):
            return True
        else:
            return False

@screening_required_decorator(colorBlind=False, eligible=False)
def screen(request):
    # * If the user is already eligible, redirect to home page.
    if request.user.participant.is_eligible == 1:
        return redirect('user:home')
    
    try:
        valid = screen_logic(request, is_eligible=request.user.participant.is_eligible)
    except ValueError:
        return render(request, 'user/screen.html', context={'err_msg': '', 'eligible': request.user.participant.is_eligible})

    if valid is True:
        request.user.participant.is_eligible = 1
        request.user.participant.save()
        return redirect('user:home')
    else:
        request.user.participant.is_eligible = 2
        request.user.participant.save()
        return render(request, 'user/screen.html', context={'err_msg': '', 'eligible': request.user.participant.is_eligible})

def freescreen(request):
    """
    This function is used to screen participants independent of user accounts. 
    """
    is_eligible = request.session.get('free_is_eligible', 0)
    if is_eligible == 1:
        return HttpResponseRedirect('https://www.google.com/')
    try:
        valid = screen_logic(request)
    except ValueError:
        return render(request, 'user/screen.html', context={'err_msg': '', 'eligible': is_eligible, 'free': True})

    if valid is True:
        request.session['free_is_eligible'] = is_eligible = 1
        return HttpResponseRedirect('https://www.google.com/')
    else:
        request.session['free_is_eligible'] = is_eligible = 2
        return render(request, 'user/screen.html', context={'err_msg': '', 'eligible': is_eligible, 'free': True})

def get_time_until_next_session(last_visit_time, sess_completed) -> str:
    time_until_next = ""
    rem_time = last_visit_time.replace(microsecond=0) + datetime.timedelta(days=13,hours=20) - timezone.now().replace(microsecond=0)
    over_time = last_visit_time.replace(microsecond=0) + datetime.timedelta(days=20,hours=4) - timezone.now().replace(microsecond=0)

    if sess_completed == 0:
        last_visit_time = "Never"
    else:
        # Show the last visit time in a more nautural language
        last_visit_time = last_visit_time.strftime("%A, %B %d, %Y at %I:%M %p")

    if(over_time < datetime.timedelta() and sess_completed != 0):
        time_until_next = "N/A"
    elif(rem_time > datetime.timedelta()):
        days, seconds = rem_time.days, rem_time.seconds
        hours = (seconds // 3600)
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        time_until_next = str(days) + " days, " + str(hours) + " hours, and " + str(minutes) + " minutes"
    else:
        time_until_next = datetime.timedelta()
        days, seconds = time_until_next.days, time_until_next.seconds
        hours = (seconds // 3600)
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        time_until_next = str(days) + " days, " + str(hours) + " hours, and " + str(minutes) + " minutes"

    return time_until_next, last_visit_time

def home(request):
    # * If the user is not logged in, redirect to the login page.
    if request.user.is_authenticated is False:
        return redirect('user:login')

    # * If the user is not verified, redirect to the error page.
    if request.user.participant.is_verified is False:
        return redirect(f"{reverse('user:error')}?err=not-verified")
    
    # * If the user has completed at least 1 session previously, mark them as eligible.
    # if request.user.participant.last_visit.replace(tzinfo=None) > datetime.datetime(1001,1,1,0,0,0) and request.user.participant.is_eligible != 1:
    if request.user.participant.sessions_completed > 0 and request.user.participant.is_eligible != 1:
        request.user.participant.is_eligible = 1
        request.user.participant.save()

    # * If the user is not eligible, redirect to the screening page.
    if request.user.participant.is_eligible != 1:
        return redirect('user:screen')

    # * If the user has not completed the color test, redirect to the color test page.
    if request.user.participant.is_colorTested is False:
        return redirect('user:ishihara')
    else:
        # * If the user is colorblind, redirect to the error page.
        if request.user.participant.is_colorBlind is True:
            return redirect(f"{reverse('user:error')}?err=colorblind")

    try:
        err_msg = request.session['proceed_err']
        del request.session['proceed_err']
    except KeyError:
        err_msg = ''
    
    user = request.user

    # * Get the user's progress percentage.
    sess_completed = user.participant.sessions_completed
    progress_percentage = sess_completed / 6 * 100
    leftnum = sess_completed - 3 if sess_completed > 3 else 0
    rightnum = sess_completed if sess_completed < 3 else 3
    amounts = [0,100,400,600,800,1000,1200]

    # * Get the time until the next session.
    time_until_next, last_visit_time = get_time_until_next_session(user.participant.last_visit, sess_completed)
    
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
            'last_vis': last_visit_time,
            'colorTested': user.participant.is_colorTested
        }
    )

@screening_required_decorator()
def directions(request):
    user = request.user
    last_vis = user.participant.last_visit
    sess_completed = user.participant.sessions_completed
    rem_time = last_vis.replace(microsecond=0) + datetime.timedelta(days=13,hours=20) - timezone.now().replace(microsecond=0)
    over_time = last_vis.replace(microsecond=0) + datetime.timedelta(days=20,hours=4) - timezone.now().replace(microsecond=0)
    # if(user.participant.is_colorBlind):
    #     request.session['proceed_err'] = str("It seems that either you have not taken the color test or you were detected as color blind. \n If you haven't, a 'Color Test' button should appear below for you to take the test.")
    #     return redirect('user:home')
    if(over_time < datetime.timedelta() and sess_completed != 0):
        request.session['proceed_err'] = str("Sorry, it has been more than 20 days since your last visit. You can no longer participate in this study.\nThank you for your contribution to science!")
        # return HttpResponse("Sorry you would have to wait %s until your next attempt." % rem_time)
        return redirect('user:home')
    elif(rem_time > datetime.timedelta()):
        request.session['proceed_err'] = str("Sorry, you will have to wait %s until your next session." % rem_time)
        # return HttpResponse("Sorry you would have to wait %s until your next attempt." % rem_time)
        return redirect('user:home')
    else:
        return render(request, 'user/directions.html')

@screening_required_decorator()
def log_visit(request):
    # if request.user.is_authenticated is False or request.user.participant.is_verified is False:
    #     return redirect('/user/login/')
    
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
        wait_time = f"{rem_time.days} days, {rem_time.seconds//3600} hours, and {rem_time.seconds%3600//60} minutes"
        return redirect(f"{reverse('user:error')}?err=too-soon&rem_time={wait_time}")
    else:
        if user.participant.sessions_completed < 6:
            ref = user.participant.ref
            otp = user_new_visit(user, ref)
            if request.method == "GET":
                return redirect(reverse('user:visit_success', args=(), kwargs={'otp': otp}))
        else:
            return HttpResponse("You have completed all of your sessions and thus cannot attempt further tests. We thank you for your participation!")

@screening_required_decorator()
def visit_success(request, otp):
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
                
    return render(request, 'user/welcome_single.html')

def consent(request):
    return render(request, 'user/consent_single.html')

@screening_required_decorator()
def long_proposal(request):
    if request.user.participant.sessions_completed == 0:
        return redirect('user:home')

    long_signup = -1
    try:
        if request.method == 'POST':
            if 'signup' in request.POST:
                long_signup = 1
            elif 'reject' in request.POST:
                long_signup = 0
            else:
                raise Exception("Invalid form submission")
        
        if long_signup == 1:
            return redirect(f"{reverse('user:error')}?err=long-signup")
        elif long_signup == 0:
            return redirect(f"{reverse('user:error')}?err=long-reject")
        else:
            return render(request, 'user/long_proposal.html')
    except:
        return render(request, 'user/long_proposal.html')

@screening_required_decorator(eligible=True, colorBlind=False)
def ishihara(request):
    # don't allow if already given
    if request.user.participant.is_colorTested:
        return redirect('user:home')

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
        return redirect('user:home')

    return render(request, 'user/ishihara.html', context={
        'score': score, 
        'image_row_tuples': image_row_tuples, 
        })