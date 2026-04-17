from django.urls import path
from .views import *
urlpatterns = [
    path('', home, name='home'),
    path('dashboard/', dashboard, name='dashboard'),
    path('upgrade_semester/', upgrade_semester, name='upgrade_semester'),
    path('lab/<int:pk>/', lab_detail, name='lab_detail'),
    path('add_lab/', add_lab, name='add_lab'),
    path('edit_lab/<int:lab_id>/', edit_lab, name='edit_lab'),
    path('delete_lab/<int:lab_id>/', delete_lab, name='delete_lab'),
    path('compiler/', compiler, name='compiler'),
    path('view_submissions/<int:lab_id>/', view_submissions, name='view_submissions'),
    path('delete_submissions/', delete_submissions, name='delete_submissions'),
    path('profile_view/', profile_view, name='profile_view'),
]