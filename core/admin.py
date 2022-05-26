from django.contrib import admin
from .models import Ativo, Desdobramento, Nota, Proventos, Cotacao

# Register your models here.
admin.site.register(Ativo)
admin.site.register(Nota)
admin.site.register(Proventos)
admin.site.register(Cotacao)
admin.site.register(Desdobramento)