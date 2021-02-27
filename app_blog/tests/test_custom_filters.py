#!/usr/bin/python3
# coding : utf-8

from random import shuffle

from app_blog.templatetags import custom_filters


def test_order_by_id():
    """Tests custom_filters.order_by_id()"""
    class Fake:
        def __init__(self, id):
            self.id = id
    sorted_value_list = [Fake(x) for x in range(0, 10)]
    random_value_list = sorted_value_list.copy()
    shuffle(random_value_list)
    # using custom_filters.order_by_id
    sorted_list = custom_filters.order_by_id(random_value_list)
    for id_elem, elem in enumerate(sorted_list):
        assert elem == sorted_value_list[id_elem]
