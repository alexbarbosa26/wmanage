from django.urls import path
from .views import CotacaoList, Dash_Carteira_X_Bolsa, DashboardTemporal, DesdobramentoCreate, NotaCreate, NotaList, NotaUpdate, NotaDelete, ProventosCreate, ProventosList, ProventosUpdate, ProventosDelete, CarteiraChart, Export_xls
from . import views

urlpatterns = [
    path('cadastrar/ativos/', NotaCreate.as_view(), name='cadastrar-nota'),
    path('cadastrar/proventos/', ProventosCreate.as_view(), name='cadastrar-proventos'),
    path('cadastrar/desdobramentos/', DesdobramentoCreate.as_view(), name='cadastrar-desdobramento'),

    path('listar/ativos/', NotaList.as_view(), name='listar-ordens'),
    path('listar/proventos/', ProventosList.as_view(), name='listar-proventos'),
    path('listar/base/cotacao/', CotacaoList.as_view(), name='listar-cotacao'),

    path('editar/ativo/<int:pk>/', NotaUpdate.as_view(), name='editar-nota'),
    path('editar/proventos/<int:pk>/', ProventosUpdate.as_view(), name='editar-provento'),

    path('excluir/nota/<int:pk>/', NotaDelete.as_view(), name='excluir-nota'),
    path('excluir/provento/<int:pk>/', ProventosDelete.as_view(), name='excluir-provento'),

    path('dashboard/carteira-chart/', CarteiraChart.as_view(), name='carteira-chart'),
    path('dashboard/proventos-chart/', views.Dashboard, name='proventos-chart'),
    path('dashboard/temporal-chart/<str:ativo>', DashboardTemporal.as_view(), name='temporal-chart'),
    path('dashboard/carteira-vs-bolsa-chart/', Dash_Carteira_X_Bolsa.as_view(), name='carteira-vs-bolsa-chart'),

    path('export/xls/', Export_xls.get_context_data, name='export-proventos-xls'),
]