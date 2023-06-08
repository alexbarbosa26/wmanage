from django.contrib import admin

from orcamento.models import Categoria, Lancamento, Subcategoria

class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nome','tipo']
    search_fields = ['nome', 'tipo']

class SubcategoriaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'categoria']
    search_fields =['nome','categoria']

class LancamentoAdmin(admin.ModelAdmin):
    list_display = ['descricao','categoria','subcategoria','valor','data','user']
    search_fields = ['descricao','cattegoria','subcategoria','data']
# Register your models here.

admin.site.register(Categoria, CategoriaAdmin)
admin.site.register(Lancamento, LancamentoAdmin)
admin.site.register(Subcategoria, SubcategoriaAdmin)