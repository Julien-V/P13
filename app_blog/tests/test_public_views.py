#!/usr/bin/python3
# coding : utf-8

import pytest


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
