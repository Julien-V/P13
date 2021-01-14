#!/usr/bin/python3
# coding : utf-8


from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound
from django.shortcuts import render, redirect
from app_blog.models import Category

import json


def index(req):
    return render(req, 'index.html')


@login_required
def get_category(req):
    if req.method == 'POST':
        body = json.loads(req.body)
        cat_name = body['name']
        if len(cat_name):
            try:
                cat = Category.objects.get(name=cat_name)
                print(cat.name)
                # category url should be implemented soon
                # return redirect(cat.get_absolute_url())
            except Category.DoesNotExist:
                print(f"Category {cat_name} DoesNotExist")
            # group verification ?
    return HttpResponseNotFound()
