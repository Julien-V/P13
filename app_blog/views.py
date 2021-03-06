#!/usr/bin/python3
# coding : utf-8

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group

from django.db.models import Subquery

from django.http import HttpResponseNotFound, HttpResponse

from django.shortcuts import render, redirect, reverse

from html import unescape
import logging

from app_blog.forms import ConnectionForm, RegisterForm
from app_blog.forms import AddArticleForm, EditArticleForm, AddCommentForm

from app_blog.models import Article, Category, Comment, Profile

from app_blog.utils import has_perm_list, perm_required
from app_blog.utils import redirect_next
from app_blog.utils import clean_post_article_fields


###############################################################################
# Logs
###############################################################################
logger = logging.getLogger(__name__)
logger.setLevel(20)


###############################################################################
# navbar_init
###############################################################################
def navbar_init(req):
    """Initializes navbar

    :param req: request object

    :return context: dict()
    """
    context = {
        "navbar_cat_list": list(),
        "navbar_sub_cat_list": list(),
        "dashboard_access": False,
        "can_add_article": False
    }
    if req.user.is_authenticated:
        # get user
        user = User.objects.get(username=req.user)
        # get profile url
        try:
            context['profile_link'] = user.profile.get_absolute_url()
        except Profile.DoesNotExist:
            profile = Profile(user=user)
            profile.save()
            messages.success(
                req, f"Profil créé pour l'utilisateur {user.username}"
            )
            user.refresh_from_db(fields=["profile"])
            context['profile_link'] = user.profile.get_absolute_url()
        # get categories
        categories = user.profile.get_visible_categories().order_by('id')
        for cat in categories:
            if not cat.parent_category:
                context["navbar_cat_list"].append(cat)
            else:
                context["navbar_sub_cat_list"].append(cat.name)
        can_dict = has_perm_list(
            req, ["view_category_all", "add_article"], return_dict=True
        )
        # dashboard access
        context["dashboard_access"] = can_dict["view_category_all"]
        # add article button
        context["can_add_article"] = can_dict["add_article"]
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
                try:
                    user_obj = User.objects.get(username=username)
                    if not user_obj.is_active:
                        error = "Compte utilisateur désactivé."
                except User.DoesNotExist:
                    error = "Utilisateur inconnu ou mauvais de mot de passe."
                messages.error(
                    req, error
                )
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
        fields = req.POST.copy()
        form = RegisterForm(fields)
        if form.is_valid():
            form.save()
            try:
                user = User.objects.get(username=fields["username"])
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
            messages.error(req, error)
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
    user = User.objects.get(username=req.user)
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
    articles = list(
        cat.articles.filter(
            category__in=user.profile.get_visible_categories(only_id=True)
        ).distinct()
    )
    if not len(articles):
        articles = None
    context = {
        "articles": articles,
        "category": cat
    }
    if has_perm_list(req, ["view_anonymous_article"]):
        context["can_view_anonymous_article"] = True
    context = {**context, **navbar_init(req)}
    return render(req, 'list_by_category.html', context)


@login_required
@perm_required(["add_article"])
def add_article(req):
    """This view cleans article fields from req.POST
    and add Article to DB
    """
    error = False
    # get user
    user = User.objects.get(username=req.user)
    # get visible cat
    visible_cat = list()
    for cat in user.profile.get_visible_categories().order_by("id"):
        visible_cat.append(cat)
    if req.method == "POST":
        form_fields = clean_post_article_fields(req.POST.copy())
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
                if cat in visible_cat:
                    cat.articles.add(article)
                    cat.save()
                else:
                    messages.warn(
                        req, f"Impossible d'ajouter l'article dans {cat.name}")
            user.profile.update_meters()
            messages.success(req, 'Article ajouté !')
            return redirect(article.get_absolute_url())
        else:
            error = form.errors
    context = {
        "categories": visible_cat,
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
    user = User.objects.get(username=req.user)
    try:
        article = Article.objects.get(slug=slug)
    except Article.DoesNotExist:
        return HttpResponseNotFound()
    # reducing number of db transaction :
    is_owner = user == article.writer
    perm_list = [
        "change_users_articles",
        "del_users_articles",
        "del_users_comment"
    ]
    has_perm = has_perm_list(req, perm_list, return_dict=True)
    can_be_edited = is_owner or has_perm["change_users_articles"]
    can_be_deleted = is_owner or has_perm["del_users_articles"]
    can_del_comments = has_perm["del_users_comment"]
    if not user.is_superuser:
        user_cat = Category.objects.filter(
            groups__in=Subquery(
                user.groups.all().only('id')
            )
        ).distinct()
        article_cat = list(article.category_set.all())
        clearance_list = [
            cat in list(user_cat) for cat in article_cat
        ]
    else:
        clearance_list = [True]
    if False in clearance_list:
        messages.error(
            req,
            "Vous n'avez pas le droit de lire cet article.")
        return HttpResponseNotFound()
    comments = [{
        "comment": comment,
        "can_be_deleted": comment.writer == is_owner or can_del_comments,
    } for comment in article.comment_set.all()]
    context = {
        "article": article,
        "can_be_edited_by_user": can_be_edited,
        "can_be_deleted_by_user": can_be_deleted,
        "content": unescape(article.content),
        "comments": comments
    }
    if has_perm_list(req, ["view_anonymous_article"]):
        context["can_view_anonymous_article"] = True
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
    user = User.objects.get(username=req.user)
    # get visible cat
    visible_cat = list()
    for cat in user.profile.get_visible_categories().order_by("id"):
        visible_cat.append(cat)
    if req.method == "POST":
        form_fields = clean_post_article_fields(req.POST.copy())
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
                if cat in visible_cat:
                    cat.articles.add(article)
                    cat.save()
                else:
                    messages.warn(
                        req, f"Impossible d'ajouter l'article dans {cat.name}")
            user.profile.update_meters()
            messages.success(req, "Article modifié !")
            return redirect(article.get_absolute_url())
        else:
            error = form.errors
    context = {
        "content": "".join(x for x in article.content.splitlines()),
        "categories": visible_cat,
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
    perm_list = [
        "change_users_articles",
        "del_users_articles",
        "del_users_comment",
        "change_group",
        "block_users",
        "view_anonymous_article"
    ]
    can_dict = has_perm_list(
        req, perm_list, return_dict=True
    )
    can_edit_users_article = can_dict["change_users_articles"]
    can_del_users_article = can_dict["del_users_articles"]
    can_del_users_comment = can_dict["del_users_comment"]
    can_change_groups = can_dict["change_group"]
    can_block_users = can_dict["block_users"]
    can_view_anon_article = can_dict["view_anonymous_article"]
    users = [{
        "user": user,
        "groups": "".join(f"{group.name};" for group in user.groups.all()),
    } for user in User.objects.all()]
    articles = [{
        "article": article,
        "can_be_edited": can_edit_users_article,
        "can_be_deleted": can_del_users_article,
        "categories": "".join(
            f"{cat.name};" for cat in article.category_set.all()
        )
    } for article in Article.objects.all()]
    comments = [{
        "comment": comment,
        "can_be_deleted": can_del_users_comment,
    } for comment in Comment.objects.all()]
    context = {
        "users": users,
        "can_change_groups": can_change_groups,
        "groups": Group.objects.all(),
        "can_block": can_block_users,
        "articles": articles,
        "comments": comments,
        "can_view_anonymous_article": can_view_anon_article
    }
    context = {**context, **navbar_init(req)}
    return render(req, "dashboard.html", context)


@login_required
def show_profile(req, username):
    user_req = User.objects.get(username=req.user)
    try:
        user_obj = User.objects.get(username=username)
        user_obj.profile
    except User.DoesNotExist:
        messages.error(
            req, f"Impossible de trouver l'utilisateur {username}.")
        return HttpResponseNotFound()
    except Profile.DoesNotExist:
        messages.error(
            req,
            f"Impossible de trouver le profil de l'utilisateur {username}"
        )
        return HttpResponseNotFound()
    own_profile = user_obj == user_req
    perm_list = [
        "change_users_articles",
        "del_users_articles",
        "del_users_comment",
        "change_group",
        "block_users",
        "view_anonymous_article"
    ]
    can_dict = has_perm_list(
        req, perm_list, return_dict=True
    )
    can_edit_users_article = can_dict["change_users_articles"]
    can_del_users_article = can_dict["del_users_articles"]
    can_del_users_comment = can_dict["del_users_comment"]
    can_change_groups = can_dict["change_group"]
    can_block_users = can_dict["block_users"]
    can_view_anon_article = can_dict["view_anonymous_article"]
    # get articles
    if user_req.is_superuser:
        user_req_categories = Category.objects.all()
        articles = Article.objects.filter(writer=user_obj)
    else:
        user_req_categories = Category.objects.filter(
            groups__in=Subquery(
                user_req.groups.all().only('id')
            )
        ).distinct()
        articles = Article.objects.filter(
            writer=user_obj,
            category__in=user_req_categories
        ).distinct()
    # transform QuerySet in a list of dict allowing us to use
    # Article methods
    articles = [{
        "article": article,
        "can_be_edited": can_edit_users_article or own_profile,
        "can_be_deleted": can_del_users_article or own_profile,
        "categories": "".join(
            f"{cat.name};" for cat in article.category_set.all()
        )
    } for article in articles]
    # get comments
    comments = Comment.objects.filter(writer=user_obj)
    # transform QuerySet in a list of dict allowing us to use
    # comments methods
    comments = [{
        "comment": comment,
        "can_be_deleted": can_del_users_comment or own_profile,
    } for comment in comments if comment.article.category_set.all()]
    # context
    context = {
        "can_edit_profile": own_profile,
        "user_obj": user_obj,
        "can_change_groups": can_change_groups,
        "can_block": can_block_users,
        "can_view_anonymous_article": can_view_anon_article or own_profile,
        "groups": Group.objects.all(),
    }

    class Req:
        user = user_obj.username

    if has_perm_list(Req, ['add_article']) and len(articles):
        context["articles"] = articles
        context["can_edit_articles"] = can_edit_users_article
        context["can_delete_articles"] = can_del_users_article
    if has_perm_list(Req, ['add_comment']) and len(comments):
        context["comments"] = comments
        context["can_delete_comments"] = can_del_users_comment

    context = {**context, **navbar_init(req)}
    return render(req, "profile.html", context)


@login_required
@perm_required(['change_group'])
def change_groups(req):
    if req.method == "POST":
        try:
            username = req.POST["username"]
            user = User.objects.get(username=username)
        except KeyError as e:
            messages.error(
                req,
                "Impossible de changer le groupe sans le nom d'utilisateur."
            )
            messages.error(req, str(e))
            return redirect(reverse('dashboard'))
        except User.DoesNotExist:
            messages.error(
                req,
                f"Impossible de trouver l'utilisateur : {username}"
            )
            return redirect(reverse('dashboard'))
        group_name_list = [group.name for group in Group.objects.all()]
        post_keys = req.POST.keys()
        group_list = [key for key in post_keys if key in group_name_list]
        group_obj_list = list()
        for name in group_list:
            group_obj = Group.objects.get(name=name)
            group_obj_list.append(group_obj)
        group_obj_list = sorted(group_obj_list, key=lambda i: i.name)
        user.groups.clear()
        user.groups.add(*group_obj_list)
        response = "".join(f"{group.name};" for group in group_obj_list)
        response = str(user.id) + "/" + response
        return HttpResponse(response)


@login_required
@perm_required(['delete_user'])
def block(req):
    if req.method == "GET":
        if "username" in req.GET.keys():
            username = req.GET["username"]
            try:
                user_obj = User.objects.get(username=username)
            except User.DoesNotExist:
                messages.error(
                    req, f"Impossible de trouver l'utilisateur {username}")
                return HttpResponseNotFound()
            # False : True is False
            # True : False is False
            user_obj.is_active = user_obj.is_active is False
            user_obj.save()
            return HttpResponse(f"{username}/{user_obj.is_active}")


@login_required
def log_out(req):
    logout(req)
    messages.success(req, "Vous avez bien été déconnecté de SéezLangues.")
    return redirect(reverse("home"))
