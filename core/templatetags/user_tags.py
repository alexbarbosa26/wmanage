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

@register.filter(name="add_classes")
def add_classes(value, arg):

    classes = value.field.widget.attrs.get('class','')

    if classes:
        classes = classes.split(" ")
    else:
        classes = []
    
    new_classes = arg.split(" ")
    for c in new_classes:
        if c not in classes:
            classes.append(c)
    
    return value.as_widget(attrs={"class":" ".join(classes)})