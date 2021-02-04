#!/usr/bin/python3
# coding : utf-8

from django.urls import path

from .import views

urlpatterns = [
    path('', views.index, name="home"),
    path('add_article', views.add_article, name="add_article"),
    path('add_comment', views.add_comment, name="add_comment"),
    path('article/<slug:slug>/', views.show_article, name="article"),
    path('category/<slug:slug>/', views.list_by_category, name="category"),
    path("login", views.log_in, name="login"),
    path("sign_up", views.sign_up, name="sign_up"),
    path('logout', views.log_out, name="logout")
]
