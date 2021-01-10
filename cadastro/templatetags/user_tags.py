from django import template
from django.contrib.auth.models import Group 

register = template.Library() 

@register.filter
def has_group(user, group_name):
    group = Group.objects.filter(name=group_name)
    if group:
        group = group.first()
        return group in user.groups.all()
    else:
        return False
