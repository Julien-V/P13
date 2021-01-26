#!/usr/bin/python3
# coding : utf-8

import re
import pytest

from app_blog.models import Article, Category
from app_blog.models import ArticleCategory


@pytest.mark.django_db
def test_list_by_category(client, make_test_articles):
    articles = Article.objects.all()
    if not len(articles):
        pytest.fail('no articles')
    client.login(username="test_aute", password="password_aute")
    cat_list = list()
    for article in articles:
        art_cat = ArticleCategory.objects.filter(article=article)
        cat_list.append(art_cat[0].category)
    cat_list = [cat.get_absolute_url() for cat in cat_list]
    response = client.get(cat_list[0])
    assert response.status_code == 200
    html = response.content.decode()
    articles_html = [article.start() for article in re.finditer('article-', html)]
    assert len(articles_html) == len(articles)