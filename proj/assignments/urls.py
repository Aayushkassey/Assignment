from django.urls import path
from .views import *
urlpatterns = [
    path('', home, name='home'),
    path('dashboard/', dashboard, name='dashboard'),
    path('lab/<int:pk>/', lab_detail, name='lab_detail'),
    path('add_lab/', add_lab, name='add_lab'),
    path('compiler/', compiler, name='compiler'),
    path('view_submissions/<int:lab_id>/', view_submissions, name='view_submissions'),
    path('profile_view/', profile_view, name='profile_view'),
]