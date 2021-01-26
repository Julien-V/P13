#!/usr/bin/python3
# coding : utf-8

import pytest

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group

from app_blog.models import Article, ArticleCategory, Category


@pytest.fixture
def make_test_users():
    """This fixture adds one user for each Group"""
    groups = [
        "Admin",
        "Conseiller",
        "Contributeur",
        "Auteur",
        "Abonné",
        "Expert",
    ]
    for group in groups:
        user_fields = {
            "username": f"test_{group.lower()[:4]}",
            "password1": f"password_{group.lower()[:4]}",
            "password2": f"password_{group.lower()[:4]}"
        }
        # add user
        user = UserCreationForm(user_fields)
        if user.is_valid():
            user.save()
        else:
            pytest.fail(
                "UserCreationForm failed in fixture : make_test_users")

        user = User.objects.get(username=user_fields['username'])
        try:
            # get group
            group_obj = Group.objects.get(name=group)
        except group.DoesNotExist:
            pytest.fail(f"{group} DoesNotExist")
        # add user to group
        group_obj.user_set.add(user)


@pytest.fixture
def make_test_articles():
    """This fixture adds several articles :
        - is_public = True
        - is_public = False
        - is_anonymous = True
        - is_anonymous = False
    """
    user_fields = {
        "username": "test_aute",
        "password1": "password_aute",
        "password2": "password_aute"
    }
    # add user
    user = UserCreationForm(user_fields)
    if user.is_valid():
        user.save()
    else:
        pytest.fail(
            "UserCreationForm failed in fixture : make_test_articles")

    user = User.objects.get(username=user_fields['username'])
    group_obj = Group.objects.get(name="Auteur")
    group_obj.user_set.add(user)
    # add articles
    article_fields_mod = [
        {'is_public': True},
        {'is_public': False},
        {'is_anonymous': True},
        {'is_anonymous': False},
    ]
    article_fields = {
        'title': 'test_title',
        'description': 'test_description',
        'content': 'test_content',
        'writer': user,
    }
    article_fields_list = list()
    for fields_mod in article_fields_mod:
        article_fields_list.append({**article_fields.copy(), **fields_mod})
    cat = Category.objects.get(name="Anglais")  # test multiples category
    for fields in article_fields_list:
        article = Article(**fields)
        article.save()
        art_cat = ArticleCategory(article=article, category=cat)
        art_cat.save()
