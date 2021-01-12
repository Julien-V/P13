# Generated by Django 3.1.4 on 2021-01-12 22:03

from django.db import migrations

from django.template.defaultfilters import slugify

from django.conf import settings

import uuid


class CreateCategories:
    def __init__(self, apps, schema_editor):
        self.app = apps
        self.schema_editor = schema_editor
        self.old_cat_list = settings.APP_BLOG_CATEGORY_HIERARCHY.copy()
        self.cat_list = self._make_cat_list()
        self.Group = apps.get_model("auth", "Group")
        self.Category = apps.get_model("app_blog", "Category")
        self.CategoryGroup = apps.get_model("app_blog", "CategoryGroup")

    def _make_cat_list(self):
        cat_list = list()
        cat_dict_list = self.old_cat_list.copy()
        while len(cat_dict_list):
            temp = cat_dict_list.pop(0)
            cat_list.append(temp)
            if isinstance(temp, tuple):
                temp = temp[0]
            if temp["sub_cat"] is not None:
                for cat in temp["sub_cat"]:
                    cat_dict_list.append((cat, temp["name"]))
        return cat_list

    def _make_cat(self, name, parent=None):
        # create a Category object with a temporary slug
        cat_obj = self.Category.objects.create(
            name=name,
            slug=str(uuid.uuid4())
        )
        if parent is not None:
            try:
                parent_cat = self.Category.objects.get(name=parent)
                cat_obj.parent_category = parent_cat
            except self.Category.DoesNotExist:
                print("Parent cat ", parent, "DoesNotExist")
        cat_obj.save()
        # then get Category and add final slug
        try:
            cat_obj = self.Category.objects.get(name=name)
            cat_obj.slug = f"{slugify(cat_obj.name)}-{cat_obj.id}"
            cat_obj.save()
            cat_obj = self.Category.objects.get(name=name)
        except self.Category.DoesNotExist:
            print(f"[!] Category {name} DoesNotExist")
            return None
        # except ValidationError ?
        return cat_obj

    def _link_cat_group(self, cat, cat_obj):
        group_name = cat['group']
        try:
            group_obj = self.Group.objects.get(name=group_name)
            cat_group = self.CategoryGroup.objects.create(
                category=cat_obj,
                group=group_obj)
            cat_group.save()
        except self.Group.DoesNotExist:
            print(f"[!] Group {group_name} DoesNotExist ({cat})")
            return None
        return cat_group

    def run(self):
        for cat in self.cat_list:
            cat_temp = cat
            parent = None
            if isinstance(cat, tuple):
                cat_temp = cat[0]
                parent = cat[1]
            cat_obj = self._make_cat(cat_temp['name'], parent)
            if cat_temp['group'] is not None:
                self._link_cat_group(cat_temp, cat_obj)
        return self.cat_list


def create_categories(apps, schema_editor):
    cc = CreateCategories(apps, schema_editor)
    cat_list = cc.run()
    print(f"\n[*] {len(cat_list)} catégories créées.")


class Migration(migrations.Migration):

    dependencies = [
        ('app_blog', '0002_auto_20210111_1708'),
    ]

    operations = [
        migrations.RunPython(create_categories)
    ]
