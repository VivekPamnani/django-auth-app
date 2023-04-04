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
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_login_failed
from django.core.mail import send_mail
from django.db import IntegrityError, OperationalError
from django.dispatch import receiver
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views import generic
from verify_email.email_handler import send_verification_email

from user.models import codes, participant, waitlist
from configSolo.models import SiteConfiguration as siteConfig

env = environ.Env()
MAX_SESSIONS = settings.USER_MAX_SESSIONS
SESSION_INTERVAL_DAYS = settings.USER_SESSION_INTERVAL_DAYS
SESSION_INTERVAL_DAYS_MAX = settings.USER_SESSION_INTERVAL_DAYS_MAX
SESSION_LINKS = settings.USER_SESSION_LINKS
SESSION_AMOUNTS = settings.USER_SESSION_AMOUNTS

def get_url(base_url, params: dict[str, str]):
    """
    f"{base_url}?{urlencode(params)}"
    """
    return f"{base_url}?{urlencode(params)}"

def long_or_single(func):
    @functools.wraps(func)
    def wrapper(request, template_path, *args, **kwargs):
        if request.user.is_authenticated is False or request.user.participant.longitudinal_enrollment_status != 1:
            tsplit = template_path.split('.')
            try:
                template_path = tsplit[0] + '_single.' + tsplit[1]
            except:
                pass
        return func(request, template_path, *args, **kwargs)
    return wrapper

crender = long_or_single(render)
"""
django.shortcuts.render with longitudinal enrollment status check. \\
Renders the appropriate template based on the user's longitudinal enrollment status. \\
Current logic is that if the user is not enrolled in the longitudinal study, the template is suffixed with '_single'.
"""


def index(request):
    return redirect('user:home')

def instructions(request):
    return crender(request, 'user/instructions.html')

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
                
    return crender(request, 'user/welcome.html')

def consent(request):
    return crender(request, 'user/consent.html')

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
            print("Error reading ALLOWED_EMAILS from .env file.")
        if(count_existing > 0 and entered_email not in allowed_emails):
            return render(request, 'user/registration.html', context={'err_msg': 'That email already exists! If you have already created an account, please log in instead.'})
        
        # * Create user if username does not exist, else return error
        try: 
            user = User.objects.create_user(entered_username, entered_email, entered_pwd)
            # * If email is in allowed_emails, automatically verify and log in (for testing purposes).
            if entered_email in allowed_emails:
                user.participant.is_verified = True
                user.save()
                login(request, user=user)
                return redirect('user:home')
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

@receiver(user_login_failed)
def user_login_failed_callback(sender, credentials, request, **kwargs):
    try:
        user = User.objects.get(username=credentials['username'])
    except User.DoesNotExist:
        pass
    else:
        if user.is_active is False:
            request.session['long_reject_login_attempted'] = True

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
            if request.session.get('long_reject_login_attempted', False):
                del request.session['long_reject_login_attempted']
                return redirect(f'{reverse("user:error")}?err=long-reject')

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
    class message:
        """
        A class to store error messages.
        """
        def __init__(self, code='', msg='', title='', type='negative'):
            self.code = code
            self.msg = msg
            self.title = title
            self.type = type

        def __str__(self):
            return self.msg

        def to_dict(self) -> dict:
            return {
                'code': self.code,
                'msg': self.msg,
                'title': self.title,
                'type': self.type,
            }

        def to_template_context(self) -> dict:
            type_color = {
                'negative': '#EF4444',
                'positive': '#047857',
            }
            return {
                'code': self.code,
                'msg': self.msg,
                'title': self.title,
                'title_color': type_color[self.type],
            }
    
    # * Read error messages from messages.json
    messages = {k: v for (k, v) in json.load(open('user/messages.json', 'r'), object_hook=lambda d:
        (d['code'], message(**d).to_template_context())
    )}

    # * Get the error code from the request.
    try:
        if request.method == "GET":
            params = request.GET
    except:
        return redirect(f'{reverse("user:error")}?err=unknown')
    
    err = params.get('err', '')


    # * Get the error message.
    try:
        err_context = messages[err]
    except KeyError:
        err_context = messages['unknown']

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

def screen_logic(request, is_eligible: int = 0) -> tuple[bool, str]:
    try:
        entered_age = int(request.POST['age'])
        speak_english = int(request.POST['english'])
        infHistory = request.POST.getlist('infHistory', [])
        covid_symptoms = int(request.POST['covid_symptoms'])
        print(f"infHistory: {infHistory}")
    except:
        raise ValueError('Invalid input.')
        return render(request, 'user/screen.html', context={'err_msg': '', 'eligible': is_eligible})
    else:
        checks: dict[str, bool] = {
            'age': False,
            'english': False,
            # 'covid_test': False,
            'infHistory': False, 
            'covid_symptoms': False,
        }

        if entered_age >= 18 and entered_age <= 60:
            checks['age'] = True
        if speak_english == 1:
            checks['english'] = True
        # if covid_test == 1:
        #     checks['covid_test'] = True
        if covid_symptoms == 1:
            checks['covid_symptoms'] = True
        if 'covid' in infHistory:  
            checks['infHistory'] = True

        if not checks['age'] or not checks['english']:
            return False, 'ineligible'
        
        config = siteConfig.objects.get()
        max_control_count = config.current_target * config.control_ratio
        max_covid_count = config.current_target * (1 - config.control_ratio)

        print(checks)
        
        if checks['infHistory'] and checks['covid_symptoms']:
            if config.covid_count < max_covid_count:
                config.covid_count += 1
                config.save()
            else:
                waitlist.objects.create(user=request.user, covid_history=True, age=entered_age)
                return False, 'waitlist'
        else:
            if config.control_count < max_control_count:
                config.control_count += 1
                config.save()
            else:
                waitlist.objects.create(user=request.user, covid_history=False, age=entered_age)
                return False, 'waitlist'

        return True, 'eligible'

        # if sum(checks.values()) == len(checks): 
        #     return True, 'eligible'
        # else:
        #     return False, 'ineligible'

@screening_required_decorator(colorBlind=False, eligible=False)
def screen(request):

    def generate_infTable_content():
        infections = [
            ('influenza', 'Influenza (flu)'),
            ('pneumonia', 'Pneumonia'),
            ('ecoli', 'E. Coli'),
            ('covid', 'COVID-19'),
            ('malaria', 'Malaria'),
            ('cholera', 'Cholera'),
            ('cold', 'Common Cold'),
            ('tb', 'Tuberculosis (TB)'),
        ]
        cols = 2
        rows = len(infections) // cols
        infTable = []
        for i in range(rows):
            infTable.append(infections[i*cols:(i+1)*cols])
        return infTable

    # * If the user is already eligible, redirect to home page.
    if request.user.participant.is_eligible == 1:
        return redirect('user:home')

    # * If the user is already on the waitlist, redirect to error page.
    try:
        waitlist.objects.get(user=request.user)
    except waitlist.DoesNotExist:
        pass
    else:
        return redirect(f"{reverse('user:error')}?err=waitlist")
    
    try:
        valid, report = screen_logic(request, is_eligible=request.user.participant.is_eligible)
    except ValueError:
        return render(request, 'user/screen.html', context={'err_msg': '', 'eligible': request.user.participant.is_eligible, 'infTable': generate_infTable_content()})
    
    if valid is True:
        request.user.participant.is_eligible = 1
        request.user.participant.save()
        return redirect('user:home')
    else:
        request.user.participant.is_eligible = 2
        request.user.participant.save()
        if report == 'waitlist':
            return redirect(f"{reverse('user:error')}?err=waitlist")
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

def stringify_remaining_time(remaining_time):
    days, seconds = remaining_time.days, remaining_time.seconds
    hours = (seconds // 3600)
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{days} days, {hours} hours, and {minutes} minutes"

def get_time_until_next_session(last_visit_time, sess_completed) -> str:
    time_until_next = ""
    rem_time = last_visit_time.replace(microsecond=0) + datetime.timedelta(days=SESSION_INTERVAL_DAYS-1,hours=20) - timezone.now().replace(microsecond=0)
    over_time = last_visit_time.replace(microsecond=0) + datetime.timedelta(days=SESSION_INTERVAL_DAYS_MAX-1,hours=4) - timezone.now().replace(microsecond=0)


    if sess_completed == 0:
        last_visit_time = "Never"
    else:
        # Show the last visit time in a more nautural language
        last_visit_time = last_visit_time.strftime("%A, %B %d, %Y at %I:%M %p")

    if(sess_completed == MAX_SESSIONS):
        time_until_next = "N/A" 
    elif(over_time < datetime.timedelta() and sess_completed != 0):
        time_until_next = f"Ineligible (over {SESSION_INTERVAL_DAYS_MAX} days since last session)"
    elif(rem_time > datetime.timedelta()):
        time_until_next = stringify_remaining_time(rem_time)
    else:
        time_until_next = "Now!"
    return time_until_next, last_visit_time

def home(request):
    if request.user.is_authenticated is False:
        return redirect('user:login')

    if request.user.is_superuser is True:
        return redirect('adminDash:adminDash')

    if request.user.participant.is_verified is False:
        return redirect(f"{reverse('user:error')}?err=not-verified")
    
    if request.user.participant.sessions_completed > 0 and request.user.participant.is_eligible != 1:
        request.user.participant.is_eligible = 1
        request.user.participant.save()

    if request.user.participant.is_eligible != 1:
        return redirect('user:screen')

    if request.user.participant.is_colorTested is False:
        return redirect('user:ishihara')
    else:
        if request.user.participant.is_colorBlind is True:
            return redirect(f"{reverse('user:error')}?err=colorblind")

    if request.user.participant.sessions_completed == 1 and request.user.participant.longitudinal_enrollment_status == 0:
        return redirect('user:long_proposal')
    
    if request.user.participant.sessions_completed > 1 and request.user.participant.longitudinal_enrollment_status != 1:
        request.user.participant.longitudinal_enrollment_status = 1
        request.user.participant.save()

    try:
        err_msg = request.session['proceed_err']
        del request.session['proceed_err']
    except KeyError:
        err_msg = ''
    
    user = request.user

    # * Get the user's progress percentage.
    sess_completed = user.participant.sessions_completed
    progress_percentage = sess_completed / MAX_SESSIONS * 100
    leftnum = sess_completed - int(MAX_SESSIONS/2) if sess_completed > int(MAX_SESSIONS/2) else 0
    rightnum = sess_completed if sess_completed < int(MAX_SESSIONS/2) else int(MAX_SESSIONS/2)

    earned = 0
    for i in range(1, sess_completed+1):
        earned += SESSION_AMOUNTS[i]
        

    # * Get the time until the next session.
    time_until_next, last_visit_time = get_time_until_next_session(user.participant.last_visit, sess_completed)
    
    return crender(request,
        'user/dashboard.html',
        context={
            'user': user,
            'completed': sess_completed,
            'percentage': int(progress_percentage),
            'leftnum': leftnum,
            'rightnum': rightnum,
            'earned': earned,
            'MAX_SESSIONS': MAX_SESSIONS,
            'MAX_AMOUNT': sum(SESSION_AMOUNTS),
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
    rem_time = last_vis.replace(microsecond=0) + datetime.timedelta(days=SESSION_INTERVAL_DAYS-1,hours=20) - timezone.now().replace(microsecond=0)
    over_time = last_vis.replace(microsecond=0) + datetime.timedelta(days=SESSION_INTERVAL_DAYS_MAX-1,hours=4) - timezone.now().replace(microsecond=0)
    # if(user.participant.is_colorBlind):
    #     request.session['proceed_err'] = str("It seems that either you have not taken the color test or you were detected as color blind. \n If you haven't, a 'Color Test' button should appear below for you to take the test.")
    #     return redirect('user:home')
    if(over_time < datetime.timedelta() and sess_completed != 0):
        request.session['proceed_err'] = f"Sorry, it has been more than {SESSION_INTERVAL_DAYS_MAX} days since your last visit. You can no longer participate in this study.\nThank you for your contribution to science!"
        # return HttpResponse("Sorry you would have to wait %s until your next attempt." % rem_time)
        return redirect('user:home')
    elif(rem_time > datetime.timedelta()):
        request.session['proceed_err'] = f"Please wait {stringify_remaining_time(rem_time)} until your next session."
        # return HttpResponse("Sorry you would have to wait %s until your next attempt." % rem_time)
        return redirect('user:home')
    else:
        if user.participant.sessions_completed == MAX_SESSIONS:
            return redirect(f"{reverse('user:error')}?err=completed-all")
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
    windback = timezone.now() - datetime.timedelta(days=SESSION_INTERVAL_DAYS-1,hours=20)
    last_time = old#.replace(tzinfo=utc)
    wind_time = windback#.replace(tzinfo=utc)
    rem_time = last_time + datetime.timedelta(days=SESSION_INTERVAL_DAYS-1,hours=20) - timezone.now()
    if(rem_time > datetime.timedelta()):
        wait_time = stringify_remaining_time(rem_time)
        return redirect(f"{reverse('user:error')}?err=too-soon&rem_time={wait_time}")
    else:
        if user.participant.sessions_completed < MAX_SESSIONS:
            ref = user.participant.ref
            otp = user_new_visit(user, ref)
            if request.method == "GET":
                return redirect(reverse('user:visit_success', args=(), kwargs={'otp': otp}))
        else:
            return redirect(f"{reverse('user:error')}?err=completed-all")

@screening_required_decorator()
def visit_success(request, otp):
    user = request.user
    try:
        return render(request, 'user/attempt.html', context={
            'user': user,
            'otp' : otp,
            'url' : SESSION_LINKS[user.participant.sessions_completed]
        })
    except:
        return redirect(f"{reverse('user:error')}?err=visit-error")

@screening_required_decorator()
def long_proposal(request):
    if request.user.participant.sessions_completed == 0:
        return redirect('user:home')

    user = request.user
    try:
        if 'signup' in request.POST:
            user.participant.longitudinal_enrollment_status = 1
            user.save()
            return redirect(f"{reverse('user:error')}?err=long-signup")
        elif 'reject' in request.POST:
            user.participant.longitudinal_enrollment_status = 2
            user.is_active = False
            user.save()
            logout(request)
            return redirect(f"{reverse('user:error')}?err=long-reject")
        else:
            raise Exception("Invalid form submission.")
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