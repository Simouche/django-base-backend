from django import template
from django.contrib.auth.models import Group

register = template.Library()


@register.filter(name='has_group')
def has_group(user, group_name):
    """
    checks if the user belongs to a group
    :param user:
    :param group_name:
    :return:
    """
    group = Group.objects.get(name=group_name)
    return group in user.groups.all()


@register.filter(name='has_perm')
def has_perm(user, perm):
    """
    checks if the user has the perm
    :param user:
    :param perm: should be of the django's permissions' format <appname.perm_modelname> ex:"recipe.view_recipe"
    :return:
    """
    return user.has_perm(perm)


@register.filter(name='is_owner')
def is_owner(request, the_object):
    """
    checks if the current user is the object's owner
    :param request:
    :param the_object: the object must specify an OWNER_FIELD property which will contain the name of the field which
    refers to the USER object.
    :return:
    """

    return request.user == getattr(the_object, the_object.OWNER_FIELD)
