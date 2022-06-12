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

def index(request):
    return HttpResponse("this is the index page")

def user_init(user):
    user.participant.sessions_completed = 0
    user.save()

def user_new_visit(user):
    user.participant.sessions_completed += 1
    t = timezone.now()
    user.participant.last_visit = t
    ob = codes.objects.create(otp=shortuuid.ShortUUID().random(length=12), session_num=user.participant.sessions_completed)
    match user.participant.sessions_completed:
        case 1:
            user.participant.visit_time_1 = t
        case 2:
            user.participant.visit_time_2 = t
        case 3:
            user.participant.visit_time_3 = t
        case 4:
            user.participant.visit_time_4 = t
        case 5:
            user.participant.visit_time_5 = t
        case 6:
            user.participant.visit_time_6 = t
        case default:
            return HttpResponse("Something went wrong.")
    user.save()
    return ob.otp

def register(request):
    try:
        entered_username = request.POST['username']
        entered_email = request.POST['email']
        entered_pwd = request.POST['password']
        # user = User.objects.create_user(entered_username, entered_email, entered_pwd)
    except:
        return render(request, 'user/registration.html')
    else:
        user = User.objects.create_user(entered_username, entered_email, entered_pwd)
        user.save()
        user_init(user)
    user = authenticate(request, username=entered_username, password=entered_pwd)
    if user is not None:
        login(request, user=user)
        return redirect("/user/home/")
    else:
        return HttpResponse("Something went wrong.")

def signin(request):
    try:
        entered_username = request.POST['username']
        # entered_email = request.POST['email']  
        entered_pwd = request.POST['password']
    except:
        return render(request, 'user/login.html')
    else:
        user = authenticate(request, username=entered_username, password=entered_pwd)
        if user is not None:
            login(request, user=user)
            return HttpResponseRedirect('/user/home')
        else:
            return HttpResponse("Invalid attempt.")

def signout(request):
    logout(request)
    return redirect('/user/login/')

def home(request):
    if request.user.is_authenticated:
        user = request.user
        progress_percentage = user.participant.sessions_completed / 6 * 100
        return render(request, 'user/home.html', context={'user': user, 'percentage': int(progress_percentage)})
    else:
        return redirect('/user/login')

def log_visit(request):
    if request.user.is_authenticated:
        user = request.user
        utc = pytz.UTC
        old = user.participant.last_visit
        # dt = datetime.datetime.strptime(str(old), '%Y-%m-%d %H:%M:%S')
        windback = timezone.now() - datetime.timedelta(days=14)
        last_time = old#.replace(tzinfo=utc)
        wind_time = windback#.replace(tzinfo=utc)
        rem_time = last_time + datetime.timedelta(seconds=10) - timezone.now()
        if(rem_time > datetime.timedelta()):
            return HttpResponse('Sorry, you cannot attempt the experiment more than once in two weeks. Time until next attempt: %s' % rem_time)
        else:
            if user.participant.sessions_completed < 6:
                otp = user_new_visit(user)
                if request.method == "GET":
                    return HttpResponseRedirect(reverse('user:visit_success', args=(), kwargs={'otp': otp}))
            else:
                return HttpResponse("You have completed all of your sessions and thus cannot attempt further tests.")
    else:
        return redirect('/user/login/')

def visit_success(request, otp):
    if request.user.is_authenticated:
        user = request.user
        match user.participant.sessions_completed:
            case 1:
                return render(request, 'user/attempt.html', {
                    'user': user, 
                    'otp' : otp, 
                    'url' : "https://www.google.com"
                })
            case 2:
                return render(request, 'user/attempt.html', {
                    'user': user, 
                    'otp' : otp, 
                    'url' : "https://www.netflix.com"
                })
            case 3:
                return render(request, 'user/attempt.html', {
                    'user': user, 
                    'otp' : otp, 
                    'url' : "https://www.youtube.com"
                })
            case 4:
                return render(request, 'user/attempt.html', {
                    'user': user, 
                    'otp' : otp, 
                    'url' : "https://www.twitch.tv"
                })
            case 5:
                return render(request, 'user/attempt.html', {
                    'user': user, 
                    'otp' : otp, 
                    'url' : "https://www.msn.com"
                })
            case 6:
                return render(request, 'user/attempt.html', {
                    'user': user, 
                    'otp' : otp, 
                    'url' : "https://www.amazon.com"
                })
            case default:
                return HttpResponse("Something went wrong.")
                # return render(request, 'user/attempt.html', {
                #     'user': user, 
                #     'otp' : otp, 
                #     'url' : "https://www.flipkart.com"
                # })
    else:
        return redirect('/user/login/')
