#!/usr/bin/python3
# coding : utf-8

from django import forms

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from app_blog.models import Article, Comment


class ConnectionForm(forms.Form):
    username_email = forms.CharField()
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput
    )
    remember_me = forms.BooleanField(required=False)

    def clean(self):
        """This methods allows connection with email and username
        by overriding forms.Form.clean()

        :return cleaned_data:
        """
        cleaned_data = super(ConnectionForm, self).clean()
        if "username_email" in cleaned_data.keys():
            value = cleaned_data["username_email"]
            cleaned_data["username"] = ""
            for field in ["email", "username"]:
                field_dict = {field: value}
                try:
                    user = User.objects.get(**field_dict)
                    cleaned_data['username'] = user.username
                except User.DoesNotExist:
                    pass
        return cleaned_data


class RegisterForm(UserCreationForm):

    class Meta:
        model = User
        fields = [
            "username", "email",
            'first_name', 'last_name',
            'password1', "password2"
        ]


class AddArticleForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(AddArticleForm, self).__init__(*args, **kwargs)
        not_required_fields = [
            'description', 'is_anonymous',
            'is_public', 'ext_link'
        ]
        for elem in not_required_fields:
            self.fields[elem].required = False

    class Meta:
        model = Article
        fields = [
            'title', 'description', 'content',
            'is_anonymous', 'is_public',
            'ext_link', "writer"
        ]


class EditArticleForm(AddArticleForm):

    def __init__(self, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs)
        not_required_fields = [
            'title', 'description', 'content',
            'is_anonymous', 'is_public', 'ext_link',
            'writer'
        ]
        for elem in not_required_fields:
            self.fields[elem].required = False

    class Meta:
        model = Article
        fields = [
            'title', 'description', 'content',
            'is_anonymous', 'is_public',
            'ext_link', "writer"
        ]


class AddCommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = [
            'content', 'article', 'writer'
        ]
