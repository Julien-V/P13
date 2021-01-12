#!/usr/bin/python3
# coding : utf-8

import pytest

from django.contrib.auth.models import Group
from django.conf import settings

from app_blog.models import Category


@pytest.mark.django_db
@pytest.mark.parametrize(
    "name",
    [
        ("Admin"),
        ("Conseiller"),
        ("Contributeur"),
        ("Auteur"),
        ("Abonné"),
        ("Expert")
    ])
def test_group(name):
    """Test groups creation"""
    try:
        group = Group.objects.get(name=name)
    except Group.DoesNotExist:
        pytest.fail(f"{name} DoesNotExist")
    assert group.name == name


@pytest.mark.django_db
@pytest.mark.parametrize(
    "cat",
    settings.APP_BLOG_CATEGORY_HIERARCHY.copy())
def test_category(cat):
    name = cat['name']
    sub_cat = cat['sub_cat']
    try:
        cat_obj = Category.objects.get(name=name)
    except Category.DoesNotExist:
        pytest.fail(f"{name} DoesNotExist")
    assert cat_obj.name == name
    assert len(sub_cat) == len(cat_obj.sub_category.all())
