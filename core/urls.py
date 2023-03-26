from django.urls import path
from .views import BonificacaoCreate, BonificacaoDelete, BonificacaoList, CotacaoList, Dash_Carteira_X_Bolsa, DashboardTemporal, DesdobramentoCreate, DesdobramentoDelete, DesdobramentoList, GrupamentoCreate, GrupamentoDelete, GrupamentoList, NotaCreate, NotaList, NotaUpdate, NotaDelete, ProventosCreate, ProventosList, ProventosUpdate, ProventosDelete, CarteiraChart, Export_xls
from . import views

urlpatterns = [
    path('cadastrar/ativos/', NotaCreate.as_view(), name='cadastrar-nota'),
    path('cadastrar/proventos/', ProventosCreate.as_view(), name='cadastrar-proventos'),
    path('cadastrar/desdobramentos/', DesdobramentoCreate.as_view(), name='cadastrar-desdobramento'),
    path('cadastrar/bonificacao/', BonificacaoCreate.as_view(), name='cadastrar-bonificacao'),
    path('cadastrar/grupamento/', GrupamentoCreate.as_view(), name='cadastrar-grupamento'),

    path('listar/ativos/', NotaList.as_view(), name='listar-ordens'),
    path('listar/proventos/', ProventosList.as_view(), name='listar-proventos'),
    path('listar/base/cotacao/', CotacaoList.as_view(), name='listar-cotacao'),
    path('listar/desdobramentos/', DesdobramentoList.as_view(), name='listar-desdobramento'),
    path('listar/bonficacao/', BonificacaoList.as_view(), name='listar-bonificacao'),
    path('listar/grupamento/', GrupamentoList.as_view(), name='listar-grupamento'),

    path('editar/ativo/<int:pk>/', NotaUpdate.as_view(), name='editar-nota'),
    path('editar/proventos/<int:pk>/', ProventosUpdate.as_view(), name='editar-provento'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),

    path('excluir/nota/<int:pk>/', NotaDelete.as_view(), name='excluir-nota'),
    path('excluir/provento/<int:pk>/', ProventosDelete.as_view(), name='excluir-provento'),
    path('excluir/desdobramento/<int:pk>/', DesdobramentoDelete.as_view(), name='excluir-desdobramento'),
    path('excluir/bonificacao/<int:pk>/', BonificacaoDelete.as_view(), name='excluir-bonificacao'),
    path('excluir/grupamento/<int:pk>/', GrupamentoDelete.as_view(), name='excluir-grupamento'),

    path('dashboard/carteira-chart/', CarteiraChart.as_view(), name='carteira-chart'),
    path('dashboard/proventos-chart/', views.Dashboard, name='proventos-chart'),
    path('dashboard/temporal-chart/<str:ativo>', DashboardTemporal.as_view(), name='temporal-chart'),
    path('dashboard/carteira-vs-bolsa-chart/', Dash_Carteira_X_Bolsa.as_view(), name='carteira-vs-bolsa-chart'),

    path('contact', views.contato, name='contact'),

    path('export/xls/', Export_xls.get_context_data, name='export-proventos-xls'),

]