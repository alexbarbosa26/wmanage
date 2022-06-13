from django.contrib import admin
from .models import Ativo, Bonificacao, Desdobramento, Grupamento, Nota, Proventos, Cotacao

# Register your models here.
# admin.site.register(Ativo)
admin.site.register(Nota)
admin.site.register(Proventos)
# admin.site.register(Cotacao)
admin.site.register(Desdobramento)
admin.site.register(Bonificacao)
admin.site.register(Grupamento)

@admin.register(Ativo)
class AtivoAdmin(admin.ModelAdmin):
    list_display = ('ativo','quantidade','preco_total','user')
    list_filter = ['ativo','user']

@admin.register(Cotacao)
class CotacaoAdmin(admin.ModelAdmin):
    list_display = ('acao','ativo','fechamento_ajustado','variacao_1','variacao_2','status_fechado_aberto')
    list_filter = ['ativo']
