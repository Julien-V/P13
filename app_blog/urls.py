#!/usr/bin/python3
# coding : utf-8

from django.urls import path

from .import views

urlpatterns = [
    path('', views.index, name="home"),
    path('category/<slug:slug>/', views.list_by_category, name="category"),
    path("login", views.log_in, name="login"),
    path('logout', views.log_out, name="logout")
]
