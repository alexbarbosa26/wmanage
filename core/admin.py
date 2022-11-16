from django.contrib import admin
from .models import Ativo, Bonificacao, Desdobramento, Grupamento, Nota, Proventos, Cotacao
# from django.contrib.auth import get_user_model
# from .models import ProfileImage
# from django.contrib.auth.admin import UserAdmin
# from django.contrib.auth.models import Group

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




# User = get_user_model()


# class ProfileInline(admin.StackedInline):
#     model = ProfileImage
#     max_num = 1
#     can_delete = False

# class MyUserAdmin(UserAdmin):
#     inlines = [ProfileInline]

# # unregister old user admin
# admin.site.unregister(User)
# # admin.site.unregister(Group)

# # register new user admin that includes a UserProfile
# admin.site.register(User, MyUserAdmin)