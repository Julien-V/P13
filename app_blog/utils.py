#!/usr/bin/python3
# coding : utf-8

from django.contrib.auth.models import User
from django.shortcuts import redirect


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
    user, groups, user_perms = get_user_groups_perm(req)
    if user.is_superuser and check_superuser:
        print(f"[{user.username}] is superuser > {perm_list}")
        return True
    for perm in perm_list:
        search_list = [
            elem for x in user_perms for elem in x if elem.codename == perm]
        if len(search_list):
            print(f"[{user.username}] permission accepted:{perm}")
        else:
            print(f"[{user.username}] permission refused:{perm}")
            return False
    return True


def has_group_perm(req, group, check_superuser=True):
    user, groups, user_perms = get_user_groups_perm(req)
    group_perm = group.permissions.all()
    # 0 : user.is_superuser
    if user.is_superuser and check_superuser:
        print(f"[{user.username}] is superuser > {group.name}")
        return True
    # 1 : group in user's groups
    elif group in groups:
        return True
    # 2 : user has group perm
    elif has_perm_list(req, group_perm):
        return True
    else:
        return False


def get_user_groups_perm(req):
    username = req.user
    user = User.objects.get(username=username)
    groups = user.groups.all()
    user_perms = list()
    for group in groups:
        perm = group.permissions.all()
        user_perms.append(perm)
    return user, groups, user_perms
