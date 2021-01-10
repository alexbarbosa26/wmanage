from django.urls import path
from .views import NotaCreate
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('cadastro/nota/', NotaCreate.as_view(), name='cadastrar-nota'), 
]