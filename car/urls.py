from django.urls import path

from . import views


urlpatterns = [
	path('', views.index),
    path('login/', views.login),
    path('<int:car_id>/', views.car),
    path('<int:car_id>/control/<str:command>', views.command),
]