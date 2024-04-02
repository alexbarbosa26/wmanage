from decimal import Decimal
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.urls import reverse
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
    lancamentos = Lancamento.objects.all().filter(user=request.user.id)
    categoria_form = CategoriaForm()
    subcategoria_form = SubcategoriaForm()
    lancamento_form = LancamentoForm()

    # Filtro por data
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Filtro por data
    data_inicial = date.today().replace(day=1)
    next_month = datetime.today().replace(day=28) + timedelta(days=4)
    end_date_month = next_month - timedelta(days=next_month.day)
    data_final = end_date_month
    lancamentos = lancamentos.filter(data__range=[data_inicial, data_final])

    if start_date and end_date:
        data_inicial = datetime.strptime(start_date, "%Y-%m-%d").date()
        data_final = datetime.strptime(end_date, "%Y-%m-%d").date()
        lancamentos = lancamentos.filter(data__range=[data_inicial, data_final])
        total_receitas = lancamentos.filter(data__range=[data_inicial, data_final],categoria__tipo='1', user=request.user.id).aggregate(total=Sum('valor'))['total']
        total_despesas = lancamentos.filter(data__range=[data_inicial, data_final], categoria__tipo='2', user=request.user.id).aggregate(total=Sum('valor'))['total']

    total_receitas = lancamentos.filter(data__range=[data_inicial, data_final],categoria__tipo='1', user=request.user.id).aggregate(total=Sum('valor'))['total']
    total_despesas = lancamentos.filter(data__range=[data_inicial, data_final], categoria__tipo='2', user=request.user.id).aggregate(total=Sum('valor'))['total']

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
        descricao = request.POST.get('descricao')
        valor = request.POST.get('valor')
        data = request.POST.get('data')
        print(descricao)
        lancamento.descricao = descricao
        lancamento.valor = valor
        lancamento.data = data
        lancamento.save()
        
        messages.success(request, 'Lançamento atualizado com sucesso')
        return JsonResponse({'success': True, 'redirect_url': reverse('orcamento:index')})

    elif request.is_ajax():
        data = {
            'descricao': lancamento.descricao,
            'valor': lancamento.valor,
            'data': lancamento.data,
            # Adicione os demais campos conforme necessário
        }
        return JsonResponse(data)
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

@login_required
def dashboard_view(request):
    response = render(request, 'dashboard.html')
    response.set_cookie('user_id', request.user.id)
    return response