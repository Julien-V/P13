#!/usr/bin/python3
# coding : utf-8

from django import template

register = template.Library()


@register.filter
def order_by_id(value):
    """Orders by id."""
    return sorted(value, key=lambda i: i.id)
