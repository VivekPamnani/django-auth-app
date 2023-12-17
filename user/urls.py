from django.urls import include, path

from . import views

app_name = 'user'

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.passwordless_login, name='register'),
    path('login/', views.passwordless_login, name='login'),
    path('home/', views.home, name='home'),
    path('visit/', views.log_visit, name='visit'),
    path('visit/<str:otp>/success/', views.visit_success, name='visit_success'),
    path('directions/', views.directions, name='directions'),
    path('logout/', views.signout, name='logout'),
    path('verification/', views.verify_email, name='verify'),
    path('instructions/', views.instructions, name='instructions'),
    path('welcome/', views.welcome, name='welcome'),
    path('consent/', views.consent, name='consent'),
    path('reset/', views.reset_pwd, name='reset'),
    path('ishihara/', views.ishihara, name='ishihara'), 
    path('screen/', views.screen, name='screen'),
    path('freescreen/', views.freescreen, name='freescreen'),
    path('msg/', views.error, name='error'),
    path('getname/', views.forgot_username, name='forgot_username'),
    path('continue/', views.long_proposal, name='long_proposal'),
    path('complete/', views.session_complete, name='session_complete'),
    # path('verification/', include('verify_email.urls')),
    # path('login/', views.login, name='login'),
    # path('logout/', views.vote, name='logout')
]

# urlpatterns = [
#     path('', views.IndexView.as_view(), name='index'),
#     path('<int:pk>/', views.DetailView.as_view(), name='detail'),
#     path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
#     path('<int:question_id>/vote/', views.vote, name='vote'),
# ]