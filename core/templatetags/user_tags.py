from django import template
from django.contrib.auth.models import Group
import requests
from django.http import HttpRequest

from wmanage.settings.base import STATIC_ROOT, STATIC_URL, STATICFILES_DIRS

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

# Filtro para tratar a url das imagens das ações
@register.filter
def url_path(path, arg):
    try:
        url = arg+'static/img/acoes/'
        cod = path
        ext = '.png'
        url_final = url+cod+ext
        request = requests.get(url_final)
        print(request.status_code)
        if request.status_code == 200:
            return 1
        else:
            return 0
    except:
        print('não acessou')