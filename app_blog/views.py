#!/usr/bin/python3
# coding : utf-8

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group

from django.http import HttpResponseNotFound

from django.shortcuts import render, redirect, reverse

from html import unescape

from app_blog.forms import ConnectionForm, RegisterForm
from app_blog.forms import AddArticleForm, EditArticleForm, AddCommentForm

from app_blog.models import Article, Category

from app_blog.utils import has_perm_list, perm_required
from app_blog.utils import has_group_perm, redirect_next
from app_blog.utils import clean_post_article_fields


def navbar_init():
    """Initializes navbar

    :return context: dict()
    """
    context = dict()
    cat_name = ["Langues"]
    for name in cat_name:
        try:
            cat = Category.objects.get(name=name)
            context[name.lower()] = cat
        except Category.DoesNotExist:
            print(f"{name} DoesNotExist")
    return context


###############################################################################
# Public views
###############################################################################


def index(req):
    context = dict()
    context = {**context, **navbar_init()}
    return render(req, 'index.html', context)


def log_in(req):
    error = False
    if req.method == "POST":
        form = ConnectionForm(req.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(
                username=username,
                password=password)
            if user:
                login(req, user)
                return redirect_next(req)
            else:
                error = True
    else:
        form = ConnectionForm()
    context = {
        "error": error,
        "form": form
    }
    context = {**context, **navbar_init()}
    return render(req, 'login.html', context)


def sign_up(req):
    error = False
    if req.method == "POST":
        form = RegisterForm(req.POST)
        if form.is_valid():
            temp = req.POST.copy()
            form = RegisterForm(temp)
            if form.is_valid():
                form.save()
                try:
                    user = User.objects.get(username=temp["username"])
                    group = Group.objects.get(name="Abonné")
                    user.groups.add(group)
                    user.save()
                    return redirect(reverse('login'))
                except User.DoesNotExist:
                    error = 'user created but DoesNotExist'
                except Group.DoesNotExist:
                    error = 'group "Abonné" DoesNotExist'
            else:
                error = form.errors
    else:
        form = RegisterForm()
    context = {
        "error": error
    }
    context = {**context, **navbar_init()}
    return render(req, 'register.html', context)


def about(req):
    context = dict()
    context = {**context, **navbar_init()}
    return render(req, "about.html", context)


###############################################################################
# login_required views
###############################################################################

@login_required
def list_by_category(req, slug):
    """This view lists all articles an user can read in a category"""
    try:
        # get cat
        cat = Category.objects.get(slug=slug)
    except Category.DoesNotExist:
        cat = None
        return HttpResponseNotFound()
    # get articles
    articles = list(cat.articles.all())
    if not len(articles):
        articles = None
    # get cat.groups
    cat_group = cat.groups.all()
    if len(cat_group):
        clearance = False
        for group in cat_group:
            if has_group_perm(req, group):
                clearance = True
        if not clearance:
            # if user not in group
            return HttpResponseNotFound()
    else:
        cat_group = None
    if not has_perm_list(req, ["view_article"]):
        if has_perm_list(req, ["view_article_public"]):
            if articles is not None:
                articles = [x for x in articles if x.is_public]
        else:
            return redirect("/")
    context = {
        "articles": articles,
        "category": cat
    }
    context = {**context, **navbar_init()}
    return render(req, 'list_by_category.html', context)


@login_required
@perm_required(["add_article"])
def add_article(req):
    """This view cleans article fields from req.POST
    and add Article to DB
    """
    error = False
    if req.method == "POST":
        form_fields = clean_post_article_fields(req.POST.copy())
        # get user
        try:
            user = User.objects.get(username=req.user)
        except User.DoesNotExist:
            print(f"User.DoesNotExist : {req.user}")
            return HttpResponseNotFound()
        form_fields["writer"] = user
        cat_dict = {c: None for c in form_fields.pop("cat_list")}
        for key in cat_dict.keys():
            try:
                cat = Category.objects.get(name=key)
                cat_dict[key] = cat
            except Category.DoesNotExist:
                print(f"Category.DoesNotExist : {key}")
                return HttpResponseNotFound()
        cat_list = [val for key, val in cat_dict.items() if val is not None]
        form = AddArticleForm(form_fields)
        if form.is_valid():
            article = form.save()
            for cat in cat_list:
                cat.articles.add(article)
                cat.save()
            return redirect(article.get_absolute_url())
        else:
            error = True
        return redirect(reverse("add_article"))
    else:
        categories = list()
        for cat in Category.objects.all():
            cat_group = cat.groups.all()
            if len(cat_group):
                clearance = False
                for group in cat_group:
                    if has_group_perm(req, group):
                        clearance = True
                if clearance:
                    categories.append(cat)
            else:
                categories.append(cat)
        context = {"categories": categories}
        context = {**context, **navbar_init()}
        return render(req, "add_article.html", context)


@login_required
@perm_required(["view_article_public"])
def show_article(req, slug):
    try:
        article = Article.objects.get(slug=slug)
    except Article.DoesNotExist:
        print("ArticleDoesNotExist")
        article = None
        return HttpResponseNotFound()
    context = {
        "article": article,
        "can_be_edited_by_user": article.can_be_edited_by(req),
        "can_be_deleted_by_user": article.can_be_deleted_by(req),
        "content": unescape(article.content)
    }
    context = {**context, **navbar_init()}
    return render(req, "article.html", context)


@login_required
@perm_required(["add_comment"])
def add_comment(req):
    if req.method == "POST":
        print(req.POST)
        # get user
        try:
            user = User.objects.get(username=req.user)
        except User.DoesNotExist:
            print(f"User.DoesNotExist : {req.user}")
            return HttpResponseNotFound()
        try:
            article = Article.objects.get(slug=req.POST['article_slug'])
        except Article.DoesNotExist:
            print(f"Article.DoesNotExist : {req.POST['article_slug']}")
            return HttpResponseNotFound()
        fields = {
            "writer": user,
            "article": article,
            "content": unescape(req.POST["content"])
        }
        form = AddCommentForm(fields)
        if form.is_valid():
            comment = form.save()
        return redirect(article.get_absolute_url())


@login_required
@perm_required(['add_article'])
def edit_article(req, slug):
    # get article from slug
    try:
        article = Article.objects.get(slug=slug)
    except Article.DoesNotExist:
        return HttpResponseNotFound()
    if not article.can_be_edited_by(req):
        return HttpResponseNotFound()
    if req.method == "POST":
        form_fields = clean_post_article_fields(req.POST.copy())
        try:
            user = User.objects.get(username=req.user)
        except User.DoesNotExist:
            return HttpResponseNotFound()
        form_fields["writer"] = user
        form = EditArticleForm(form_fields, instance=article)
        article.category_set.clear()
        cat_dict = {c: None for c in form_fields.pop("cat_list")}
        for key in cat_dict.keys():
            try:
                cat = Category.objects.get(name=key)
                cat_dict[key] = cat
            except Category.DoesNotExist:
                print(f"Category.DoesNotExist : {key}")
                return HttpResponseNotFound()
        cat_list = [val for key, val in cat_dict.items() if val is not None]
        if form.is_valid():
            article = form.save()
            for cat in cat_list:
                cat.articles.add(article)
                cat.save()
            return redirect(article.get_absolute_url())
        else:
            error = True
    else:
        categories = list()
        for cat in Category.objects.all():
            cat_group = cat.groups.all()
            if len(cat_group):
                clearance = False
                for group in cat_group:
                    if has_group_perm(req, group):
                        clearance = True
                if clearance:
                    categories.append(cat)
            else:
                categories.append(cat)
        context = {
            "content": "".join(x for x in article.content.splitlines()),
            "categories": categories,
            "article": article,
        }
        context = {**context, **navbar_init()}
        return render(req, "edit_article.html", context)


@login_required
@perm_required(['del_user_articles'])
def del_article(req, slug):
    try:
        article = Article.objects.get(slug=slug)
    except Article.DoesNotExist:
        return HttpResponseNotFound()
    if not article.can_be_deleted_by(req):
        return HttpResponseNotFound()
    else:
        article.delete()
    return redirect(reverse("home"))


@login_required
def log_out(req):
    logout(req)
    return redirect(reverse("home"))
