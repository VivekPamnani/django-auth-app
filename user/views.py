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
from user.models import codes
import shortuuid
import json


# Create your views here.
# def vote(request, question_id):
#     question = get_object_or_404(Question, pk=question_id)
#     try:
#         selected_choice = question.choice_set.get(pk=request.POST['choice'])
#     except (KeyError, choice.DoesNotExist):
#         # Redisplay the question voting form.
#         return render(request, 'polls/vote.html', {
#             'question': question,
#             'error_message': "You didn't select a choice.",
#         })
#     else:
#         selected_choice.votes += 1
#         selected_choice.save()
#         # Always return an HttpResponseRedirect after successfully dealing
#         # with POST data. This prevents data from being posted twice if a
#         # user hits the Back button.
#         return HttpResponseRedirect(reverse('polls:detail', args=(question.id,)))

def index(request):
    return HttpResponse("this is the index page")

def user_init(user):
    user.participant.department = "CSE"
    user.participant.sessions_completed = 0
    # user.participant.visit_time_1 = datetime.timedelta()
    # user.participant.visit_time_2 = datetime.timedelta()
    # user.participant.visit_time_3 = datetime.timedelta()
    # user.participant.visit_time_4 = datetime.timedelta()
    # user.participant.visit_time_5 = datetime.timedelta()
    # user.participant.visit_time_6 = datetime.timedelta()
    # user.participant.last_visit = datetime.timedelta()
    user.save()

def user_new_visit(user):
    user.participant.sessions_completed += 1
    t = datetime.datetime.now()
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
    return render(request, 'user/home.html')

def log_visit(request):
    # return JsonResponse({'timezone': timezone.now(), 'datetime': datetime.datetime.now()})
    old = "2022-05-28 00:00:00"
    dt = datetime.datetime.strptime(old, '%Y-%m-%d %H:%M:%S')
    windback = datetime.datetime.now() - datetime.timedelta(days=12, seconds=1)
    if(dt > windback):
        return HttpResponse('Sorry, you cannot attempt the experiment more than once in two weeks.')
    else:
        if request.user.is_authenticated:
            user = request.user
            # col = "visit_time_" + user.participant.sessions_completed
            if user.participant.sessions_completed < 6:
                otp = user_new_visit(user)
                match user.participant.sessions_completed:
                    case 1:
                        # return redirect('https://www.psytoolkit.org/c/3.4.2/survey?s=WTkWO')
                        return HttpResponse("Your OTP is %s." % otp)
                    case 2:
                        # return redirect('https://www.psytoolkit.org/c/3.4.2/survey?s=WTkWO')
                        return HttpResponse("Your OTP is %s." % otp)
                    case 3:
                        # return redirect('https://www.psytoolkit.org/c/3.4.2/survey?s=WTkWO')
                        return HttpResponse("Your OTP is %s." % otp)
                    case 4:
                        # return redirect('https://www.psytoolkit.org/c/3.4.2/survey?s=WTkWO')
                        return HttpResponse("Your OTP is %s." % otp)
                    case 5:
                        # return redirect('https://www.psytoolkit.org/c/3.4.2/survey?s=WTkWO')
                        return HttpResponse("Your OTP is %s." % otp)
                    case 6:
                        # return redirect('https://www.psytoolkit.org/c/3.4.2/survey?s=WTkWO')
                        return HttpResponse("Your OTP is %s." % otp)
                    case default:
                        return HttpResponse("Something went wrong.")
            else:
                return HttpResponse("You have completed all of your sessions and thus cannot attempt further tests.")
        else:
            return redirect('/user/home/')
    # return redirect('https://www.psytoolkit.org/c/3.4.2/survey?s=WTkWO')