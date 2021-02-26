#!/usr/bin/python3
# coding : utf-8

from django.urls import path

from .import views

urlpatterns = [
    path('', views.index, name="home"),
    path('about', views.about, name="about_us"),
    path('add_article', views.add_article, name="add_article"),
    path('add_comment', views.add_comment, name="add_comment"),
    path('article/<slug:slug>/', views.show_article, name="article"),
    path('category/<slug:slug>/', views.list_by_category, name="category"),
    path('edit/article/<slug:slug>/', views.edit_article, name="edit_article"),
    path('delete/article/<slug:slug>/', views.del_article, name="del_article"),
    path('del_comment', views.del_comment, name="del_comment"),
    path('dashboard', views.dashboard, name="dashboard"),
    path("login", views.log_in, name="login"),
    path("sign_up", views.sign_up, name="sign_up"),
    path('logout', views.log_out, name="logout")
]
