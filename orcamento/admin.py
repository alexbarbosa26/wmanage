from django.contrib import admin

from orcamento.models import Categoria, Lancamento

# Register your models here.

admin.site.register(Categoria)
admin.site.register(Lancamento)