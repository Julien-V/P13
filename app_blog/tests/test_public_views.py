#!/usr/bin/python3
# coding : utf-8

import pytest

from django.contrib.auth.models import User

from django.shortcuts import reverse

from app_blog.models import Profile


@pytest.mark.django_db
@pytest.mark.parametrize(
    "url, expected_status_code",
    [
        (reverse("home"), 200,),
        (reverse("about_us"), 200),
        (reverse("login"), 200),
        (reverse("sign_up"), 200)
    ]
)
def test_public_url(client, url, expected_status_code):
    response = client.get(url)
    assert response.status_code == expected_status_code


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


class TestSignUp:
    fields = {
        "first_name": "test_first_name",
        "last_name": "test_last_name",
        "username": "test_username",
        "email": "test@email.com",
        "password1": "password_test",
        "password2": "password_test"
    }

    @pytest.mark.django_db
    def get_csrf(self, client):
        response = client.get(reverse("sign_up"))
        assert response.status_code == 200
        csrf_token = client.cookies['csrftoken'].value
        self.fields["csrftoken"] = csrf_token

    @pytest.mark.django_db
    def test_valid_sign_up(self, client):
        self.get_csrf(client)
        response = client.post(reverse("sign_up"), self.fields)
        assert response.status_code == 302
        assert response.url == "/login"

    @pytest.mark.django_db
    def test_valid_sign_up_profile(self, client):
        self.test_valid_sign_up(client)
        try:
            user = User.objects.get(username=self.fields["username"])
            Profile.objects.get(user=user)
        except User.DoesNotExist:
            pytest.fail("User DoesNotExist")
        except Profile.DoesNotExist:
            pytest.fail("Profile DoesNotExist")
        groups = user.groups.all()
        groups_name = [group.name for group in groups]
        assert "Abonné" in groups_name

    @pytest.mark.django_db
    def test_invalid_sign_up(self, client):
        self.get_csrf(client)
        fields = self.fields.copy()
        fields["username"] = fields["username"].replace("_", " ")
        response = client.post(reverse("sign_up"), fields)
        assert response.status_code == 200
        html = response.content.decode()
        assert "errorlist" in html
        div_alert = """<div class="alert alert-danger """
        div_alert += """alert-dismissible fade show" role="alert">"""
        assert div_alert in html
