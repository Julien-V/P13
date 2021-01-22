#!/usr/bin/python3
# coding : utf-8

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from django.http import HttpResponseNotFound

from django.shortcuts import render, redirect, reverse

from app_blog.forms import ConnectionForm
from app_blog.models import Category


def navbar_init():
    """Initializes navbar

    :return context: dict()
    """
    context = dict()
    cat_name = ["Langues"]
    for name in cat_name:
        try:
            cat = Category.objects.get(name=name)
            context[name.lower()] = cat
        except Category.DoesNotExist:
            print(f"{name} DoesNotExist")
    return context


def index(req):
    context = dict()
    context = context | navbar_init()
    return render(req, 'index.html', context)


def log_in(req):
    error = False
    if req.method == "POST":
        form = ConnectionForm(req.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(
                username=username,
                password=password)
            if user:
                login(req, user)
            else:
                error = True
    else:
        form = ConnectionForm()
    return render(req, 'login.html', locals())


@login_required
def list_by_category(req, slug):
    try:
        cat = Category.objects.get(slug=slug)
    except Category.DoesNotExist:
        return HttpResponseNotFound()
    context = {
        "category": cat
    }
    context = context | navbar_init()
    return render(req, 'list_by_category.html', context)


@login_required
def log_out(req):
    logout(req)
    return redirect(reverse("home"))
