#!/usr/bin/python3
# coding : utf-8

from django.contrib.auth.models import User

from django.shortcuts import redirect

from django.utils.http import url_has_allowed_host_and_scheme


def perm_required(perm_list):
    def decorator(func):
        def decorated_func(*args, **kwargs):
            req = args[0]
            if has_perm_list(req, perm_list):
                return func(*args, **kwargs)
            else:
                return redirect("/")
        return decorated_func
    return decorator


def has_perm_list(req, perm_list, check_superuser=True):
    """This function returns True if perm_list in user permissions.

    :param req: request object
    :param perm_list: list(), permission.codename
    :param check_superuser: boolean, default=True

    :return True: user.is_superuser, perm_list in user_perms
    :return False:
    """
    user, groups, user_perms = get_user_groups_perm(req)
    if user is None:
        return False
    if user.is_superuser and check_superuser:
        return True
    user_perms_codename = [perm.codename for perm in user_perms]
    for perm in perm_list:
        if perm not in user_perms_codename:
            return False
    return True


def has_group_perm(req, group, check_superuser=True):
    """This function returns True if an user (from request object)
    has got group permissions.

    :param req: request object
    :param group: Group object
    :param check_superuser: boolean, default=True

    :return True: user.is_superuser, group in user.groups, user has the perms
    :return False:
    """
    user, groups, user_perms = get_user_groups_perm(req)
    group_perm = [perm.codename for perm in group.permissions.all()]
    if user:
        # 0 : user.is_superuser
        if user.is_superuser and check_superuser:
            return True
        # 1 : group in user's groups
        elif group in groups:
            return True
        # 2 : user has group perm
        elif has_perm_list(req, group_perm):
            return True
        else:
            return False
    else:
        return False


def get_user_groups_perm(req):
    """This function returns a user object, a QueryList of Group,
    and a list of user permissions.

    :param req: request object

    :return None, None, None: User.DoesNotExist
    :return user, groups, user_perms: User, QueryList<Group>, [Permissions,]
    """
    username = req.user
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        print("get_user_groups_perm : User.DoesNotExist")
        return None, None, None
    groups = user.groups.all()
    user_perms = list()
    for group in groups:
        perms = group.permissions.all()
        for perm in perms:
            user_perms.append(perm)
    return user, groups, user_perms


def redirect_next(req):
    """This function checks"""
    nxt = req.GET.get("next", None)
    print(nxt)
    if nxt is None:
        return redirect("/")
    elif url_has_allowed_host_and_scheme(
            url=nxt, allowed_hosts={req.get_host()},
            require_https=req.is_secure()):
        return redirect(nxt)
    else:
        return redirect("/")
