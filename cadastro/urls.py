from django.urls import path
from .views import NotaCreate, NotaList, NotaUpdate, NotaDelete, ProventosCreate, ProventosList
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('cadastrar/ativo/', NotaCreate.as_view(), name='cadastrar-nota'),
    path('cadastros/proventos/', ProventosCreate.as_view(), name='cadastrar-proventos'),

    path('listar/ativos/', NotaList.as_view(), name='listar-ordens'),
    path('cadastro/listas/proventos/', ProventosList.as_view(), name='listar-proventos'),

    path('editar/ativo/<int:pk>/', NotaUpdate.as_view(), name='editar-nota'),
    path('excluir/nota/<int:pk>/', NotaDelete.as_view(), name='excluir-nota'),
]