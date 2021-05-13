from django.urls import path
from .views import CotacaoList, NotaCreate, NotaList, NotaUpdate, NotaDelete, ProventosCreate, ProventosList, ProventosUpdate, ProventosDelete, CarteiraChart
from . import views

urlpatterns = [
    path('cadastrar/ativos/', NotaCreate.as_view(), name='cadastrar-nota'),
    path('cadastrar/proventos/', ProventosCreate.as_view(), name='cadastrar-proventos'),

    path('listar/ativos/', NotaList.as_view(), name='listar-ordens'),
    path('listar/proventos/', ProventosList.as_view(), name='listar-proventos'),
    path('listar/base/cotacao/', CotacaoList.as_view(), name='listar-cotacao'),

    path('editar/ativo/<int:pk>/', NotaUpdate.as_view(), name='editar-nota'),
    path('editar/proventos/<int:pk>/', ProventosUpdate.as_view(), name='editar-provento'),

    path('excluir/nota/<int:pk>/', NotaDelete.as_view(), name='excluir-nota'),
    path('excluir/provento/<int:pk>/', ProventosDelete.as_view(), name='excluir-provento'),

    path('dashboard/carteira-chart/', CarteiraChart.as_view(), name='carteira-chart'),

    path(r'^export/xls/$', views.export_proventos_xls, name='export-proventos-xls'),
]