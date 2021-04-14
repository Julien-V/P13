#!/usr/bin/python3
# coding : utf-8

import pytest

from django.contrib.auth.models import User, Group

from app_blog.utils import has_perm_list, get_user_groups_perm
from app_blog.utils import has_group_perm


@pytest.mark.django_db
@pytest.mark.parametrize(
    "group",
    [
        ("Admin"),
        ("Conseiller"),
        ("Contributeur"),
        ("Auteur"),
        ("Abonné"),
        ("Expert"),
    ]
)
def test_get_user_group_perm(make_test_users, group):
    username = f"test_{group.lower()[:4]}"
    user = User.objects.get(username=username)
    group_obj = Group.objects.get(name=group)

    class Req:
        # fake request object
        user = username
    t_user, t_group, t_perm = get_user_groups_perm(Req)
    assert t_user == user
    assert t_group[0] == group_obj


@pytest.mark.django_db
@pytest.mark.parametrize(
    "group",
    [
        ("Admin"),
        ("Conseiller"),
        ("Contributeur"),
        ("Auteur"),
        ("Abonné"),
        ("Expert"),
    ]
)
def test_has_perm_list(make_test_users, group):
    username = f"test_{group.lower()[:4]}"
    group_obj = Group.objects.get(name=group)
    perms = [perm.codename for perm in group_obj.permissions.all()]

    class Req:
        # fake request object
        user = username
    t_val = has_perm_list(Req, perms, False)
    assert t_val is True
    t_val = has_perm_list(Req, ["fake_perm"], False)
    assert t_val is not True
    t_val = has_perm_list(Req, perms, False, return_dict=True)
    assert isinstance(t_val, dict)
    assert False not in t_val.values()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "group, users_dict",
    [
        ("Admin", {
            "test_admi": True,
        }),
        ("Conseiller", {
            "test_admi": True,
            "test_cons": True,
        }),
        ("Contributeur", {
            "test_admi": True,
            "test_aute": True,
            "test_cont": True,
        }),
        ("Auteur", {
            "test_admi": True,
            "test_aute": True,
        }),
        ("Abonné", {
            "test_admi": True,
            "test_aute": True,
            "test_cont": True,
            "test_expe": True,
        }),
        ("Expert", {
            "test_admi": True,
            "test_expe": True,
        }),
    ]
)
def test_has_group_perm(make_test_users, group, users_dict):
    for key, val in users_dict.items():
        username = key
        group_obj = Group.objects.get(name=group)

        class Req:
            # fake request object
            user = username
        t_val = has_group_perm(Req, group_obj, False)
        assert t_val is val
