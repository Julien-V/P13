#!/usr/bin/python3
# coding : utf-8


from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound
from django.shortcuts import render
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
