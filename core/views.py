from datetime import datetime
from core.forms import BonificacaoForm, DateForm, DesdobramentoForm
from .models import Ativo, Bonificacao, Desdobramento, Nota, Proventos, Cotacao
from decimal import Decimal
from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView
from django.views.generic import TemplateView
from django.db.models import Count, Sum
from bootstrap_datepicker_plus import DatePickerInput
from braces.views import  GroupRequiredMixin
import xlwt
from django.http import HttpResponse
import locale
import requests
from bs4 import BeautifulSoup
import plotly.express as px
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd

# Set Locale
locale.setlocale(locale.LC_ALL, 'pt_BR')

# Create
class NotaCreate(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    login_url = reverse_lazy('account_login')
    model = Nota
    fields = (
        'ativo',
        'quantidade',
        'preco',
        'data',
        'tipo',
        'identificador',
        'corretagem',
        'emolumentos',
        'tx_liquida_CBLC',
        'IRRF_Final',
        'Lucro_Day_Trade',
        'IRRF_Day_Trade',
        'corretora',
    )   
    template_name = 'cadastros/form.html'
    success_url = reverse_lazy('listar-ordens')
    success_message = "%(ativo)s registrado com sucesso!"

    def form_valid(self, form):
        ativo_reg = Ativo.objects.values().filter(ativo__icontains=form.cleaned_data['ativo'], user=self.request.user)
        ativo_reg = list(ativo_reg)
        cotacao_reg = Cotacao.objects.values().filter(ativo__icontains=form.cleaned_data['ativo'])
        cotacao_reg = list(cotacao_reg)        

        # Se o ativo for null e a tentativa for uma venda
        if not ativo_reg and form.cleaned_data['tipo'] == 'V' and form.cleaned_data['preco']> 0:
            context ={
                'message':'Não foi possível registrar sua ordem, por favor verifique a quantidade correta informada.'
            }
            return render(self.request, 'error.html', context)
        # Se não existir cotação e ativo e a quantidade e preço maior que 0 para a  compra será então cadastre ativo e cotação
        elif not ativo_reg and form.cleaned_data['tipo'] == 'C' and form.cleaned_data['quantidade'] > 0 and not cotacao_reg and form.cleaned_data['preco'] > 0:
            Ativo.objects.create(ativo=form.cleaned_data['ativo'],  quantidade=form.cleaned_data['quantidade'], preco_total=form.cleaned_data['quantidade']*form.cleaned_data['preco'], user=self.request.user)
            Cotacao.objects.create(acao=form.cleaned_data['identificador'], ativo=form.cleaned_data['ativo'])
        # se não existir ativo, mas tem cotação na compra e preço maior que 0 então cadastre apenas ativo
        elif not ativo_reg and form.cleaned_data['tipo'] == 'C' and form.cleaned_data['quantidade'] > 0 and cotacao_reg and form.cleaned_data['preco'] > 0:
            Ativo.objects.create(ativo=form.cleaned_data['ativo'],  quantidade=form.cleaned_data['quantidade'], preco_total=form.cleaned_data['quantidade']*form.cleaned_data['preco'], user=self.request.user)      
        # Se não existir cotação na compra e a quantidade e preço maior que 0 então some a quantidade e preço com o existente depois cadastre noa tivo e tambem a cotação
        elif form.cleaned_data['tipo'] == 'C' and form.cleaned_data['quantidade'] > 0 and not cotacao_reg and form.cleaned_data['preco'] > 0:
            ativo_reg[0]['quantidade'] = ativo_reg[0]['quantidade'] + form.cleaned_data['quantidade']
            ativo_reg[0]['preco_total'] = ativo_reg[0]['preco_total'] + (form.cleaned_data['quantidade']*form.cleaned_data['preco'])
            Ativo.objects.filter(ativo=form.cleaned_data['ativo'], user=self.request.user).update(ativo=form.cleaned_data['ativo'], quantidade=ativo_reg[0]['quantidade'], preco_total=ativo_reg[0]['preco_total'], user=self.request.user)
            Cotacao.objects.create(acao=form.cleaned_data['identificador'], ativo=form.cleaned_data['ativo'])
        # Se existir cotação na compra e a quantidade e preço maior que 0 então some a quantidade e preço com o existente depois cadastre o ativo
        elif form.cleaned_data['tipo'] == 'C' and form.cleaned_data['quantidade'] > 0 and cotacao_reg and form.cleaned_data['preco'] > 0:
            ativo_reg[0]['quantidade'] = ativo_reg[0]['quantidade'] + form.cleaned_data['quantidade']
            ativo_reg[0]['preco_total'] = ativo_reg[0]['preco_total'] + (form.cleaned_data['quantidade']*form.cleaned_data['preco'])
            Ativo.objects.filter(ativo=form.cleaned_data['ativo'], user=self.request.user).update(ativo=form.cleaned_data['ativo'], quantidade=ativo_reg[0]['quantidade'], preco_total=ativo_reg[0]['preco_total'], user=self.request.user)
        # Se a venda for menor do que a existente e preço maior que 0 então some a quantidade e preço existente depois cadastre o ativo
        elif form.cleaned_data['tipo'] == 'V' and form.cleaned_data['quantidade'] <= ativo_reg[0]['quantidade'] and form.cleaned_data['quantidade'] > 0 and form.cleaned_data['preco'] > 0:
            ativo_reg[0]['quantidade'] = ativo_reg[0]['quantidade'] - form.cleaned_data['quantidade']
            ativo_reg[0]['preco_total'] = ativo_reg[0]['preco_total'] - (form.cleaned_data['quantidade']*form.cleaned_data['preco'])
            Ativo.objects.filter(ativo=form.cleaned_data['ativo'], user=self.request.user).update(ativo=form.cleaned_data['ativo'], quantidade=ativo_reg[0]['quantidade'], preco_total=ativo_reg[0]['preco_total'], user=self.request.user)

        else:
            context ={
                'message':'Ordem não registrada, pois a quantidade informada ou o preço não é compatível com o que você possui em carteira.'
            }
            return render(self.request, 'error.html', context)

        return super().form_valid(form)
    
    def get_success_message(self, cleaned_data):
        return self.success_message % dict(
            cleaned_data,
            ativo=self.object.ativo,
        )    

    def get_form(self):
        form = super().get_form()
        form.instance.user = self.request.user        
        #  form.fields['ativo'].widget.attrs['placeholder'] = 'MGLU3',
        form.fields['data'].widget = DatePickerInput(format='%d/%m/%Y',
         options={'locale':'pt-br'}
        )
        return form

# List
class NotaList(LoginRequiredMixin, ListView):
    login_url = reverse_lazy('account_login')
    model = Nota
    template_name = 'listar/ordens.html'

    def get_queryset(self):
        self.object_list = Nota.objects.filter(user=self.request.user).order_by('-data')
        return self.object_list


# Delete
class NotaDelete(GroupRequiredMixin, LoginRequiredMixin, DeleteView):
    login_url = reverse_lazy('account_login')
    group_required = u'Administrador'
    model = Nota
    template_name = 'cadastros/form-excluir.html'
    success_url = reverse_lazy('listar-ordens')
    success_message = "%(ativo)s deletado com sucesso!"
    
    def delete(self, request, *args, **kwargs):
        nota = Nota.objects.filter(user=self.request.user, id=kwargs['pk'])
        ativo = Ativo.objects.filter(user=self.request.user, ativo=nota[0].ativo)

        ativo = list(ativo)
        nota = list(nota)
        if nota[0].tipo == 'C' or nota[0].tipo == 'B':
            qtd_ajustada = ativo[0].quantidade - nota[0].quantidade
            preco_ajustado = ativo[0].preco_total - nota[0].total_compra
        else:
            qtd_ajustada = ativo[0].quantidade + nota[0].quantidade
            preco_ajustado = ativo[0].preco_total + nota[0].total_compra

        Ativo.objects.filter(user=self.request.user, ativo=nota[0].ativo).update(quantidade=qtd_ajustada, preco_total=preco_ajustado)

        return super(NotaDelete, self).delete(request, *args, **kwargs)

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(
            cleaned_data,
            ativo=self.object.ativo,
        )


# Updates
class NotaUpdate(LoginRequiredMixin,SuccessMessageMixin, UpdateView):
    login_url = reverse_lazy('account_login')
    model = Nota
    fields = [
        'ativo',
        'quantidade',
        'preco',
        'data',
        'tipo',
        'identificador',
        'corretagem',
        'emolumentos',
        'tx_liquida_CBLC',
        'IRRF_Final',
        'Lucro_Day_Trade',
        'IRRF_Day_Trade',
        'corretora',
        ]
    template_name = 'cadastros/form.html'
    success_url = reverse_lazy('listar-ordens')
    success_message = "%(ativo)s atualizado com sucesso!"

    def form_valid(self, form):
        Ativo.objects.filter(id=self.object.id, user=self.request.user).update(ativo=form.cleaned_data['ativo'])

        qtd_antigo = Nota.objects.values('quantidade','total_compra').filter(id=self.object.id, user=self.request.user)
        qtd_antigo = list(qtd_antigo)
        
        ativo_reg = Ativo.objects.values().filter(ativo=form.cleaned_data['ativo'], user=self.request.user)
        ativo_reg = list(ativo_reg)

        if ativo_reg[0]['quantidade'] <= 0:
            context ={
                'message':'Seu saldo é 0 por favor lance uma nota de compra.'
            }
            return render(self.request, 'error.html', context)

        elif not ativo_reg and form.cleaned_data['tipo'] == 'V' and form.cleaned_data['quantidade'] < 0:
            context ={
                'message':'Não foi possível atualizar sua ordem, por favor verifique a quantidade informada.'
            }
            return render(self.request, 'error.html', context)
        else:
            ativo_reg[0]['quantidade'] = ativo_reg[0]['quantidade'] - qtd_antigo[0]['quantidade']
            ativo_reg[0]['preco_total'] = ativo_reg[0]['preco_total'] - qtd_antigo[0]['total_compra']
            Ativo.objects.filter(ativo=form.cleaned_data['ativo'], user=self.request.user).update(quantidade=ativo_reg[0]['quantidade'], preco_total=ativo_reg[0]['preco_total'])

            ativo_reg[0]['quantidade'] = ativo_reg[0]['quantidade'] + form.cleaned_data['quantidade']
            ativo_reg[0]['preco_total'] = ativo_reg[0]['preco_total'] + (form.cleaned_data['quantidade']*form.cleaned_data['preco'])
            Ativo.objects.filter(ativo=form.cleaned_data['ativo'], user=self.request.user).update(quantidade=ativo_reg[0]['quantidade'], preco_total=ativo_reg[0]['preco_total'])

        return super().form_valid(form)


    def get_success_message(self, cleaned_data):
        return self.success_message % dict(
            cleaned_data,
            ativo=self.object.ativo,
        )

    def get_form(self):
         form = super().get_form()
         form.instance.user = self.request.user
         form.fields['data'].widget = DatePickerInput(format='%d/%m/%Y',
          options={'locale':'pt-br'},
          )

         return form

def b3_cotacao():
        dados=[]
        url = 'https://br.finance.yahoo.com/quote/^BVSP'
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.64'}
        #pegando cotação no yahoo            
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')

        b3_nome = soup.find_all('h3', {'class':'Maw(160px)'})[0].find('a').text
        b3_indice = soup.find_all('h3', {'class':'Maw(160px)'})[0].find('fin-streamer').text
        b3_porcentagem = soup.find_all('h3', {'class':'Maw(160px)'})[0].find('div').text

        dados.append(b3_nome)
        dados.append(b3_indice)
        dados.append(b3_porcentagem)
    
        return dados
# Classe para mostrar os calculos da tela Home.html
class WalletView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('account_login')  
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        v_zero = locale.currency(0, grouping=True)
        r_result = []
        total_lucro = []
        total_lucro = v_zero
        total_investido = []
        total_investido = v_zero
        total_v_mercado = []
        total_v_mercado = v_zero
        ultima_atualizacao = []
        status_fechado_aberto = []
        porcentagem_lucro = 0.0
        status_fechado_aberto = 'Aguardando o cadastro de ações'
        x = 0
        y = 0
        v = 0
        result_compra = Nota.objects.values('ativo').annotate(qt=Sum('quantidade'), preco_f=Sum('total_compra'), custos=Sum('total_custo'), preco_m=Sum('preco'), v_mercado=Sum('preco'), lucro=Sum('preco'), variacao_mercado_1=Count('identificador'), variacao_mercado_2=Count('identificador')).filter(tipo__in=['C','B'], user=self.request.user)
        result_venda = Nota.objects.values('ativo').annotate(qt=Sum('quantidade'), preco_f=Sum('total_compra'), custos=Sum('total_custo')).filter(tipo='V', user=self.request.user)
            
        for venda in result_venda:
            for compra in result_compra:
                if compra['ativo'] == venda['ativo']:                
                    compra['qt'] = compra['qt'] - venda['qt']
                    compra['preco_f'] = abs(compra['preco_f'] - venda['preco_f'])
                    compra['custos'] = compra['custos'] - venda['custos']

        for compra in result_compra:
            if compra['qt'] != 0:
                preco_mercado = Cotacao.objects.filter(ativo=compra['ativo']).last()
                status_fechado_aberto = Cotacao.objects.filter(ativo=compra['ativo']).last()
                status_fechado_aberto = status_fechado_aberto.status_fechado_aberto
                ultima_atualizacao = preco_mercado.data_instante
                compra['v_mercado'] = locale.currency(Decimal(preco_mercado.fechamento_ajustado.replace(",",".")) * compra['qt'], grouping=True)
                compra['lucro'] = (Decimal(preco_mercado.fechamento_ajustado.replace(",","."))*compra['qt'])-compra['preco_f']-compra['custos']-compra['custos']*(Decimal(preco_mercado.fechamento_ajustado.replace(",","."))*compra['qt'])/compra['preco_f']
                
                v = (Decimal(preco_mercado.fechamento_ajustado.replace(",",".")) * compra['qt']) + v
                x = compra['lucro'] + x
                y = compra['preco_f'] + compra['custos'] + y

                porcentagem_lucro = round((x/y)*100,2)
                compra['lucro'] = locale.currency(compra['lucro'], grouping=True)
                compra['preco_m'] = locale.currency(Decimal(preco_mercado.fechamento_ajustado.replace(",",".")), grouping=True)
                compra['preco_f'] = locale.currency(compra['preco_f'], grouping=True)
                compra['custos'] = locale.currency(compra['custos'], grouping=True)
                compra['variacao_1'] = preco_mercado.variacao_1
                compra['variacao_2'] = preco_mercado.variacao_2                

                r_result.append(compra)                
                total_lucro=locale.currency(x, grouping=True)
                total_investido=locale.currency(y, grouping=True)
                total_v_mercado = locale.currency(v, grouping=True)            

        pro = 0
        pro_result = []
        pro_result = 0
        proventos = Proventos.objects.filter(user=self.request.user)
        for i in proventos:
            pro = i.valor + pro

        pro_result = locale.currency(pro, grouping=True)

        total_v_mercado_extra = locale.currency(v + pro, grouping=True)
        # Tratando erro em caso de erro do certificado digital
        try:
            b3 = b3_cotacao()
        except requests.exceptions.SSLError:
            b3 = ['IBOV','N/A','N/A']
            
        context = {
            'result_c' : r_result,
            'total_lucro' : total_lucro,
            'total_investido' : total_investido,
            'total_v_mercado' : total_v_mercado,
            'total_v_mercado_extra': total_v_mercado_extra,
            'total_proventos' : pro_result,
            'status_fechado_aberto' : status_fechado_aberto,
            'ultima_atualizacao': ultima_atualizacao,
            'porcentagem_lucro': porcentagem_lucro,
            'b3_nome':b3[0],
            'b3_indice':b3[1],
            'b3_porcentagem':b3[2]
        }
        
        return context
# Cadastrar proventos
class ProventosCreate(LoginRequiredMixin, CreateView):
    model = Proventos
    fields = ('ativo','tipo_provento','data','valor')
    template_name = 'cadastros/form-proventos.html'
    success_url = reverse_lazy('listar-proventos')
    success_message = "%(ativo)s registrado com sucesso!"    

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(
            cleaned_data,
            ativo=self.object.ativo,
        )

    def get_form(self):
        form = super().get_form()
        form.instance.user = self.request.user
        form.fields['data'].widget = DatePickerInput(format='%d/%m/%Y',
         options={'locale':'pt-br'}
        )
        return form

# Atualizar proventod
class ProventosUpdate(LoginRequiredMixin, UpdateView):
    model = Proventos
    fields = ('ativo','tipo_provento','data','valor')
    template_name = 'cadastros/form-proventos.html'
    success_url = reverse_lazy('listar-proventos')
    success_message = "Proventos do %(ativo)s atualizado com sucesso!"    

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(
            cleaned_data,
            ativo=self.object.ativo,
        )

    def get_form(self):
        form = super().get_form()
        form.instance.user = self.request.user
        form.fields['data'].widget = DatePickerInput(format='%d/%m/%Y',
         options={'locale':'pt-br'}
        )
        return form
# Listar proventos
class ProventosList(LoginRequiredMixin,ListView):
    login_url = reverse_lazy('account_login')
    model = Proventos
    template_name = 'listar/proventos.html'

    def get_queryset(self):
        data_inicial = self.request.GET.get('data_inicial')
        data_final = self.request.GET.get('data_final')

        if data_inicial or data_final:
            self.object_list = Proventos.objects.filter(data__range=(data_inicial, data_final), user=self.request.user).order_by('data')
        else:
            self.object_list = Proventos.objects.filter(user=self.request.user).order_by('data')
        return self.object_list

# Delete proventos
class ProventosDelete(LoginRequiredMixin, DeleteView):
    login_url = reverse_lazy('account_login')
    model = Proventos
    template_name = 'cadastros/form-excluir.html'
    success_url = reverse_lazy('listar-ordens')
    success_message = "%(ativo)s deletado com sucesso!"

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(
            cleaned_data,
            ativo=self.object.ativo,
        )

# Função de Gráfico
class CarteiraChart(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('account_login')  
    template_name = 'dashboard/carteiraChart.html' 
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        data_inicio = self.request.GET.get('data_inicio')
        data_fim = self.request.GET.get('data_fim')
        r_result = []
        status_fechado_aberto = []
        status_fechado_aberto = 'Aguardando o cadastro de ações'
        x = 0
        y = 0
        v = 0
        if data_inicio or data_fim:
            result_compra = Nota.objects.values('ativo').annotate(qt=Sum('quantidade'), preco_f=Sum('total_compra'), custos=Sum('total_custo'), preco_m=Sum('preco'), v_mercado=Sum('preco'), lucro=Sum('preco'), variacao_mercado_1=Count('identificador'), variacao_mercado_2=Count('identificador')).filter(data__range=(data_inicio, data_fim),tipo__in=['C','B'], user=self.request.user)
            result_venda = Nota.objects.values('ativo').annotate(qt=Sum('quantidade'), preco_f=Sum('total_compra'), custos=Sum('total_custo')).filter(data__range=(data_inicio, data_fim),tipo='V', user=self.request.user)
        else:
            result_compra = Nota.objects.values('ativo').annotate(qt=Sum('quantidade'), preco_f=Sum('total_compra'), custos=Sum('total_custo'), preco_m=Sum('preco'), v_mercado=Sum('preco'), lucro=Sum('preco'), variacao_mercado_1=Count('identificador'), variacao_mercado_2=Count('identificador')).filter(tipo__in=['C','B'], user=self.request.user)
            result_venda = Nota.objects.values('ativo').annotate(qt=Sum('quantidade'), preco_f=Sum('total_compra'), custos=Sum('total_custo')).filter(tipo='V', user=self.request.user)
                
        for venda in result_venda:
            for compra in result_compra:
                if compra['ativo'] == venda['ativo']:                
                    compra['qt'] = compra['qt'] - venda['qt']
                    compra['preco_f'] = abs(compra['preco_f'] - venda['preco_f'])
                    compra['custos'] = compra['custos'] - venda['custos']

        for compra in result_compra:
            if compra['qt'] != 0:
                preco_mercado = Cotacao.objects.filter(ativo=compra['ativo']).last()
                status_fechado_aberto = Cotacao.objects.filter(ativo=compra['ativo']).last()
                status_fechado_aberto = status_fechado_aberto.status_fechado_aberto
                compra['v_mercado'] = locale.currency(Decimal(preco_mercado.fechamento_ajustado.replace(",",".")) * compra['qt'], grouping=True)
                compra['lucro'] = (Decimal(preco_mercado.fechamento_ajustado.replace(",","."))*compra['qt'])-compra['preco_f']-compra['custos']-compra['custos']*(Decimal(preco_mercado.fechamento_ajustado.replace(",","."))*compra['qt'])/compra['preco_f']
                
                v = (Decimal(preco_mercado.fechamento_ajustado.replace(",",".")) * compra['qt']) + v
                x = compra['lucro'] + x
                y = compra['preco_f'] + compra['custos'] + y

                compra['lucro'] = locale.currency(compra['lucro'], grouping=True)
                compra['preco_m'] = locale.currency(Decimal(preco_mercado.fechamento_ajustado.replace(",",".")), grouping=True)
                compra['preco_f'] = locale.currency(compra['preco_f'], grouping=True)
                compra['custos'] = locale.currency(compra['custos'], grouping=True)
                compra['variacao_1'] = preco_mercado.variacao_1
                compra['variacao_2'] = preco_mercado.variacao_2
                

                r_result.append(compra)
            else:
                pass
        quantidade = 0
        for i in r_result:
            quantidade += int(i['qt'])

        valor_acumulado = quantidade
        if not r_result:
            r_result = [{'ativo':'N/A','qt':0}]

        fig = px.pie(r_result, values='qt', names='ativo', title='Distribuição da Carteira')
        chart = fig.to_html()
        form = DateForm()
        if self.request.GET:
            form = DateForm(self.request.GET)
        context = {
            'chart' : chart,
            'valor_acumulado':valor_acumulado,
            'form':form
        }

        
        
        return context

# Grafico de proventos
def Dashboard(request):
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    total_proventos=0
    
    if data_inicio or data_fim:
        proventos = Proventos.objects.select_related('user').filter(data__range=(data_inicio,data_fim), user=request.user).values('ativo').annotate(valor_total=Sum('valor')).order_by('-valor_total')        
        for p in proventos:
            total_proventos += p['valor_total']
    else:    
        proventos = Proventos.objects.select_related('user').filter(user=request.user).values('ativo').annotate(valor_total=Sum('valor')).order_by('-valor_total')
        for p in proventos:
            total_proventos += p['valor_total']

    if not proventos:
            proventos = [{'ativo':'Nenhum','valor_total':0}]

    total_proventos = locale.currency(total_proventos, grouping=True)

    fig = px.bar(proventos,
        x = 'ativo',
        y = 'valor_total',
        text_auto='.2s',
        title="Soma de proventos por ativo",
        labels={'x':'Ativos','y':'Valor'},
    )

    fig.update_traces(texttemplate='R$ %{y:,.2f}',textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
    fig.update_layout(yaxis_tickprefix = 'R$ ', yaxis_tickformat = ',.2f',uniformtext_minsize=8, uniformtext_mode='hide',title={'font_size':22,'xanchor':'center','x':0.5})
    chart = fig.to_html()
    form = DateForm()
    if request.GET:
        form = DateForm(request.GET)
    
    context = {'chart': chart, 'form': form, 'total_proventos':total_proventos}
    return render(request, 'dashboard/chart.html', context)    

# Dashboard Temporal
class DashboardTemporal(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('account_login')  
    template_name = 'dashboard/dashboardTemporal.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ano = str(datetime.today().year)
        data_inicio = self.request.GET.get('data_inicio')
        data_fim = self.request.GET.get('data_fim')

        if data_inicio or data_fim:
            df = yf.download(context['ativo']+'.SA', start=data_inicio, end=data_fim, rounding=True)
        else:
            df = yf.download(context['ativo']+'.SA', start=ano+'-01-01', end=ano+'-12-31', rounding=True)

        fig = go.Figure(data=[go.Candlestick(x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Adj Close'])])
        fig.update_layout(xaxis_rangeslider_visible=False)
        chart = fig.to_html()

        fig = go.Figure([go.Scatter(x=df.index, y=df['Adj Close'])])
        chart_2 = fig.to_html()
        form = DateForm()
        if self.request.GET:
            form = DateForm(self.request.GET)
        context = {'chart':chart, 'chart_2':chart_2, 'form':form, 'ativo':context['ativo']}
        return context

# List Cotação
class CotacaoList(LoginRequiredMixin, ListView):
    login_url = reverse_lazy('account_login')
    model = Cotacao
    template_name = 'listar/cotacao.html'

    def get_queryset(self):
        filter = self.request.GET.get('filter')

        if filter:
            self.object_list = Cotacao.objects.filter(ativo__icontains=filter)
        else:
            self.object_list = Cotacao.objects.all()
        return self.object_list


class Export_xls:

    def get_context_data(request):
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="proventos.xls"'

        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Proventos')

        # Sheet header, first row
        row_num = 0

        font_style = xlwt.XFStyle()
        font_style.font.bold = True

        columns = ['Ativo', 'Tipo', 'Data', 'Valor', ]

        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], font_style)

        # Sheet body, remaining rows
        font_style = xlwt.XFStyle()

        rows = Proventos.objects.all().values_list('ativo', 'tipo_provento', 'data', 'valor').filter(user=request.user)
        for row in rows:
            row_num += 1
            for col_num in range(len(row)):
                ws.write(row_num, col_num, row[col_num], font_style)

        wb.save(response)
        return response

# Dashboard Carteira vs Bolsa
class Dash_Carteira_X_Bolsa(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('account_login')  
    template_name = 'dashboard/dash_carteira_x_bolsa.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ano = str(datetime.today().year)
        ano_passado = int(ano)-1
        ano_passado = str(ano_passado)
        # 
        inicio = self.request.GET.get('data_inicio')
        fim = self.request.GET.get('data_fim')
        # Consultado a relação de ativos do usuario maior que 0
        ativos = Ativo.objects.filter(user=self.request.user, quantidade__gt=0)
        acoes = [a.ativo for a in ativos]

        # buscando as informações via Yahoo Fincance
        precos = pd.DataFrame()
        if inicio or fim:            
            for i in acoes:
                precos[i] = yf.download(i+'.SA', start = inicio, end = fim)['Adj Close']
        else:            
            for i in acoes:
                precos[i] = yf.download(i+'.SA', start = ano_passado+'-01-01', end = ano+'-12-31')['Adj Close']    

        # Vamos normalizar o preço dos ativos para visualizar seus desempenhos
        df = precos/precos.iloc[0]
        # Apresentando as informações no gráfico 
        fig = px.line(df, x=df.index, y=df.columns,title='Desempenho dos Ativos')
        fig.update_xaxes(dtick="M1",tickformat="%b\n%Y",ticklabelmode="period")
        chart = fig.to_html()

        # Criando um dicionário com as alocações que vamos fazer para cada ativo na nossa carteira
        carteira = {str(dado.ativo):dado.quantidade for dado in ativos}
        carteira_df = pd.Series(data=carteira, index=list(carteira.keys()))        
        # Obtendo preços dos ativos no primeiro dia do investimento
        primeiro = precos.iloc[0]
        # Quantidade de papéis comprados de cada ativo
        qtd_acoes = carteira_df/primeiro
        # Criando um dataframe que contém a posição diária de cada ativo
        PL = precos*qtd_acoes
        # Criando uma coluna que contém a posição consolidada da nossa carteira diariamente
        PL['PL Total'] = PL.iloc[:].sum(axis = 1)

        # Apresentando as informações no gráfico 
        fig = px.line(PL, x=PL.index, y=PL.columns,title='Posição diária de cada ativo')
        fig.update_xaxes(dtick="M1",tickformat="%b\n%Y",ticklabelmode="period")
        chart_PL = fig.to_html()

        # Obtendo dados do IBOV para comparar com a nossa carteira
        if inicio or fim:
            ibov = yf.download('^BVSP', start = inicio, end = fim)
        else:
            ibov = yf.download('^BVSP', start = ano_passado+'-01-01', end = ano+'-12-31')
        # Renomeando a coluna com o nome IBOV
        ibov.rename(columns = {'Adj Close': 'IBOV'}, inplace = True)
        # Limpando as demais colunas
        ibov = ibov.drop(ibov.columns[[0,1,2,3,5]], axis = 1)
        # Verificando se o índice dos dataframes está no formato 'data'
        ibov.index = pd.to_datetime(ibov.index)
        PL.index = pd.to_datetime(PL.index)
        # Juntando tudo num dataframe só
        novo_df = pd.merge(ibov, PL, how = 'inner', on = 'Date')
        # Normalizando esse novo dataframe que contém o IBOV, todos os ativos e o PL da nossa carteira
        PL_normalizado = novo_df/novo_df.iloc[0]
        # Filtrando as colunas IBOV e PL Total
        PL_normalizado = PL_normalizado[['IBOV','PL Total']]

        # Apresentando as informações no gráfico
        fig = px.line(PL_normalizado, x=PL_normalizado.index, y=PL_normalizado.columns,title='Carteira Vs Ibovespa')
        fig.update_xaxes(dtick="M1", tickformat="%b\n%Y", ticklabelmode="period")
        chart_IBOV_PL = fig.to_html()
        form = DateForm()
        if self.request.GET:
            form = DateForm(self.request.GET)
        context = {'chart':chart, 'chart_PL':chart_PL, 'chart_IBOV_PL':chart_IBOV_PL, 'form':form}
        
        return context
# Cadastrado de Desdobramento
class DesdobramentoCreate(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Desdobramento
    form_class = DesdobramentoForm
    template_name = 'cadastros/desdobramento.html'
    success_url = reverse_lazy('cadastrar-desdobramento')
    success_message = "Desdobramento registrado com sucesso!"

    def form_valid(self, form):
        if form.cleaned_data['a_cada'] <= 0 or form.cleaned_data['desdobra_se']<=0:
            context ={
                'message':'A quantidade não pode ser igual ou menor que 0. Por favor tente novamente.'
            }
            return render(self.request, 'error.html', context)
        else:
            a_cada = form.cleaned_data['a_cada']
            desdobra_se = form.cleaned_data['desdobra_se']
            ativo = Ativo.objects.filter(user=self.request.user, quantidade__gt=0, ativo=form.cleaned_data['ativo'])
            nota = Nota.objects.filter(user=self.request.user, quantidade__gt=0, ativo=form.cleaned_data['ativo'], data__lte=form.cleaned_data['data'])
            qtd_ajustada_ativo=0
            qtd_ajustada_ativo_venda = 0
            qtd_nota_c = 0
            qtd_nota_v = 0
            ativo = list(ativo)
            ativo = ativo[0].quantidade

            for i in nota:
                qtd_ajustada = int((i.quantidade / a_cada)*desdobra_se)
                preco_ajustado = i.total_compra / qtd_ajustada       
                Nota.objects.filter(user=self.request.user, id=i.id).update(quantidade=qtd_ajustada, preco=preco_ajustado)
                if i.tipo == 'C':
                    qtd_nota_c +=i.quantidade
                    qtd_ajustada_ativo += qtd_ajustada
                else:
                    qtd_nota_v +=i.quantidade
                    qtd_ajustada_ativo_venda += qtd_ajustada
                qtd_ajustada_ativo = (qtd_ajustada_ativo-qtd_ajustada_ativo_venda)

            # calculando a diferença de quantidade da nota e do ativo e somando com o desdobramento 
            qtd_ajustada_ativo = qtd_ajustada_ativo+(ativo -(qtd_nota_c-qtd_nota_v))
            Ativo.objects.filter(user=self.request.user).update(quantidade=qtd_ajustada_ativo)

        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()

        return super().form_valid(form)

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(DesdobramentoCreate, self).get_form_kwargs(*args, **kwargs)        
        kwargs['user'] = self.request.user
        return kwargs

# Lista de desdobramento do usuario
class DesdobramentoList(LoginRequiredMixin, ListView):
    login_url = reverse_lazy('account_login')
    model = Desdobramento
    template_name = 'listar/desdobramento.html'

    def get_queryset(self):
        self.object_list = Desdobramento.objects.filter(user=self.request.user).order_by('-data')
        return self.object_list

class DesdobramentoDelete(LoginRequiredMixin, DeleteView):
    login_url = reverse_lazy('account_login')
    model = Desdobramento
    template_name = 'cadastros/form-excluir-desdobramento.html'
    success_url = reverse_lazy('listar-desdobramento')
    success_message = "%(ativo)s foi desfeito e excluído com sucesso!"

    def delete(self, *args, **kwargs):  
        desdobramento = Desdobramento.objects.filter(user=self.request.user, id=kwargs['pk'])
        desdobramento = list(desdobramento) 
        ativo_d = desdobramento[0].ativo
        a_cada = desdobramento[0].a_cada
        desdobra_se = desdobramento[0].desdobra_se
        data = desdobramento[0].data

        # consultando os ativos e as notas  
        ativo = Ativo.objects.filter(user=self.request.user, quantidade__gt=0, ativo=ativo_d)
        nota = Nota.objects.filter(user=self.request.user, quantidade__gt=0, ativo=ativo_d, data__lte=data)        
        qtd_ajustada_ativo=0
        qtd_ajustada_ativo_venda = 0
        qtd_nota_c = 0
        qtd_nota_v = 0
        ativo = list(ativo)
        ativo = ativo[0].quantidade
        # Desfazendo o desdobramento das notas registradas
        for i in nota:
            qtd_ajustada = int((i.quantidade / desdobra_se)*a_cada)
            preco_ajustado = i.total_compra / qtd_ajustada
            Nota.objects.filter(user=self.request.user, id=i.id, data__lte=data).update(quantidade=qtd_ajustada, preco=preco_ajustado)            
            if i.tipo == 'C':
                qtd_nota_c += i.quantidade
                qtd_ajustada_ativo += qtd_ajustada
            else:
                qtd_nota_v += i.quantidade
                qtd_ajustada_ativo_venda += qtd_ajustada
            qtd_ajustada_ativo = (qtd_ajustada_ativo - qtd_ajustada_ativo_venda)
            
        # calculando a diferença de quantidade da nota e do ativo e somando com o desdobramento 
        qtd_ajustada_ativo = qtd_ajustada_ativo + (ativo - (qtd_nota_c - qtd_nota_v))
        Ativo.objects.filter(user=self.request.user).update(quantidade=qtd_ajustada_ativo)

        return super(DesdobramentoDelete, self).delete(*args, **kwargs)

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(
            cleaned_data,
            ativo=self.object.ativo,
        )

class BonificacaoCreate(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Bonificacao
    form_class= BonificacaoForm
    login_url = reverse_lazy('account_login')
    template_name = 'cadastros/bonificacao.html'
    success_url = reverse_lazy('cadastrar-bonificacao')
    success_message = "Bonificação do %(ativo)s lançada com sucesso!"

    def form_valid(self, form):
        if form.cleaned_data['a_cada'] <= 0 or form.cleaned_data['recebo_bonus_de'] <= 0 or form.cleaned_data['custo_atribuido'] <= 0:
            context ={
                'message':'A quantidade não pode ser menor ou igual a 0. Por favor tente novamente.'
            }
            return render(self.request, 'error.html', context)
        else:
            ativo_bonificado = form.cleaned_data['ativo']
            data = form.cleaned_data['data']
            a_cada = form.cleaned_data['a_cada']
            recebo_bonus_de = form.cleaned_data['recebo_bonus_de']
            custo_atribuido = form.cleaned_data['custo_atribuido']
            
            ativo = Ativo.objects.filter(user=self.request.user, quantidade__gt=0, ativo=form.cleaned_data['ativo'])
            nota = Nota.objects.filter(user=self.request.user, quantidade__gt=0, ativo=form.cleaned_data['ativo'], data__lte=data)
            qtd_ajustada = 0
            qtd_total_ativo = 0
            total_compra = 0
            qtd_nota_c = 0
            qtd_nota_v = 0
            preco_total_ajustado = 0
            
            for i in nota:
                if i.tipo == 'C' or i.tipo == 'B':
                    qtd_nota_c += i.quantidade
                else:
                    qtd_nota_v += i.quantidade

            qtd_ajustada = qtd_nota_c - qtd_nota_v

            for i in ativo:
                qtd_ajustada = int((qtd_ajustada/a_cada)*recebo_bonus_de)
                qtd_total_ativo = i.quantidade + qtd_ajustada

                total_compra = Decimal(form.cleaned_data['custo_atribuido'] * qtd_ajustada)
                preco_total_ajustado = i.preco_total + total_compra

            if qtd_ajustada <= 0 or qtd_total_ativo <= 0 or total_compra <= 0 or preco_total_ajustado <= 0:
                context ={
                'message':'A quantidade não pode ser menor ou igual a 0. Por favor tente novamente.'
                }
                return render(self.request, 'error.html', context)
            else:
                ativo.update(quantidade=qtd_total_ativo, preco_total=preco_total_ajustado)    
                nota.create(ativo=ativo_bonificado.ativo, quantidade=qtd_ajustada, preco=custo_atribuido, data=data, tipo='B', total_compra=total_compra, identificador=ativo_bonificado.ativo+' BONIFICAÇÃO', corretagem=0.0, emolumentos=0.0, tx_liquida_CBLC =0.0, user=self.request.user)

        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()

        return super().form_valid(form)

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(BonificacaoCreate, self).get_form_kwargs(*args, **kwargs)        
        kwargs['user'] = self.request.user
        return kwargs

# Lista de bonificação do usuario
class BonificacaoList(LoginRequiredMixin, ListView):
    login_url = reverse_lazy('account_login')
    model = Bonificacao
    template_name = 'listar/bonificacao.html'

    def get_queryset(self):
        self.object_list = Bonificacao.objects.filter(user=self.request.user).order_by('-data')
        return self.object_list
        
# Apagar a bonificação e o que foi lançado em notas e ativo
class BonificacaoDelete(LoginRequiredMixin, DeleteView):
    login_url = reverse_lazy('account_login')
    model = Bonificacao
    template_name = 'cadastros/form-excluir-bonificacao.html'
    success_url = reverse_lazy('listar-bonificacao')
    success_message = "%(ativo)s foi desfeito e excluído com sucesso!"

    def delete(self, *args, **kwargs):  
        # consultando a bonificação que será excluida os ativos e as notas 
        bonificacao = Bonificacao.objects.filter(user=self.request.user, id=kwargs['pk'])
        bonificacao = list(bonificacao) 
        ativo_b = bonificacao[0].ativo
        data = bonificacao[0].data
         
        ativo = Ativo.objects.filter(user=self.request.user, quantidade__gt=0, ativo=ativo_b)
        nota = Nota.objects.filter(user=self.request.user, quantidade__gt=0, ativo=ativo_b, data=data, tipo='B')

        qtd_ajustada_ativo=0
        preco_ajustado_ativo = 0
        
        # Desfazendo a bonificação das notas registradas
        for i, j in zip(ativo, nota):
            qtd_ajustada_ativo = i.quantidade-j.quantidade
            preco_ajustado_ativo = i.preco_total - j.total_compra
        #  se os valores forem menores ou igual a 0 renderiza para pagina de erro   
        if qtd_ajustada_ativo <= 0 and preco_ajustado_ativo <= 0:
            context ={
            'message':'A quantidade não pode ser menor ou igual a 0. Por favor tente novamente.'
            }
            return render(self.request, 'error.html', context)
        else:
            # apagando a bonificação lançada nas notas
            nota.delete()
            # alterando as quantidades e o preco do ativo
            Ativo.objects.filter(user=self.request.user, ativo=ativo_b).update(quantidade=qtd_ajustada_ativo, preco_total=preco_ajustado_ativo)

        return super(BonificacaoDelete, self).delete(*args, **kwargs)

# Renderezação de erros
def error_500(request):
    return render(request, '500.html')

def error_404(request,exception):
    return render(request, '404.html')