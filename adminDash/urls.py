from django.urls import include, path

from . import views

app_name = 'adminDash'

urlpatterns = [
    path('', views.adminDash, name='adminDash'),
    path('login/', views.signin, name='login'),
]