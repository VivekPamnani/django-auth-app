from dataclasses import dataclass
from logging import exception
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.views import generic
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
import datetime
from django.utils import timezone
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

def update_custom_fields(user):
    user.participant.department = "CSE"
    user.save()

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
        update_custom_fields(user)
    return redirect("https://www.psytoolkit.org/")

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
            return HttpResponse("The logged in user department is: %s" % user.participant.department)
        return redirect('/user/home/')
    return HttpResponse('%s' % windback)
    # return redirect('https://www.psytoolkit.org/c/3.4.2/survey?s=WTkWO')