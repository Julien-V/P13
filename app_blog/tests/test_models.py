#!/usr/bin/python3
# coding : utf-8

import pytest

from app_blog.models import Article, Category, Comment

from django.contrib.auth.models import User

from django.shortcuts import reverse


@pytest.mark.django_db
@pytest.mark.parametrize(
    "obj, fields, slug",
    [
        (Article, {
                'title': 'test_title',
                'description': 'test_description',
                'content': 'test_content',
                'writer': '',
            }, lambda i: f'test_title-{i}'),
        (Category, {
                'name': 'test_name'
            }, lambda i: f'test_name-{i}')
    ])
def test_slug(obj, fields, slug):
    """Test slugs creation"""
    if isinstance(obj(), Article):
        writer = User(
            username='test_user',
            password='test_password')
        writer.save()
        fields['writer'] = User.objects.get(username='test_user')
    temp = obj(**fields)
    temp.save()
    key = list(fields.keys())[0]
    try:
        temp = obj.objects.get(**{key: fields[key]})
    except obj.DoesNotExist:
        pytest.fail(f"{obj} DoesNotExist")
    slug = slug(temp.id)
    assert temp.slug == slug


@pytest.mark.django_db
def test_article_get_edit_url(make_test_articles):
    """Tests Article.get_edit_url()"""
    articles = Article.objects.all()
    if not len(articles):
        pytest.fail("No articles")
    else:
        for article in articles:
            edit_url = f"/edit/article/{article.slug}/"
            assert article.get_edit_url() == edit_url


@pytest.mark.django_db
@pytest.mark.parametrize(
    "username, expected",
    [
        ("test_admi", True,),
        ("test_unknown", False,),
        ("test_cons", False,),
    ]
)
def test_article_can_be_edited_by(make_test_articles, username, expected):
    """Tests Article._can_be_edited_by(req)"""
    class Req:
        user = username
    articles = Article.objects.all()
    if not len(articles):
        pytest.fail("No articles")
    else:
        article = articles[0]
        assert article.can_be_edited_by(Req) == expected


@pytest.mark.django_db
@pytest.mark.parametrize(
    "username, expected",
    [
        ("test_admi", True,),
        ("test_unknown", False,),
        ("test_cons", False,),
    ]
)
def test_article_can_be_deleted_by(make_test_articles, username, expected):
    """Tests Article._can_be_deleted_by(req)"""
    class Req:
        user = username
    articles = Article.objects.all()
    if not len(articles):
        pytest.fail("No articles")
    else:
        article = articles[0]
        assert article.can_be_deleted_by(Req) == expected


@pytest.mark.django_db
def test_comment_get_delete_url(make_test_comment):
    """Tests Comment.get_delete_url()"""
    comments = Comment.objects.all()
    if not len(comments):
        pytest.fail("No comments")
    else:
        for comment in comments:
            del_url = f"{reverse('del_comment')}?id={comment.id}"
            assert comment.get_delete_url() == del_url


@pytest.mark.django_db
@pytest.mark.parametrize(
    "username, expected",
    [
        ("test_admi", True,),
        ("test_unknown", False,),
        ("test_aute", True,),
    ]
)
def test_comment_can_be_deleted_by(make_test_comment, username, expected):
    """Tests Comment.can_be_deleted_by(req)"""
    class Req:
        user = username
    comments = Comment.objects.all()
    if not len(comments):
        pytest.fail("No comments")
    else:
        comment = comments[0]
        assert comment.can_be_deleted_by(Req) == expected
