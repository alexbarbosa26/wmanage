from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('categoria_modal/', views.categoria_modal, name='categoria_modal'),
    path('subcategoria_modal/', views.subcategoria_modal, name='subcategoria_modal'),
    path('lancamento_modal/', views.lancamento_modal, name='lancamento_modal'),
    path('subcategorias/', views.get_subcategorias, name='get_subcategorias'),
    path('lancamento/editar/<int:pk>/', views.editar_lancamento, name='editar_lancamento'),
    path('lancamento/excluir/<int:pk>/', views.excluir_lancamento, name='excluir_lancamento'),
]
