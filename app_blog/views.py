#!/usr/bin/python3
# coding : utf-8

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group

from django.http import HttpResponseNotFound

from django.shortcuts import render, redirect, reverse

from html import unescape

from app_blog.forms import ConnectionForm, RegisterForm
from app_blog.forms import AddArticleForm, EditArticleForm, AddCommentForm

from app_blog.models import Article, Category, Comment, Profile

from app_blog.utils import has_perm_list, perm_required
from app_blog.utils import redirect_next
from app_blog.utils import clean_post_article_fields


def navbar_init(req):
    """Initializes navbar

    :param req: request object

    :return context: dict()
    """
    context = {
        "navbar_cat_list": list(),
        "navbar_sub_cat_list": list(),
        "dashboard_access": has_perm_list(req, ["view_category_all"])
    }
    categories = Category.objects.all().order_by("id")
    for cat in categories:
        if cat.can_be_viewed_by(req):
            if not cat.parent_category:
                context["navbar_cat_list"].append(cat)
            else:
                context["navbar_sub_cat_list"].append(cat.name)
    return context


###############################################################################
# Public views
###############################################################################


def index(req):
    context = dict()
    context = {**context, **navbar_init(req)}
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
                messages.success(req, f"Bonjour {user.username} !")
                return redirect_next(req)
            else:
                error = True
    else:
        form = ConnectionForm()
    context = {
        "error": error,
        "form": form
    }
    context = {**context, **navbar_init(req)}
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
                    profile = Profile(user=user)
                    profile.save()
                    messages.success(
                        req, f"Nouvel utilisateur {user.username} ajouté.")
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
    context = {**context, **navbar_init(req)}
    return render(req, 'register.html', context)


def about(req):
    context = dict()
    context = {**context, **navbar_init(req)}
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
    if not cat.can_be_viewed_by(req):
        messages.error(
            req,
            "Vous n'avez pas le droit de voir cette catégorie."
        )
        return HttpResponseNotFound()
    # get articles
    articles = list(cat.articles.all())
    if not len(articles):
        articles = None
    else:
        articles = [x for x in articles if x.can_be_viewed_by(req)]
    context = {
        "articles": articles,
        "category": cat
    }
    context = {**context, **navbar_init(req)}
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
        user = User.objects.get(username=req.user)
        form_fields["writer"] = user
        cat_dict = {c: None for c in form_fields.pop("cat_list")}
        for key in cat_dict.keys():
            try:
                cat = Category.objects.get(name=key)
                cat_dict[key] = cat
            except Category.DoesNotExist:
                messages.error(req, f"Category.DoesNotExist : {key}")
                return HttpResponseNotFound()
        cat_list = [val for key, val in cat_dict.items() if val is not None]
        form = AddArticleForm(form_fields)
        if form.is_valid():
            article = form.save()
            for cat in cat_list:
                cat.articles.add(article)
                cat.save()
            user.profile.update_meters()
            messages.success(req, 'Article ajouté !')
            return redirect(article.get_absolute_url())
        else:
            error = form.errors
    categories = list()
    for cat in Category.objects.all().order_by("id"):
        if cat.can_be_viewed_by(req):
            categories.append(cat)
    context = {
        "categories": categories,
        "error": error
    }
    context = {**context, **navbar_init(req)}
    return render(req, "add_article.html", context)


@login_required
@perm_required(["view_article_public"])
def show_article(req, slug):
    """This views gets an article from its slug,
    checks if current user can view this article and renders it.
    """
    try:
        article = Article.objects.get(slug=slug)
    except Article.DoesNotExist:
        return HttpResponseNotFound()
    if not article.can_be_viewed_by(req):
        return HttpResponseNotFound()
    comments = [{
        "comment": comment,
        "can_be_deleted": comment.can_be_deleted_by(req),
    } for comment in article.comment_set.all()]
    context = {
        "article": article,
        "can_be_edited_by_user": article.can_be_edited_by(req),
        "can_be_deleted_by_user": article.can_be_deleted_by(req),
        "content": unescape(article.content),
        "comments": comments
    }
    context = {**context, **navbar_init(req)}
    return render(req, "article.html", context)


@login_required
@perm_required(['add_article'])
def edit_article(req, slug):
    error = False
    # get article from slug
    try:
        article = Article.objects.get(slug=slug)
    except Article.DoesNotExist:
        messages.error(req, "Article introuvable.")
        return HttpResponseNotFound()
    if not article.can_be_edited_by(req):
        messages.error(
            req, "Vous n'avez pas le droit de modifier cet article.")
        return HttpResponseNotFound()
    if req.method == "POST":
        form_fields = clean_post_article_fields(req.POST.copy())
        user = User.objects.get(username=req.user)
        form_fields["writer"] = user
        form = EditArticleForm(form_fields, instance=article)
        article.category_set.clear()
        cat_dict = {c: None for c in form_fields.pop("cat_list")}
        for key in cat_dict.keys():
            try:
                cat = Category.objects.get(name=key)
                cat_dict[key] = cat
            except Category.DoesNotExist:
                messages.error(req, f"Catégorie introuvable {key}")
                return HttpResponseNotFound()
        cat_list = [val for key, val in cat_dict.items() if val is not None]
        if form.is_valid():
            article = form.save()
            for cat in cat_list:
                cat.articles.add(article)
                cat.save()
            user.profile.update_meters()
            messages.success(req, "Article modifié !")
            return redirect(article.get_absolute_url())
        else:
            error = form.errors
    categories = list()
    for cat in Category.objects.all().order_by("id"):
        if cat.can_be_viewed_by(req):
            categories.append(cat)
    context = {
        "content": "".join(x for x in article.content.splitlines()),
        "categories": categories,
        "article": article,
        "error": error
    }
    context = {**context, **navbar_init(req)}
    return render(req, "edit_article.html", context)


@login_required
@perm_required(['del_user_articles'])
def del_article(req, slug):
    try:
        article = Article.objects.get(slug=slug)
    except Article.DoesNotExist:
        messages.error(req, f"Impossible de trouver l'article {slug}")
        return HttpResponseNotFound()
    if not article.can_be_deleted_by(req):
        messages.error(
            req, "Vous n'avez pas le droit de supprimer cet article.")
        return HttpResponseNotFound()
    else:
        user = article.writer
        article.delete()
        user.profile.update_meters()
        messages.success(req, "Article supprimé.")
    return redirect(reverse("home"))


@login_required
@perm_required(["add_comment"])
def add_comment(req):
    if req.method == "POST":
        # get user
        user = User.objects.get(username=req.user)
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
            form.save()
            user.profile.update_meters()
        return redirect(article.get_absolute_url())


@login_required
@perm_required(['del_user_comment'])
def del_comment(req):
    try:
        id_comment = req.GET["id"]
    except KeyError:
        messages.error(
            req, "Précisez le commentaire à supprimer"
        )
        return HttpResponseNotFound()
    try:
        comment = Comment.objects.get(id=id_comment)
    except Comment.DoesNotExist:
        messages.error(
            req, f"Impossible de trouver le commentaire id={id_comment}")
        return HttpResponseNotFound()
    article_url = comment.article.get_absolute_url()
    if not comment.can_be_deleted_by(req):
        messages.error(
            req, "Vous n'avez pas le droit de supprimer ce commentaire.")
        return HttpResponseNotFound()
    else:
        user = comment.writer
        comment.delete()
        user.profile.update_meters()
        messages.success(req, "Commentaire supprimé.")
    return redirect(article_url)


@login_required
@perm_required(['view_category_all'])
def dashboard(req):
    users = [{
        "user": user,
        "groups": "".join(f"{group.name};" for group in user.groups.all())
    } for user in User.objects.all()]
    articles = [{
        "article": article,
        "can_be_edited": article.can_be_edited_by(req),
        "can_be_deleted": article.can_be_deleted_by(req),
        "categories": "".join(
            f"{cat.name};" for cat in article.category_set.all()
        )
    } for article in Article.objects.all()]
    comments = [{
        "comment": comment,
        "can_be_deleted": comment.can_be_deleted_by(req),
    } for comment in Comment.objects.all()]
    context = {
        "users": users,
        "articles": articles,
        "comments": comments
    }
    context = {**context, **navbar_init(req)}
    return render(req, "dashboard.html", context)


@login_required
def log_out(req):
    logout(req)
    messages.success(req, "Vous avez bien été déconnecté de SéezLangues.")
    return redirect(reverse("home"))
