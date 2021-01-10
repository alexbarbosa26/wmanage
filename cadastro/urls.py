from django.urls import path
from .views import NotaCreate, NotaList, NotaUpdate
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('cadastrar/ativo/', NotaCreate.as_view(), name='cadastrar-nota'), 

    path('listar/ativos/', NotaList.as_view(), name='listar-ordens'),

    path('editar/ativo/<int:pk>/', NotaUpdate.as_view(), name='editar-nota'),
]