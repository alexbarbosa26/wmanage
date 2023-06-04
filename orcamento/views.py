from decimal import Decimal
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from .forms import CategoriaForm, SubcategoriaForm, LancamentoForm
from .models import Categoria, Subcategoria, Lancamento
from django.db.models import Sum


def index(request):
    lancamentos = Lancamento.objects.all()
    categoria_form = CategoriaForm()
    subcategoria_form = SubcategoriaForm()
    lancamento_form = LancamentoForm()

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