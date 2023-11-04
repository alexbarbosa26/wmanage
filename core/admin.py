from django.contrib import admin
from .models import Ativo, Bonificacao, Desdobramento, Grupamento, Nota, Profile, Proventos, Cotacao

@admin.register(Proventos)
class ProventosAdmin(admin.ModelAdmin):
    list_display = ('ativo','tipo_provento', 'data', 'valor', 'user')
    search_fields = ['ativo']

admin.site.register(Desdobramento)
admin.site.register(Bonificacao)
admin.site.register(Grupamento)
admin.site.register(Profile)

@admin.register(Nota)
class NotaAdmin(admin.ModelAdmin):
    list_display = ('ativo','data','quantidade','preco','tipo','user')
    search_fields = ['ativo']

@admin.register(Ativo)
class AtivoAdmin(admin.ModelAdmin):
    list_display = ('ativo','quantidade','preco_total','user')
    list_filter = ['ativo']
    search_fields = ['ativo']

@admin.register(Cotacao)
class CotacaoAdmin(admin.ModelAdmin):
    list_display = ('acao','ativo','fechamento_ajustado','variacao_1','variacao_2','status_fechado_aberto')
    list_filter = ['ativo']
    search_fields = ['ativo']