#!/usr/bin/python3
# coding : utf-8

import pytest

from django.contrib.auth.models import Group


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
