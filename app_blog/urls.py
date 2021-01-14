#!/usr/bin/python3z
# coding : utf-8

from django.urls import path

from .import views

urlpatterns = [
    path('', views.index, name="home"),
    path('get_category', views.get_category, name="get_category")
]
