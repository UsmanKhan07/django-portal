from django.contrib import admin
from django.urls import path
from home import views

urlpatterns = [
    path("", views.index, name='home'),
    path("about", views.about, name='about'),
    path("services", views.services, name='services'),
    path("contact", views.contact, name='contact'), 
    path("main", views.main, name='main'), 
    path("/(?P<defualt_email>\w+<t_id>\w+)/$", views.index, name='home')
    
]