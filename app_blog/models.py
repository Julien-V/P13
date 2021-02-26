#!/usr/bin/python3
# coding : utf-8

from django.db import models

from django.utils import timezone
from django.shortcuts import reverse

from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.template.defaultfilters import slugify

from app_blog.utils import has_perm_list, has_group_perm

import uuid


class Article(models.Model):
    title = models.CharField(max_length=300)
    description = models.TextField(null=True)
    content = models.TextField()
    writer = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(editable=False)
    updated = models.DateTimeField()
    is_anonymous = models.BooleanField(null=True)
    is_public = models.BooleanField(null=True)
    ext_link = models.URLField(max_length=600, null=True)
    slug = models.SlugField(null=False, unique=True)

    def get_absolute_url(self):
        return reverse('article', args=(self.slug,))

    def get_edit_url(self):
        return reverse('edit_article', args=(self.slug,))

    def get_delete_url(self):
        return reverse('del_article', args=(self.slug,))

    def _can_be_by(self, req, first_perm, second_perm):
        try:
            user = User.objects.get(username=req.user)
        except User.DoesNotExist:
            return False
        if self.writer == user:
            return has_perm_list(req, [first_perm])
        else:
            return has_perm_list(req, [second_perm])

    def can_be_edited_by(self, req):
        return self._can_be_by(
            req, "change_user_articles", "change_users_articles"
        )

    def can_be_deleted_by(self, req):
        return self._can_be_by(
            req, "del_user_articles", "del_users_articles"
        )

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
        self.updated = timezone.now()
        # temp slug
        if len(self.slug) < 1:
            self.slug = str(uuid.uuid4())
            super().save(*args, **kwargs)
            self.slug = f"{slugify(self.title)}-{self.id}"
            return super().save(*args, **kwargs)
        else:
            return super().save(*args, **kwargs)

    class Meta:
        permissions = (
            ("view_article_public", "Can view public article"),
            ("view_anonymous_article", "Can view writer of anonymous article"),
            ("add_anonymous_article", "Can add anonymous article"),
            ("del_user_articles", "Can delete its own articles"),
            ("del_users_articles", "Can delete other users' articles"),
            ("change_user_articles", "Can change its own articles"),
            ("change_users_articles", "Can change other users' articles")
        )


class Category(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(null=True)
    slug = models.SlugField(null=False, unique=True)
    parent_category = models.ForeignKey(
        'self', related_name='sub_category',
        on_delete=models.SET_NULL, null=True)
    articles = models.ManyToManyField(Article)
    groups = models.ManyToManyField(Group)

    def get_absolute_url(self):
        return reverse('category', args=(self.slug,))

    def can_be_viewed_by(self, req):
        try:
            User.objects.get(username=req.user)
        except User.DoesNotExist:
            return False
        if not len(self.groups.all()):
            return True
        else:
            group_clearance = [
                has_group_perm(req, group) for group in self.groups.all()
            ]
            if True in group_clearance:
                return True
            else:
                return False

    def save(self, *args, **kwargs):
        # temp slug
        if len(self.slug) < 1:
            self.slug = str(uuid.uuid4())
            super().save(*args, **kwargs)
            self.slug = f"{slugify(self.name)}-{self.id}"
            return super().save(*args, **kwargs)
        else:
            return super().save(*args, **kwargs)

    class Meta:
        permissions = (
            ("edit_category", "Can edit a category"),
            ("del_category", "Can delete a category"),
            ("view_category_forum", "Can view Forum"),
            ("view_category_all_wo_c_f",
                "Can view all category w/o Conseillers&Forum"),
            ("view_category_all", "Can view all category")
        )


class Comment(models.Model):
    content = models.TextField()
    original_content = models.TextField(null=True)
    writer = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    created = models.DateTimeField(editable=False)
    updated = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
        self.updated = timezone.now()
        return super().save(*args, **kwargs)

    def get_delete_url(self):
        return f"/del_comment?id={self.id}"

    def _can_be_by(self, req, first_perm, second_perm):
        try:
            user = User.objects.get(username=req.user)
        except User.DoesNotExist:
            return False
        if self.writer == user:
            return has_perm_list(req, [first_perm])
        else:
            return has_perm_list(req, [second_perm])

    def can_be_deleted_by(self, req):
        return self._can_be_by(
            req, "del_user_comment", "del_users_comment"
        )

    class Meta:
        permissions = (
            ("edit_comment", "Can edit a comment"),
            ("del_user_comment", "Can delete its own comments"),
            ("del_users_comment", "Can delete other users' comments")
        )
