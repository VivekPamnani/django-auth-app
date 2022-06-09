from logging import exception
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.views import generic
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse


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

def login(request):
    try:
        entered_username = request.POST['username']
        # entered_email = request.POST['email']  
        entered_pwd = request.POST['password']
    except:
        return render(request, 'user/login.html')
    else:
        user = authenticate(username=entered_username, password=entered_pwd)
        if user is not None:
            return HttpResponse("You are logged in")
        else:
            return HttpResponse("Invalid attempt.")