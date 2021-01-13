#!/usr/bin/python3
# coding : utf-8

from django.shortcuts import render


def index(req):
    return render(req, 'index.html')
