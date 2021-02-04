#!/usr/bin/python3
# coding : utf-8

import pytest

from django.contrib.auth.models import User

from django.shortcuts import reverse


@pytest.mark.django_db
@pytest.mark.parametrize(
    "url, expected_status, expected_redirect_url",
    [
        ("/login", 302, "/",),
        ("/login?next=/add_article", 302, "/add_article",),
        ("/login?next=http://unsecuresite.com", 302, "/",),
    ]
)
def test_log_in(
        client, make_test_users, url,
        expected_status, expected_redirect_url):
    """Tests login view"""
    credentials = {
        "username_email": "test_aute",
        "password": "password_aute"
    }
    response = client.post(url, credentials)
    assert response.status_code == expected_status
    assert response.url == expected_redirect_url


@pytest.mark.django_db
def test_sign_up(client):
    fields = {
        "first_name": "test_first_name",
        "last_name": "test_last_name",
        "username": "test_username",
        "email": "test@email.com",
        "password1": "password_test",
        "password2": "password_test"
    }
    response = client.get(reverse("sign_up"))
    assert response.status_code == 200
    # get csrf_token from cookie
    csrf_token = client.cookies['csrftoken'].value
    fields["csrftoken"] = csrf_token
    response = client.post(reverse("sign_up"), fields)
    assert response.status_code == 302
    assert response.url == "/login"
    try:
        user = User.objects.get(username=fields["username"])
    except User.DoesNotExist:
        pytest.fail("User DoesNotExist")
    groups = user.groups.all()
    groups_name = [group.name for group in groups]
    assert "Abonné" in groups_name
