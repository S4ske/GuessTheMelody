from django.urls import path

from . import views

urlpatterns = [
	path('create_game/<str:nickname>/', views.create_game),
	path('get_token/', views.get_token),
	path('delete_token/', views.delete_token),
	path('add_link/', views.add_link),
	path('get_melody_file/<str:filename>/', views.get_melody_file),
]
