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

MAX_SESSIONS = settings.USER_MAX_SESSIONS
SESSION_INTERVAL_DAYS = settings.USER_SESSION_INTERVAL_DAYS
SESSION_INTERVAL_DAYS_MAX = settings.USER_SESSION_INTERVAL_DAYS_MAX
SESSION_LINKS = settings.USER_SESSION_LINKS
SESSION_AMOUNTS = settings.USER_SESSION_AMOUNTS

# Create your views here.
def index(request):
    return HttpResponse("Hello, world. You're at the adminDash index.")
    # return render(request, 'adminDash/index.html')

# ! Unused
def signin(request):
    return redirect('user:login')
    print("adminDash:login")
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_superuser != 1:
                return render(request, "adminDash/login.html", {
                    "err_msg": "You are not an admin."
                })
            login(request, user)
            return redirect('adminDash:adminDash')
        else:
            return render(request, "adminDash/login.html", {
                "message": "Invalid credentials."
            })
    else:
        return render(request, "adminDash/login.html")

def adminDash(request):
    if request.user.is_superuser != 1:
        return redirect('adminDash:login')

    users = User.objects.all()
    total_participants = 0

    # * Get session completion counts
    sess_counts = [[0, 100, 100] for _ in range(7)]
    for user in users:
        # ! Superusers/admins will not have a participant object; skip them.
        if user.is_superuser is True:
            continue
        
        user_sessions_completed = user.participant.sessions_completed
        if user_sessions_completed > 0:
            total_participants += 1
        for sessnum in range(user_sessions_completed+1):
            sess_counts[sessnum][0] += 1
    for sessnum in range(1, 7):
        try:
            sess_counts[sessnum][1] = sess_counts[sessnum][0] * 100 // sess_counts[1][0] 
        except:
            sess_counts[sessnum][1] = 0
        try:
            sess_counts[sessnum][2] = sess_counts[sessnum][0] * 100 // sess_counts[sessnum-1][0] if sessnum > 1 else 100
        except:
            sess_counts[sessnum][2] = 0

    # * Get sessions completed last week
    last_week = timezone.now() - datetime.timedelta(days=7)
    last_week_participants = 0
    for user in users:
        # ! Superusers/admins will not have a participant object; skip them.
        if user.is_superuser is True:
            continue
        
        user_sessions_completed = user.participant.sessions_completed
        user_last_visit = user.participant.last_visit
        if user_last_visit > last_week:
            last_week_participants += 1

    # * Get % of participants enrolled for longitudinal study
    longitudinal_accepted = 0
    longitudinal_rejected = 0
    longitudinal_unanswered = 0
    for user in users:
        # ! Superusers/admins will not have a participant object; skip them.
        if user.is_superuser is True:
            continue
        
        user_sessions_completed = user.participant.sessions_completed
        try:
            user_longitudinal = user.participant.longitudinal_enrollment_status
        except:
            user_longitudinal = 0
        if user_sessions_completed > 0:
            if user_longitudinal == 1:
                longitudinal_accepted += 1
            elif user_longitudinal == 2:
                longitudinal_rejected += 1
            else:
                longitudinal_unanswered += 1
    total_proposed = longitudinal_accepted + longitudinal_rejected + longitudinal_unanswered
    longitudinal_acceptance_rate = longitudinal_accepted * 100 // total_proposed

    return render(request, 'adminDash/adminDash.html', {
        'sess_counts': sess_counts[1:],
        'total_participants': total_participants,
        'last_week': last_week_participants,
        'long_acceptance_rate': longitudinal_acceptance_rate,
    })