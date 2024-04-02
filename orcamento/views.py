from decimal import Decimal
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from .forms import CategoriaForm, SubcategoriaForm, LancamentoForm
from .models import Categoria, Subcategoria, Lancamento
from django.db.models import Sum
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from datetime import datetime
from django.shortcuts import render
from django_plotly_dash import DjangoDash
import plotly.graph_objs as go
from dash import html, dcc
from dash.dependencies import Input, Output
from .dash_app import app
from .dash_app2 import app
from django.contrib.auth.decorators import login_required
from django_plotly_dash.models import DashApp
import os

def get_last_util_day(date_obj):
    last_day = date_obj.replace(day=1) + relativedelta(months=1) - relativedelta(days=25)
    while last_day.weekday() >= 5:
        last_day -= relativedelta(days=1)
    return last_day

def index(request):
    lancamentos = Lancamento.objects.all()
    categoria_form = CategoriaForm()
    subcategoria_form = SubcategoriaForm()
    lancamento_form = LancamentoForm()

    # Filtro por data
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Filtro por data
    data_inicial = date.today().replace(day=1) + timedelta(days=4)
    data_final = get_last_util_day(data_inicial + relativedelta(months=1))
    lancamentos = lancamentos.filter(data__range=[data_inicial, data_final])

    if start_date and end_date:
        data_inicial = datetime.strptime(start_date, "%Y-%m-%d").date()
        data_final = datetime.strptime(end_date, "%Y-%m-%d").date()
        lancamentos = lancamentos.filter(data__range=[data_inicial, data_final])

    total_receitas = lancamentos.filter(categoria__tipo='1').aggregate(total=Sum('valor'))['total']
    total_despesas = lancamentos.filter(categoria__tipo='2').aggregate(total=Sum('valor'))['total']

    if not total_receitas:
        total_receitas = Decimal(0.00)
    if not total_despesas:
        total_despesas = Decimal(0.00)

    total_saldo = total_receitas - total_despesas    
    
    context = {
        'lancamentos': lancamentos,
        'categoria_form': categoria_form,
        'subcategoria_form': subcategoria_form,
        'lancamento_form': lancamento_form,
        'total_receitas': total_receitas or Decimal(0.00),
        'total_despesas': total_despesas or Decimal(0.00),
        'total_saldo':total_saldo,
        'data_inicial':data_inicial,
        'data_final':data_final,
    }
    return render(request, 'index.html', context)


def categoria_modal(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoria adicionada com sucesso')
            return redirect('orcamento:index')
        else:
            messages.error(request, 'Erro ao adicionar categoria')
    else:
        form = CategoriaForm()
    return render(request, 'index.html', {'categoria_form': form})


def subcategoria_modal(request):
    if request.method == 'POST':
        form = SubcategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subcategoria adicionada com sucesso.')
            return redirect('orcamento:index')
        else:
            messages.error(request, 'Erro ao adicionar subcategoria.')
    else:
        form = SubcategoriaForm()
    return render(request, 'orcamento_app/index.html', {'subcategoria_form': form})


def lancamento_modal(request):
    if request.method == 'POST':
        form = LancamentoForm(request.POST)
        if form.is_valid():            
            lancamento = form.save(commit=False)
            lancamento.user = request.user  # Associar a instância do usuário ao lançamento
            lancamento.save()
            messages.success(request, 'Lançamento adicionado com sucesso.')
            return redirect('orcamento:index')
        else:
            messages.error(request, 'Erro ao adicionar lançamento.')
    else:
        form = LancamentoForm(instance=request.user)
    return render(request, 'index.html', {'categoria_form': form})

def get_subcategorias(request):
    categoria_id = request.GET.get('categoria_id')
    subcategorias = Subcategoria.objects.filter(categoria_id=categoria_id)
    data = [{'id': subcategoria.id, 'nome': subcategoria.nome} for subcategoria in subcategorias]
    return JsonResponse(data, safe=False)

def editar_lancamento(request, pk):
    lancamento = get_object_or_404(Lancamento, pk=pk)
    if request.method == 'POST':
        form = LancamentoForm(request.POST, instance=lancamento)
        if form.is_valid():
            form.save()
            messages.success(request, 'Lançamento atualizado com sucesso')
            return redirect('orcamento:index')
        else:
            messages.error(request, 'Erro ao atualizar')
    else:
        form = LancamentoForm(instance=lancamento)
    return render(request, 'editar_lancamento.html', {'form': form, 'lancamento': lancamento})

def excluir_lancamento(request, pk):
    lancamento = get_object_or_404(Lancamento, pk=pk)
    if request.method == 'POST':
        lancamento.delete()
        messages.success(request, 'Lançamento excluido com sucesso')
        return redirect('orcamento:index')
    else:
        messages.error(request, 'Erro ao excluir')
    return render(request, 'excluir_lancamento.html', {'lancamento': lancamento})


# def dashboard_view(request):
#     # Crie uma instância do DjangoDash
#     app = DjangoDash('Simple')

#     # Defina o layout da aplicação Dash
#     app.layout = html.Div(children=[
#         html.H1('Relação de Modelos'),
#         dcc.Graph(id='graph'),
#     ])

#     # Crie uma função de callback para atualizar o gráfico
#     @app.callback(
#         Output('graph', 'figure'),
#         [Input('graph', 'id')]
#     )
#     def update_graph(input_value):
#         # Obtenha os dados para o gráfico a partir do seu modelo
#         categorias = Categoria.objects.filter(lancamento__isnull=False).distinct()
#         receitas = []
#         despesas = []

#         for categoria in categorias:
#             lancamentos = Lancamento.objects.filter(categoria=categoria)
#             total = sum(lancamento.valor for lancamento in lancamentos)

#             if categoria.tipo == '1':
#                 receitas.append(total)
#             elif categoria.tipo == '2':
#                 despesas.append(total)

#         # Crie o gráfico de barras
#         trace1 = go.Bar(
#             x=[categoria.nome for categoria in categorias if categoria.tipo == '1'],
#             y=receitas,
#             name='Receitas'
#         )
#         trace2 = go.Bar(
#             x=[categoria.nome for categoria in categorias if categoria.tipo == '2'],
#             y=despesas,
#             name='Despesas'
#         )

#         data = [trace1, trace2]
#         layout = go.Layout(
#             barmode='group',
#             title='Relação de Receitas e Despesas por Categoria'
#         )

#         fig = go.Figure(data=data, layout=layout)

#         return fig

#     return render(request, 'dashboard.html')
@login_required
def dashboard_view(request):
    response = render(request, 'dashboard.html')
    response.set_cookie('user_id', request.user.id)
    return response