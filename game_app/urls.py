from django.urls import path

from . import views

urlpatterns = [
    path('create_game/<str:nickname>/', views.create_game, name='index'),
]
