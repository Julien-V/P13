#!/usr/bin/python3
# coding : utf-8

import re
import pytest

from django.contrib.auth.models import User

from django.shortcuts import reverse

from app_blog.models import Article, Comment


@pytest.mark.django_db
def test_list_by_category(client, make_test_articles):
    """Tests /category/ status_code and number of articles
    in response.content
    """
    # get all articles
    articles = Article.objects.all()
    if not len(articles):
        pytest.fail('no articles')
    client.login(username="test_aute", password="password_aute")
    cat_list = list()
    for article in articles:
        for cat in article.category_set.all():
            cat_list.append(cat)
    cat_list = [cat.get_absolute_url() for cat in cat_list]
    response = client.get(cat_list[0])
    assert response.status_code == 200
    html = response.content.decode()
    articles_html = [
        article.start() for article in re.finditer('row article-detail', html)
    ]
    assert len(articles_html) == len(articles)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "name, expected_status_code, cat_list, expected_nb_articles",
    [
        ("Admin", 200, ["subcat-Anglais", "subcat-Conseiller"], 4),
        ("Conseiller", 200, ["subcat-Anglais", "subcat-Conseiller"], 4),
        ("Contributeur", 200, ["subcat-Anglais", "subcat-Référentiels"], 4),
        ("Auteur", 200, ["subcat-Anglais", "subcat-Forum"], 4),
        ("Abonné", 302, [], 0),
        ("Expert", 302, [], 0)
    ])
def test_add_article(
        client, make_test_users, get_articles_fields,
        name, expected_status_code, cat_list, expected_nb_articles):
    """Tests /add_article status code, articles in db
    for each group
    """
    group_name = name.lower()[:4]
    credentials = {
        "username": f"test_{group_name}",
        "password": f"password_{group_name}"
    }
    client.login(**credentials)
    response = client.get(reverse("add_article"))
    assert response.status_code == expected_status_code
    # login_required
    # add_article perm
    if response.status_code == 200:
        # get csrf_token from cookie
        csrf_token = client.cookies['csrftoken'].value
        # get articles fields from fixture
        articles_fields_list = get_articles_fields(None)
        for article_fields in articles_fields_list:
            # we don't need 'writer' field
            article_fields.pop('writer')
            if len(cat_list):
                for cat in cat_list:
                    article_fields[cat] = "on"
            # add csrf
            article_fields["csrfmiddlewaretoken"] = csrf_token
            # post request
            response = client.post(reverse("add_article"), article_fields)
        # get all articles
        articles = Article.objects.all()
        assert len(articles) == expected_nb_articles
        if len(cat_list):
            # get cat name from cat_list ('subcat-name'-->'name')
            cat_list = [elem.split("-")[1] for elem in cat_list]
            for article in articles:
                cat_all = article.category_set.all()
                cat_validation = {
                    cat.name: True for cat in cat_all if cat.name in cat_list
                }
                # cat name verification
                assert len(cat_validation) == len(cat_list)


@pytest.mark.django_db
def test_show_article(client, make_test_articles):
    """Tests show article"""
    client.login(username="test_admi", password="password_admi")
    articles = Article.objects.all()
    for article in articles:
        res = client.get(article.get_absolute_url())
        assert res.status_code == 200
        assert article.content in res.content.decode()


@pytest.mark.django_db
def test_show_article_wrong_article(client, make_test_articles):
    client.login(username="test_admi", password="password_admi")
    response = client.get("/article/test-1/")
    assert response.status_code == 404


@pytest.mark.django_db
def test_add_comment(client, make_test_articles, make_test_users):
    """Tests /add_comment"""
    client.login(username="test_admi", password="password_admi")
    articles = Article.objects.all()
    article = articles[0]
    response = client.get(article.get_absolute_url())
    assert response.status_code == 200
    if response.status_code == 200:
        # get csrf_token from cookie
        csrf_token = client.cookies['csrftoken'].value
        fields = {
            "content": "test_add_comment",
            "csrfmiddlewaretoken": csrf_token,
            "article_slug": article.slug
        }
        response = client.post(reverse('add_comment'), fields)
        assert response.status_code == 302
        try:
            comment = Comment.objects.get(content=fields["content"])
        except Comment.DoesNotExist:
            pytest.fail('comment DoesNotExist')
        assert comment.writer.username == "test_admi"


@pytest.mark.django_db
def test_edit_article(client, make_test_articles):
    client.login(username="test_admi", password="password_admi")
    articles = Article.objects.all()
    article = articles[0]
    response = client.get(article.get_edit_url())
    assert response.status_code == 200
    if response.status_code == 200:
        # get csrf_token from cookie
        csrf_token = client.cookies['csrftoken'].value
        content = "test_edit_article"
        cat_dict = {
            f"subcat-{cat.name}": "on" for cat in article.category_set.all()}
        fields = {
            "categories": cat_dict,
            "content": content,
            "title": article.title+"edited",
            "description": article.description,
            "csrfmiddlewaretoken": csrf_token,
        }
        response = client.post(article.get_edit_url(), fields)
        assert response.status_code == 302
        assert response.url == article.get_absolute_url()
        article = Article.objects.get(id=article.id)
        assert "edited" in article.title


@pytest.mark.django_db
def test_edit_article_wrong_user(client, make_test_articles):
    """Tests edit_article view by trying to edit an article
    with the wrong user test_cont (Contributeur)."""
    client.login(username="test_cont", password="password_cont")
    articles = Article.objects.all()
    article = articles[0]
    response = client.get(article.get_edit_url())
    assert response.status_code == 404


@pytest.mark.django_db
@pytest.mark.parametrize(
    "username, password, expected, is_deleted",
    [
        ("test_admi", "password_admi", {"code": 302, "url": "/"}, True,),
        ("test_cons", "password_cons", {"code": 404, "url": None}, False,),
        ("test_fake", "password_fake", {"code": 302, "url": None}, False,),
    ]
)
def test_del_article(
        client, make_test_articles,
        username, password, expected, is_deleted):
    """Tests del_article view by deleting an article"""
    client.login(username=username, password=password)
    articles = Article.objects.all()
    article = articles[0]
    article_slug = article.slug
    response = client.get(article.get_delete_url())
    assert response.status_code == expected["code"]
    if expected["url"]:
        assert response.url == expected["url"]
    if is_deleted:
        with pytest.raises(Article.DoesNotExist):
            Article.objects.get(slug=article_slug)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "username, password, expected, is_deleted",
    [
        ("test_admi", "password_admi", {"code": 302, "url": ""}, True,),
        ("test_aute", "password_aute", {"code": 302, "url": ""}, True,),
        ("test_fake", "password_fake", {"code": 302, "url": None}, False,),
    ]
)
def test_del_comment(
        client, make_test_comment,
        username, password, expected, is_deleted):
    """Tests del_comment view by deleting an article"""
    client.login(username=username, password=password)
    comments = Comment.objects.all()
    comment = comments[0]
    comment_id = comment.id
    article_url = comment.article.get_absolute_url()
    response = client.get(comment.get_delete_url())
    assert response.status_code == expected["code"]
    if expected["url"]:
        assert response.url == article_url
    if is_deleted:
        with pytest.raises(Comment.DoesNotExist):
            Comment.objects.get(id=comment_id)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "username, password, expected, link_displayed",
    [
        ("test_admi", "password_admi", {"code": 200, "url": None}, True,),
        ("test_cons", "password_cons", {"code": 200, "url": None}, False,),
        ("test_fake", "password_fake", {
            "code": 302, "url": "/login?next=/dashboard"}, False,),
    ]
)
def test_dashboard(
        client, make_test_users,
        username, password, expected, link_displayed):
    """Tests status_code for /dashboard"""
    client.login(username=username, password=password)
    if link_displayed:
        response = client.get(reverse('home'))
        assert "/dashboard" in response.content.decode()
    response = client.get(reverse('dashboard'))
    assert response.status_code == expected["code"]
    if expected["url"]:
        assert response.url == expected['url']


@pytest.mark.django_db
@pytest.mark.parametrize(
    "username, password, expected",
    [
        ("test_admi", "password_admi", {"code": 200, "can_edit": True},),
        ("test_aute", "password_aute", {"code": 200, "can_edit": False},),
        ("test_abon", "password_abon", {"code": 200, "can_edit": False},),
    ]
)
def test_show_profile(
        client, make_test_users,
        username, password, expected):
    """Tests status_code for /user/test_admi/"""
    client.login(username=username, password=password)
    response = client.get("/user/test_admi/")
    assert response.status_code == expected["code"]
    if expected["can_edit"]:
        assert "Éditer mon profil" in response.content.decode()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "username, groups, expected",
    [
        ('test_aute', ["Contributeur", "Abonné"], {"code": 200, "url": None},),
        ('', ["Admin"], {"code": 302, "url": reverse('dashboard')},),
        ('test_null', ["Admin"], {"code": 302, "url": reverse('dashboard')},),
        ('test_aute', ["null"], {"code": 200, "url": None},),
    ]
)
def test_change_groups(
        client, make_test_users,
        username, groups, expected):
    """Tests /change_groups"""
    client.login(username="test_admi", password="password_admi")
    response = client.get('/user/test_aute/')
    # get csrf_token from cookie
    csrf_token = client.cookies['csrftoken'].value
    fields = dict()
    fields['csrfmiddlewaretoken'] = csrf_token
    if len(username):
        fields['username'] = username
    for group in groups:
        fields[group] = "on"
    response = client.post(reverse('change_groups'), fields)
    assert response.status_code == expected['code']
    if expected['url']:
        assert response.url == expected['url']
    if response.status_code == 200:
        user = User.objects.get(username=username)
        groups = sorted(user.groups.all(), key=lambda i: i.name)
        groups_str = ''.join(f"{group.name};" for group in groups)
        expected_response = f"{user.id}/{groups_str}"
        assert response.content.decode() == expected_response


@pytest.mark.django_db
@pytest.mark.parametrize(
    "username, expected",
    [
        ("test_cont", {"code": 200}),
        ("test_fake", {"code": 404}),
    ]
)
def test_block_users(client, make_test_users, username, expected):
    """Tests /block"""
    client.login(username="test_admi", password="password_admi")
    response = client.get(reverse('block'), {"username": username})
    assert response.status_code == expected["code"]
    if response.status_code == 200:
        try:
            user_obj = User.objects.get(username=username)
        except User.DoesNotExist:
            pytest.fail("User.DoesNotExist")
        assert user_obj.is_active is False
        assert response.content.decode() == f"{username}/{user_obj.is_active}"
