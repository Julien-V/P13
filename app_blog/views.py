#!/usr/bin/python3
# coding : utf-8

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from django.http import HttpResponseNotFound

from django.shortcuts import render, redirect, reverse

from app_blog.forms import ConnectionForm

from app_blog.models import ArticleCategory, Category, CategoryGroup

from app_blog.utils import has_perm_list
from app_blog.utils import has_group_perm


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
    context = {**context, **navbar_init()}
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
    context = {
        "error": error,
        "form": form
    }
    context = {**context, **navbar_init()}
    return render(req, 'login.html', context)


@login_required
def list_by_category(req, slug):
    try:
        # get cat
        cat = Category.objects.get(slug=slug)
        # get articles
        articles = ArticleCategory.objects.filter(category=cat)
        if not len(articles):
            raise ArticleCategory.DoesNotExist
        articles = [elem.article for elem in articles]
    except Category.DoesNotExist:
        cat = None
        return HttpResponseNotFound()
    except ArticleCategory.DoesNotExist:
        articles = None

    try:
        # get cat_group
        cat_group = CategoryGroup.objects.get(category=cat)
        if not has_group_perm(req, cat_group.group):
            # if user not in cat_group.group
            return HttpResponseNotFound()
    except CategoryGroup.DoesNotExist:
        cat_group = None

    if not has_perm_list(req, ["view_article"]):
        if has_perm_list(req, ["view_article_public"]):
            if articles is not None:
                articles = [x for x in articles if x.is_public]
        else:
            return redirect("/")
    context = {
        "articles": articles,
        "category": cat
    }
    context = {**context, **navbar_init()}
    return render(req, 'list_by_category.html', context)


@login_required
def log_out(req):
    logout(req)
    return redirect(reverse("home"))
