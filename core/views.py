from datetime import datetime
from core.forms import BonificacaoForm, CalculadoraForm, ContatoForm, DateForm, DesdobramentoForm, GrupamentoForm, ProventosForm, ProfileForm, UserForm
from .models import Ativo, Bonificacao, Desdobramento, Grupamento, Nota, Profile, Proventos, Cotacao
from decimal import Decimal
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView
from django.views.generic import TemplateView
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth, TruncYear
from bootstrap_datepicker_plus import DatePickerInput
from braces.views import GroupRequiredMixin
import xlwt
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
import locale
import requests
from bs4 import BeautifulSoup
import plotly.express as px
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from django.contrib import messages
from plotly.offline import plot
from chartjs.views.lines import BaseLineChartView
import boto3
from botocore.exceptions import NoCredentialsError
import uuid

from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

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
        ativo_reg = Ativo.objects.values().filter(
            ativo__icontains=form.cleaned_data['ativo'], user=self.request.user)
        ativo_reg = list(ativo_reg)
        cotacao_reg = Cotacao.objects.values().filter(
            ativo__icontains=form.cleaned_data['ativo'])
        cotacao_reg = list(cotacao_reg)

        # Se o ativo for null e a tentativa for uma venda
        if not ativo_reg and form.cleaned_data['tipo'] == 'V' and form.cleaned_data['preco'] > 0:
            context = {
                'message': 'Não foi possível registrar sua ordem, por favor verifique a quantidade correta informada.'
            }
            return render(self.request, 'error.html', context)
        # Se não existir cotação e ativo e a quantidade e preço maior que 0 para a  compra será então cadastre ativo e cotação
        elif not ativo_reg and form.cleaned_data['tipo'] == 'C' and form.cleaned_data['quantidade'] > 0 and not cotacao_reg and form.cleaned_data['preco'] > 0:
            Ativo.objects.create(ativo=form.cleaned_data['ativo'],  quantidade=form.cleaned_data['quantidade'],
                                 preco_total=form.cleaned_data['quantidade']*form.cleaned_data['preco'], user=self.request.user)
            Cotacao.objects.create(
                acao=form.cleaned_data['identificador'], ativo=form.cleaned_data['ativo'])
        # se não existir ativo, mas tem cotação na compra e preço maior que 0 então cadastre apenas ativo
        elif not ativo_reg and form.cleaned_data['tipo'] == 'C' and form.cleaned_data['quantidade'] > 0 and cotacao_reg and form.cleaned_data['preco'] > 0:
            Ativo.objects.create(ativo=form.cleaned_data['ativo'],  quantidade=form.cleaned_data['quantidade'],
                                 preco_total=form.cleaned_data['quantidade']*form.cleaned_data['preco'], user=self.request.user)
        # Se não existir cotação na compra e a quantidade e preço maior que 0 então some a quantidade e preço com o existente depois cadastre noa tivo e tambem a cotação
        elif form.cleaned_data['tipo'] == 'C' and form.cleaned_data['quantidade'] > 0 and not cotacao_reg and form.cleaned_data['preco'] > 0:
            ativo_reg[0]['quantidade'] = ativo_reg[0]['quantidade'] + \
                form.cleaned_data['quantidade']
            ativo_reg[0]['preco_total'] = ativo_reg[0]['preco_total'] + \
                (form.cleaned_data['quantidade']*form.cleaned_data['preco'])
            Ativo.objects.filter(ativo=form.cleaned_data['ativo'], user=self.request.user).update(
                ativo=form.cleaned_data['ativo'], quantidade=ativo_reg[0]['quantidade'], preco_total=ativo_reg[0]['preco_total'], user=self.request.user)
            Cotacao.objects.create(
                acao=form.cleaned_data['identificador'], ativo=form.cleaned_data['ativo'])
        # Se existir cotação na compra e a quantidade e preço maior que 0 então some a quantidade e preço com o existente depois cadastre o ativo
        elif form.cleaned_data['tipo'] == 'C' and form.cleaned_data['quantidade'] > 0 and cotacao_reg and form.cleaned_data['preco'] > 0:
            ativo_reg[0]['quantidade'] = ativo_reg[0]['quantidade'] + \
                form.cleaned_data['quantidade']
            ativo_reg[0]['preco_total'] = ativo_reg[0]['preco_total'] + \
                (form.cleaned_data['quantidade']*form.cleaned_data['preco'])
            Ativo.objects.filter(ativo=form.cleaned_data['ativo'], user=self.request.user).update(
                ativo=form.cleaned_data['ativo'], quantidade=ativo_reg[0]['quantidade'], preco_total=ativo_reg[0]['preco_total'], user=self.request.user)
        # Se a venda for menor do que a existente e preço maior que 0 então some a quantidade e preço existente depois cadastre o ativo
        elif form.cleaned_data['tipo'] == 'V' and form.cleaned_data['quantidade'] <= ativo_reg[0]['quantidade'] and form.cleaned_data['quantidade'] > 0 and form.cleaned_data['preco'] > 0:
            ativo_reg[0]['quantidade'] = ativo_reg[0]['quantidade'] - \
                form.cleaned_data['quantidade']
            ativo_reg[0]['preco_total'] = ativo_reg[0]['preco_total'] - \
                (form.cleaned_data['quantidade']*form.cleaned_data['preco'])
            Ativo.objects.filter(ativo=form.cleaned_data['ativo'], user=self.request.user).update(
                ativo=form.cleaned_data['ativo'], quantidade=ativo_reg[0]['quantidade'], preco_total=ativo_reg[0]['preco_total'], user=self.request.user)

        else:
            context = {
                'message': 'Ordem não registrada, pois a quantidade informada ou o preço não é compatível com o que você possui em carteira.'
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
                                                     options={
                                                         'locale': 'pt-br'}
                                                     )
        return form

# List


class NotaList(LoginRequiredMixin, ListView):
    login_url = reverse_lazy('account_login')
    model = Nota
    template_name = 'listar/ordens.html'

    # def get_queryset(self):
    #     self.object_list = Nota.objects.filter(
    #         user=self.request.user).order_by('-data')
    #     return self.object_list

    def get(self, request):
        notas = Nota.objects.filter(user=request.user).order_by('-data')
        export_type = request.GET.get('export_type', None)

        notas_data = []

        for nota in notas:
            notas_data.append([
                nota.ativo,
                nota.quantidade,
                nota.preco,
                nota.data.strftime("%d/%m/%Y"),
                nota.tipo,
                nota.total_compra,
                nota.identificador,
                nota.corretagem,
                nota.emolumentos,
                nota.tx_liquida_CBLC,
                nota.IRRF_Final,
                nota.Lucro_Day_Trade,
                nota.IRRF_Day_Trade,
                nota.total_custo,
                nota.corretora,
                nota.data_instante.strftime("%d/%m/%Y %H:%M:%S")
            ])

        if export_type == 'excel':
            df = pd.DataFrame(notas_data)
            df = df.rename(columns={
                0: 'ativo',
                1: 'quantidade',
                2: 'preco',
                3: 'data',
                4: 'tipo',
                5: 'total_compra',
                6: 'identificador',
                7: 'corretagem',
                8: 'emolumentos',
                9: 'tx_liquida_CBLC',
                10: 'IRRF_Final',
                11: 'Lucro_Day_Trade',
                12: 'IRRF_Day_Trade',
                13: 'total_custo',
                14: 'corretora',
                15: 'data_instante',
            })
            response = HttpResponse(content_type='application/ms-excel')
            response['Content-Disposition'] = 'attachment; filename="notas.xlsx"'
            df.to_excel(response, index=False)

            return response
        
        elif export_type == 'pdf':
            doc = SimpleDocTemplate("notas.pdf", pagesize=landscape(letter))
            elements = []

            style = getSampleStyleSheet()
            style.add(ParagraphStyle(name='TextColor', textColor=colors.black))

            table_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), style['TextColor']),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, 1), (-1, -1), style['TextColor']),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                ('BOX', (0, 0), (-1, -1), 0.25, colors.black)
            ])
            from reportlab.lib.units import inch
            from reportlab.lib.units import cm

            # Define a altura das células da tabela em polegadas
            CELL_HEIGHT = 0.25 * inch
            notas_table = Table([
                ['Ativo', 'Quantidade', 'Preço', 'Data', 'Tipo', 'Total Compra', 'Identificador',
                    'Corretagem', 'Emolumentos', 'Taxa Líquida CBLC', 'IRRF Final', 'Lucro Day Trade',
                    'IRRF Day Trade', 'Total Custo', 'Corretora', 'Data/Hora'],
                *notas_data
            ], colWidths=[2*cm] + [1.2*cm]*6 + [1.8*cm] + [1.5*cm]*4 + [2*cm]*3 + [1.5*cm]*2 + [2.5*cm])
            
            notas_table.setStyle(table_style)
            elements.append(notas_table)

            doc.build(elements)
            with open("notas.pdf", 'rb') as file:
                response = HttpResponse(file.read(), content_type='application/pdf')
                response['Content-Disposition'] = 'attachment; filename="notas.pdf"'
                return response

        else:
            context = {'object_list': notas}
            return render(request, 'listar/ordens.html', context)

# Delete


class NotaDelete(GroupRequiredMixin, SuccessMessageMixin, LoginRequiredMixin, DeleteView):
    login_url = reverse_lazy('account_login')
    group_required = u'Administrador'
    model = Nota
    template_name = 'cadastros/form-excluir.html'
    success_url = reverse_lazy('listar-ordens')
    success_message = "%(ativo)s deletado com sucesso!"

    def delete(self, request, *args, **kwargs):
        nota = Nota.objects.filter(user=self.request.user, id=kwargs['pk'])
        ativo = Ativo.objects.filter(
            user=self.request.user, ativo=nota[0].ativo)

        ativo = list(ativo)
        nota = list(nota)
        if nota[0].tipo == 'C' or nota[0].tipo == 'B':
            qtd_ajustada = ativo[0].quantidade - nota[0].quantidade
            preco_ajustado = ativo[0].preco_total - nota[0].total_compra
        else:
            qtd_ajustada = ativo[0].quantidade + nota[0].quantidade
            preco_ajustado = ativo[0].preco_total + nota[0].total_compra

        Ativo.objects.filter(user=self.request.user, ativo=nota[0].ativo).update(
            quantidade=qtd_ajustada, preco_total=preco_ajustado)

        return super(NotaDelete, self).delete(request, *args, **kwargs)

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(
            cleaned_data,
            ativo=self.object.ativo,
        )

# Updates


class NotaUpdate(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
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
        tipo_antes_atualizar = self.get_object(
            queryset=Nota.objects.values('tipo'))
        Ativo.objects.filter(ativo=self.get_object(), user=self.request.user).update(
            ativo=form.cleaned_data['ativo'])
        Nota.objects.filter(id=self.object.id, user=self.request.user).update(
            ativo=form.cleaned_data['ativo'])

        qtd_antigo = Nota.objects.values('quantidade', 'total_compra').filter(
            id=self.object.id, user=self.request.user)
        qtd_antigo = list(qtd_antigo)

        ativo_reg = Ativo.objects.values().filter(
            ativo=form.cleaned_data['ativo'], user=self.request.user)
        ativo_reg = list(ativo_reg)

        if ativo_reg[0]['quantidade'] <= 0:
            context = {
                'message': 'Seu saldo é 0 por favor lance uma nota de compra.'
            }
            return render(self.request, 'error.html', context)

        elif form.cleaned_data['tipo'] == 'V':
            qtd_ajustada = ativo_reg[0]['quantidade'] - \
                qtd_antigo[0]['quantidade']
            qtd_ajustada = qtd_ajustada - form.cleaned_data['quantidade']
            preco_total_ajustado = ativo_reg[0]['preco_total'] - (
                form.cleaned_data['quantidade']*form.cleaned_data['preco'])
            preco_total_ajustado = preco_total_ajustado - \
                (form.cleaned_data['quantidade']*form.cleaned_data['preco'])
            Ativo.objects.filter(ativo=form.cleaned_data['ativo'], user=self.request.user).update(
                quantidade=qtd_ajustada, preco_total=preco_total_ajustado)

        elif tipo_antes_atualizar['tipo'] == 'V' and form.cleaned_data['tipo'] == 'C':
            qtd_ajustada = ativo_reg[0]['quantidade'] + \
                form.cleaned_data['quantidade']
            qtd_ajustada = qtd_ajustada + form.cleaned_data['quantidade']
            preco_total_ajustado = ativo_reg[0]['preco_total'] + (
                form.cleaned_data['quantidade']*form.cleaned_data['preco'])
            preco_total_ajustado = preco_total_ajustado + \
                (form.cleaned_data['quantidade']*form.cleaned_data['preco'])
            Ativo.objects.filter(ativo=form.cleaned_data['ativo'], user=self.request.user).update(
                quantidade=qtd_ajustada, preco_total=preco_total_ajustado)

        else:
            pass

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
                                                     options={
                                                         'locale': 'pt-br'},
                                                     )

        return form


def b3_cotacao():
    dados = []
    url = 'https://br.financas.yahoo.com/quote/%5EBVSP'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.64'}
    # pegando cotação no yahoo
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')

    b3_nome = soup.find_all('h1', {'class': 'D(ib) Fz(18px)'})[0].text
    b3_indice = soup.find_all('div', {'class': 'D(ib) Mend(20px)'})[0].find('fin-streamer').text
    b3_porcentagem = soup.find_all('fin-streamer', {'class':'Fw(500) Pstart(8px) Fz(24px)'})[0].text

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
        # Formato local de moeda agrupado
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
        preco_medio = 0
        status_fechado_aberto = 'Aguardando o cadastro de ações'
        x = 0
        y = 0
        v = 0
        # Buscando a relação de compras usuario
        result_compra = Nota.objects.values('ativo').annotate(qt=Sum('quantidade'), preco_f=Sum('total_compra'), custos=Sum('total_custo'), preco_m=Sum('preco'), preco_medio=Sum(
            'preco'), v_mercado=Sum('preco'), lucro=Sum('preco'), variacao_mercado_1=Count('identificador'), variacao_mercado_2=Count('identificador')).filter(tipo__in=['C', 'B'], user=self.request.user)

        # Buscando a relação de vendas do usuario
        result_venda = Nota.objects.values('ativo').annotate(qt=Sum('quantidade'), preco_f=Sum(
            'total_compra'), custos=Sum('total_custo')).filter(tipo='V', user=self.request.user)

        # Varrendo a lista de vendas e compras e realizando o calculo sobre as quantidades e valores pagos e vendidos
        for venda in result_venda:
            for compra in result_compra:
                if compra['ativo'] == venda['ativo']:
                    compra['qt'] = compra['qt'] - venda['qt']
                    compra['preco_f'] = abs(
                        compra['preco_f'] - venda['preco_f'])
                    compra['custos'] = compra['custos'] - venda['custos']

        for compra in result_compra:
            if compra['qt'] != 0:
                # Retornando a cotação do ativo no mercado
                preco_mercado = Cotacao.objects.filter(
                    ativo=compra['ativo']).last()
                # Retornando o status do antivo no mercado
                status_fechado_aberto = Cotacao.objects.filter(
                    ativo=compra['ativo']).last()
                status_fechado_aberto = status_fechado_aberto.status_fechado_aberto
                # coletando a ultima atualização realizada
                ultima_atualizacao = preco_mercado.data_instante
                # Caculando o valor de mercado
                compra['v_mercado'] = locale.currency(Decimal(
                    preco_mercado.fechamento_ajustado.replace(",", ".")) * compra['qt'], grouping=True)
                # Calculando o lucro
                compra['lucro'] = (Decimal(preco_mercado.fechamento_ajustado.replace(",", "."))*compra['qt'])-compra['preco_f']-compra['custos'] - \
                    compra['custos']*(Decimal(preco_mercado.fechamento_ajustado.replace(
                        ",", "."))*compra['qt'])/compra['preco_f']
                # Calculando o preço di fechamento ajustado * a quantidade de compras que o cliente possui
                v = (Decimal(preco_mercado.fechamento_ajustado.replace(
                    ",", ".")) * compra['qt']) + v
                # Enquanto tiver lucro ou não, ele irá ser somado na variavel x
                x = compra['lucro'] + x
                # Calculo de preço de fechamento, mais custos na compra do ativo, mais a soma disso tudo de novo atribuido a variavel y
                y = compra['preco_f'] + compra['custos'] + y
                # calculando o percentual do lucro
                porcentagem_lucro = round((x/y)*100, 2)
                # convertendo o valor do lucro em moeda Real Brasil e agrupando as casas decimais
                compra['lucro'] = locale.currency(
                    compra['lucro'], grouping=True)
                # convertendo o valor do preço de mercado em moeda Real Brasil e agrupando as casas decimais
                compra['preco_m'] = locale.currency(
                    Decimal(preco_mercado.fechamento_ajustado.replace(",", ".")), grouping=True)
                # convertendo o valor do preço de mercado em moeda Real Brasil e agrupando as casas decimais
                compra['preco_medio'] = locale.currency(
                    compra['preco_f'] / compra['qt'], grouping=True)
                # convertendo o valor do preço de fechamento em moeda Real Brasil e agrupando as casas decimais
                compra['preco_f'] = locale.currency(
                    compra['preco_f'], grouping=True)
                # convertendo o valor dos custos em moeda Real Brasil e agrupando as casas decimais
                compra['custos'] = locale.currency(
                    compra['custos'], grouping=True)
                # obtendo o valor da variação de mercado em duas frente de variaveis
                compra['variacao_1'] = preco_mercado.variacao_1
                compra['variacao_2'] = preco_mercado.variacao_2

                # Atribuindo os valores da compra via append dentro da variavel r_result
                r_result.append(compra)
                # convertendo o valor total do lucro em moeda Real Brasil e agrupando as casas decimais
                total_lucro = locale.currency(x, grouping=True)
                # convertendo o valor total investido em moeda Real Brasil e agrupando as casas decimais
                total_investido = locale.currency(y, grouping=True)
                # convertendo o valor total de mercado moeda Real Brasil e agrupando as casas decimais
                total_v_mercado = locale.currency(v, grouping=True)

        pro = 0
        pro_result = []
        pro_result = 0
        # Obtendo os valores de proventos do usuario para poder somar todo o ganho
        proventos = Proventos.objects.filter(user=self.request.user)
        for i in proventos:
            pro = i.valor + pro
        # convertendo a soma dos proventos em moeda Real Brasil e agrupando as casas decimais
        pro_result = locale.currency(pro, grouping=True)
        # convertendo o valor total de mercado extra em moeda Real Brasil e agrupando as casas decimais
        total_v_mercado_extra = locale.currency(v + pro, grouping=True)
        # Tratando erro em caso de erro do certificado digital
        try:
            b3 = b3_cotacao()
        except requests.exceptions.SSLError:
            b3 = ['IBOV', 'N/A', 'N/A']
        # Atribuindo todo o resultado acima e consolida tudo em context
        context = {
            'result_c': r_result,
            'total_lucro': total_lucro,
            'total_investido': total_investido,
            'total_v_mercado': total_v_mercado,
            'total_v_mercado_extra': total_v_mercado_extra,
            'total_proventos': pro_result,
            'status_fechado_aberto': status_fechado_aberto,
            'ultima_atualizacao': ultima_atualizacao,
            'porcentagem_lucro': porcentagem_lucro,
            'b3_nome': b3[0],
            'b3_indice': b3[1],
            'b3_porcentagem': b3[2]
        }

        return context

# Cadastrar proventos


class ProventosCreate(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Proventos
    form_class = ProventosForm
    template_name = 'cadastros/form-proventos.html'
    success_url = reverse_lazy('cadastrar-proventos')
    success_message = "Provento do ativo %(ativo)s registrado com sucesso!"

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()

        return super().form_valid(form)

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(ProventosCreate, self).get_form_kwargs(*args, **kwargs)
        kwargs['user'] = self.request.user
        return kwargs

# Atualizar proventos


class ProventosUpdate(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Proventos
    # fields = ('ativo','tipo_provento','data','valor')
    form_class = ProventosForm
    template_name = 'cadastros/form-proventos.html'
    success_url = reverse_lazy('listar-proventos')
    success_message = "Proventos do %(ativo)s atualizado com sucesso!"

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()

        return super().form_valid(form)

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(ProventosUpdate, self).get_form_kwargs(*args, **kwargs)
        kwargs['user'] = self.request.user
        return kwargs

# Listar proventos


class ProventosList(LoginRequiredMixin, SuccessMessageMixin, ListView):
    login_url = reverse_lazy('account_login')
    model = Proventos
    template_name = 'listar/proventos.html'

    def get_queryset(self):
        data_inicial = self.request.GET.get('data_inicial')
        data_final = self.request.GET.get('data_final')

        if data_inicial or data_final:
            self.object_list = Proventos.objects.filter(data__range=(
                data_inicial, data_final), user=self.request.user).order_by('data')
        else:
            self.object_list = Proventos.objects.filter(
                user=self.request.user).order_by('data')
        return self.object_list

# Delete proventos


class ProventosDelete(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    login_url = reverse_lazy('account_login')
    model = Proventos
    template_name = 'cadastros/form-excluir.html'
    success_url = reverse_lazy('listar-proventos')
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
            result_compra = Nota.objects.values('ativo').annotate(qt=Sum('quantidade'), preco_f=Sum('total_compra'), custos=Sum('total_custo'), preco_m=Sum('preco'), v_mercado=Sum('preco'), lucro=Sum(
                'preco'), variacao_mercado_1=Count('identificador'), variacao_mercado_2=Count('identificador')).filter(data__range=(data_inicio, data_fim), tipo__in=['C', 'B'], user=self.request.user)
            result_venda = Nota.objects.values('ativo').annotate(qt=Sum('quantidade'), preco_f=Sum('total_compra'), custos=Sum(
                'total_custo')).filter(data__range=(data_inicio, data_fim), tipo='V', user=self.request.user)
        else:
            result_compra = Nota.objects.values('ativo').annotate(qt=Sum('quantidade'), preco_f=Sum('total_compra'), custos=Sum('total_custo'), preco_m=Sum('preco'), v_mercado=Sum(
                'preco'), lucro=Sum('preco'), variacao_mercado_1=Count('identificador'), variacao_mercado_2=Count('identificador')).filter(tipo__in=['C', 'B'], user=self.request.user)
            result_venda = Nota.objects.values('ativo').annotate(qt=Sum('quantidade'), preco_f=Sum(
                'total_compra'), custos=Sum('total_custo')).filter(tipo='V', user=self.request.user)

        for venda in result_venda:
            for compra in result_compra:
                if compra['ativo'] == venda['ativo']:
                    compra['qt'] = compra['qt'] - venda['qt']
                    compra['preco_f'] = abs(
                        compra['preco_f'] - venda['preco_f'])
                    compra['custos'] = compra['custos'] - venda['custos']

        for compra in result_compra:
            if compra['qt'] != 0:
                preco_mercado = Cotacao.objects.filter(
                    ativo=compra['ativo']).last()
                status_fechado_aberto = Cotacao.objects.filter(
                    ativo=compra['ativo']).last()
                status_fechado_aberto = status_fechado_aberto.status_fechado_aberto
                compra['v_mercado'] = locale.currency(Decimal(
                    preco_mercado.fechamento_ajustado.replace(",", ".")) * compra['qt'], grouping=True)
                compra['lucro'] = (Decimal(preco_mercado.fechamento_ajustado.replace(",", "."))*compra['qt'])-compra['preco_f']-compra['custos'] - \
                    compra['custos']*(Decimal(preco_mercado.fechamento_ajustado.replace(
                        ",", "."))*compra['qt'])/compra['preco_f']

                v = (Decimal(preco_mercado.fechamento_ajustado.replace(
                    ",", ".")) * compra['qt']) + v
                x = compra['lucro'] + x
                y = compra['preco_f'] + compra['custos'] + y

                compra['lucro'] = locale.currency(
                    compra['lucro'], grouping=True)
                compra['preco_m'] = locale.currency(
                    Decimal(preco_mercado.fechamento_ajustado.replace(",", ".")), grouping=True)
                compra['preco_f'] = locale.currency(
                    compra['preco_f'], grouping=True)
                compra['custos'] = locale.currency(
                    compra['custos'], grouping=True)
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
            r_result = [{'ativo': 'N/A', 'qt': 0}]

        fig = px.pie(r_result, values='qt', names='ativo',
                     title='Distribuição da Carteira')
        chart = fig.to_html()
        form = DateForm()
        if self.request.GET:
            form = DateForm(self.request.GET)
        context = {
            'chart': chart,
            'valor_acumulado': valor_acumulado,
            'form': form
        }

        return context

# Grafico de proventos


def Dashboard(request):
    locale.setlocale(locale.LC_ALL, 'pt_BR')
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    total_proventos = 0

    if data_inicio or data_fim:
        proventos = Proventos.objects.select_related('user').filter(data__range=(
            data_inicio, data_fim), user=request.user).values('ativo').annotate(valor_total=Sum('valor')).order_by('-valor_total')
        proventos_mes = Proventos.objects.select_related('user').filter(data__range=(data_inicio, data_fim), user=request.user).annotate(
            mes=TruncMonth('data')).values('mes').annotate(valor_total=Sum('valor')).order_by('-valor_total')
        proventos_ano = Proventos.objects.select_related('user').filter(data__range=(data_inicio, data_fim), user=request.user).annotate(
            ano=TruncYear('data')).values('ano').annotate(valor_total=Sum('valor')).order_by('-valor_total')
        for p in proventos:
            total_proventos += p['valor_total']
    else:
        proventos = Proventos.objects.select_related('user').filter(user=request.user).values(
            'ativo').annotate(valor_total=Sum('valor')).order_by('-valor_total')
        proventos_mes = Proventos.objects.select_related('user').filter(user=request.user).annotate(
            mes=TruncMonth('data')).values('mes').annotate(valor_total=Sum('valor')).order_by('-valor_total')
        proventos_ano = Proventos.objects.select_related('user').filter(user=request.user).annotate(
            ano=TruncYear('data')).values('ano').annotate(valor_total=Sum('valor')).order_by('-valor_total')
        for p in proventos:
            total_proventos += p['valor_total']

    if not proventos:
        proventos = [{'ativo': 'Nenhum', 'valor_total': 0}]
        proventos_mes = [{'ativo': 'Nenhum', 'valor_total': 0}]

    total_proventos = locale.currency(total_proventos, grouping=True)

    fig_ano = px.bar(proventos_ano, x='ano', y='valor_total', text_auto='.2s',
                     title='Soma de Proventos por Ano', labels={'ano': 'Ano', 'valor_total': 'Valor Total'})
    fig_ano.update_traces(texttemplate='R$ %{y:,.2f}', textfont_size=12,
                          textangle=0, textposition="outside", cliponaxis=False)
    fig_ano.update_layout(yaxis_tickprefix='R$ ', yaxis_tickformat=',.2f', uniformtext_minsize=8,
                          uniformtext_mode='hide', title={'font_size': 22, 'xanchor': 'center', 'x': 0.5})
    chart_ano = fig_ano.to_html()

    fig_mes = px.bar(proventos_mes, x='mes', y='valor_total', text_auto='.2s',
                     title='Soma de Proventos por Mês', labels={'mes': 'Mês', 'valor_total': 'Valor Total'})
    fig_mes.update_traces(texttemplate='R$ %{y:,.2f}', textfont_size=12,
                          textangle=0, textposition="outside", cliponaxis=False)
    fig_mes.update_layout(yaxis_tickprefix='R$ ', yaxis_tickformat=',.2f', uniformtext_minsize=8,
                          uniformtext_mode='hide', title={'font_size': 22, 'xanchor': 'center', 'x': 0.5})
    chart_mes = fig_mes.to_html()

    fig = px.bar(proventos,
                 x='ativo',
                 y='valor_total',
                 text_auto='.2s',
                 title="Soma de Proventos por Ativo",
                 labels={'ativo': 'Lista de Ativos',
                         'valor_total': 'Valor Total'},
                 )

    fig.update_traces(texttemplate='R$ %{y:,.2f}', textfont_size=12,
                      textangle=0, textposition="outside", cliponaxis=False)
    fig.update_layout(yaxis_tickprefix='R$ ', yaxis_tickformat=',.2f', uniformtext_minsize=8,
                      uniformtext_mode='hide', title={'font_size': 22, 'xanchor': 'center', 'x': 0.5})
    chart = fig.to_html()
    form = DateForm()
    if request.GET:
        form = DateForm(request.GET)

    context = {'chart': chart, 'chart_mes': chart_mes, 'chart_ano': chart_ano,
               'form': form, 'total_proventos': total_proventos}
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
            df = yf.download(
                context['ativo']+'.SA', start=data_inicio, end=data_fim, rounding=True)
        else:
            df = yf.download(
                context['ativo']+'.SA', start=ano+'-01-01', end=ano+'-12-31', rounding=True)

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
        context = {'chart': chart, 'chart_2': chart_2,
                   'form': form, 'ativo': context['ativo']}
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

# Exportar Proventos do usuario


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

        rows = Proventos.objects.all().values_list('ativo', 'tipo_provento',
                                                   'data', 'valor').filter(user=request.user)
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
                precos[i] = yf.download(
                    i+'.SA', start=inicio, end=fim)['Adj Close']
        else:
            for i in acoes:
                precos[i] = yf.download(
                    i+'.SA', start=ano_passado+'-01-01', end=ano+'-12-31')['Adj Close']

        # Vamos normalizar o preço dos ativos para visualizar seus desempenhos
        df = precos/precos.iloc[0]
        # Apresentando as informações no gráfico
        fig = px.line(df, x=df.index, y=df.columns,
                      title='Desempenho dos Ativos')
        fig.update_xaxes(dtick="M1", tickformat="%b\n%Y",
                         ticklabelmode="period")
        chart = fig.to_html()

        # Criando um dicionário com as alocações que vamos fazer para cada ativo na nossa carteira
        carteira = {str(dado.ativo): dado.quantidade for dado in ativos}
        carteira_df = pd.Series(data=carteira, index=list(carteira.keys()))
        # Obtendo preços dos ativos no primeiro dia do investimento
        primeiro = precos.iloc[0]
        # Quantidade de papéis comprados de cada ativo
        qtd_acoes = carteira_df/primeiro
        # Criando um dataframe que contém a posição diária de cada ativo
        PL = precos*qtd_acoes
        # Criando uma coluna que contém a posição consolidada da nossa carteira diariamente
        PL['PL Total'] = PL.iloc[:].sum(axis=1)

        # Apresentando as informações no gráfico
        fig = px.line(PL, x=PL.index, y=PL.columns,
                      title='Posição diária de cada ativo')
        fig.update_xaxes(dtick="M1", tickformat="%b\n%Y",
                         ticklabelmode="period")
        chart_PL = fig.to_html()

        # Obtendo dados do IBOV para comparar com a nossa carteira
        if inicio or fim:
            ibov = yf.download('^BVSP', start=inicio, end=fim)
        else:
            ibov = yf.download('^BVSP', start=ano_passado +
                               '-01-01', end=ano+'-12-31')
        # Renomeando a coluna com o nome IBOV
        ibov.rename(columns={'Adj Close': 'IBOV'}, inplace=True)
        # Limpando as demais colunas
        ibov = ibov.drop(ibov.columns[[0, 1, 2, 3, 5]], axis=1)
        # Verificando se o índice dos dataframes está no formato 'data'
        ibov.index = pd.to_datetime(ibov.index)
        PL.index = pd.to_datetime(PL.index)
        # Juntando tudo num dataframe só
        novo_df = pd.merge(ibov, PL, how='inner', on='Date')
        # Normalizando esse novo dataframe que contém o IBOV, todos os ativos e o PL da nossa carteira
        PL_normalizado = novo_df/novo_df.iloc[0]
        # Filtrando as colunas IBOV e PL Total
        PL_normalizado = PL_normalizado[['IBOV', 'PL Total']]

        # Apresentando as informações no gráfico
        fig = px.line(PL_normalizado, x=PL_normalizado.index,
                      y=PL_normalizado.columns, title='Carteira Vs Ibovespa')
        fig.update_xaxes(dtick="M1", tickformat="%b\n%Y",
                         ticklabelmode="period")
        chart_IBOV_PL = fig.to_html()
        form = DateForm()
        if self.request.GET:
            form = DateForm(self.request.GET)
        context = {'chart': chart, 'chart_PL': chart_PL,
                   'chart_IBOV_PL': chart_IBOV_PL, 'form': form}

        return context

# Cadastrado de Desdobramento


class DesdobramentoCreate(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Desdobramento
    form_class = DesdobramentoForm
    template_name = 'cadastros/desdobramento.html'
    success_url = reverse_lazy('cadastrar-desdobramento')
    success_message = "Desdobramento registrado com sucesso!"

    def form_valid(self, form):
        if form.cleaned_data['a_cada'] <= 0 or form.cleaned_data['desdobra_se'] <= 0:
            context = {
                'message': 'A quantidade não pode ser igual ou menor que 0. Por favor tente novamente.'
            }
            return render(self.request, 'error.html', context)
        else:
            a_cada = form.cleaned_data['a_cada']
            desdobra_se = form.cleaned_data['desdobra_se']
            ativo = Ativo.objects.filter(
                user=self.request.user, quantidade__gt=0, ativo=form.cleaned_data['ativo'])
            nota = Nota.objects.filter(user=self.request.user, quantidade__gt=0,
                                       ativo=form.cleaned_data['ativo'], data__lte=form.cleaned_data['data'])
            qtd_ajustada_ativo = 0
            qtd_ajustada_ativo_venda = 0
            qtd_nota_c = 0
            qtd_nota_v = 0
            ativo = list(ativo)
            ativo = ativo[0].quantidade

            for i in nota:
                qtd_ajustada = int((i.quantidade / a_cada)*desdobra_se)
                preco_ajustado = i.total_compra / qtd_ajustada
                Nota.objects.filter(user=self.request.user, id=i.id).update(
                    quantidade=qtd_ajustada, preco=preco_ajustado)
                if i.tipo == 'C' or i.tipo == 'B':
                    qtd_nota_c += i.quantidade
                    qtd_ajustada_ativo += qtd_ajustada
                else:
                    qtd_nota_v += i.quantidade
                    qtd_ajustada_ativo_venda += qtd_ajustada
                qtd_ajustada_ativo = (
                    qtd_ajustada_ativo-qtd_ajustada_ativo_venda)

            # calculando a diferença de quantidade da nota e do ativo e somando com o desdobramento
            qtd_ajustada_ativo = qtd_ajustada_ativo + \
                (ativo - (qtd_nota_c-qtd_nota_v))
            Ativo.objects.filter(user=self.request.user).update(
                quantidade=qtd_ajustada_ativo)

        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()

        return super().form_valid(form)

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(DesdobramentoCreate,
                       self).get_form_kwargs(*args, **kwargs)
        kwargs['user'] = self.request.user
        return kwargs

# Lista de desdobramento do usuario


class DesdobramentoList(LoginRequiredMixin, ListView):
    login_url = reverse_lazy('account_login')
    model = Desdobramento
    template_name = 'listar/desdobramento.html'

    def get_queryset(self):
        self.object_list = Desdobramento.objects.filter(
            user=self.request.user).order_by('-data')
        return self.object_list

# Deletar desdobramento


class DesdobramentoDelete(LoginRequiredMixin, DeleteView):
    login_url = reverse_lazy('account_login')
    model = Desdobramento
    template_name = 'cadastros/form-excluir-desdobramento.html'
    success_url = reverse_lazy('listar-desdobramento')
    success_message = "%(ativo)s foi desfeito e excluído com sucesso!"

    def delete(self, *args, **kwargs):
        desdobramento = Desdobramento.objects.filter(
            user=self.request.user, id=kwargs['pk'])
        desdobramento = list(desdobramento)
        ativo_d = desdobramento[0].ativo
        a_cada = desdobramento[0].a_cada
        desdobra_se = desdobramento[0].desdobra_se
        data = desdobramento[0].data

        # consultando os ativos e as notas
        ativo = Ativo.objects.filter(
            user=self.request.user, quantidade__gt=0, ativo=ativo_d)
        nota = Nota.objects.filter(
            user=self.request.user, quantidade__gt=0, ativo=ativo_d, data__lte=data)
        qtd_ajustada_ativo = 0
        qtd_ajustada_ativo_venda = 0
        qtd_nota_c = 0
        qtd_nota_v = 0
        ativo = list(ativo)
        ativo = ativo[0].quantidade
        # Desfazendo o desdobramento das notas registradas
        for i in nota:
            qtd_ajustada = int((i.quantidade / desdobra_se)*a_cada)
            preco_ajustado = i.total_compra / qtd_ajustada
            Nota.objects.filter(user=self.request.user, id=i.id, data__lte=data).update(
                quantidade=qtd_ajustada, preco=preco_ajustado)
            if i.tipo == 'C' or i.tipo == 'B':
                qtd_nota_c += i.quantidade
                qtd_ajustada_ativo += qtd_ajustada
            else:
                qtd_nota_v += i.quantidade
                qtd_ajustada_ativo_venda += qtd_ajustada
            qtd_ajustada_ativo = (qtd_ajustada_ativo -
                                  qtd_ajustada_ativo_venda)

        # calculando a diferença de quantidade da nota e do ativo e somando com o desdobramento
        qtd_ajustada_ativo = qtd_ajustada_ativo + \
            (ativo - (qtd_nota_c - qtd_nota_v))
        Ativo.objects.filter(user=self.request.user).update(
            quantidade=qtd_ajustada_ativo)

        return super(DesdobramentoDelete, self).delete(*args, **kwargs)

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(
            cleaned_data,
            ativo=self.object.ativo,
        )

# Cadastro de bonificação


class BonificacaoCreate(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Bonificacao
    form_class = BonificacaoForm
    login_url = reverse_lazy('account_login')
    template_name = 'cadastros/bonificacao.html'
    success_url = reverse_lazy('cadastrar-bonificacao')
    success_message = "Bonificação do %(ativo)s lançada com sucesso!"

    def form_valid(self, form):
        if form.cleaned_data['a_cada'] <= 0 or form.cleaned_data['recebo_bonus_de'] <= 0 or form.cleaned_data['custo_atribuido'] <= 0:
            context = {
                'message': 'A quantidade não pode ser menor ou igual a 0. Por favor tente novamente.'
            }
            return render(self.request, 'error.html', context)
        else:
            ativo_bonificado = form.cleaned_data['ativo']
            data = form.cleaned_data['data']
            a_cada = form.cleaned_data['a_cada']
            recebo_bonus_de = form.cleaned_data['recebo_bonus_de']
            custo_atribuido = form.cleaned_data['custo_atribuido']

            ativo = Ativo.objects.filter(
                user=self.request.user, quantidade__gt=0, ativo=form.cleaned_data['ativo'])
            nota = Nota.objects.filter(
                user=self.request.user, quantidade__gt=0, ativo=form.cleaned_data['ativo'], data__lte=data)
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

                total_compra = Decimal(
                    form.cleaned_data['custo_atribuido'] * qtd_ajustada)
                preco_total_ajustado = i.preco_total + total_compra

            if qtd_ajustada <= 0 or qtd_total_ativo <= 0 or total_compra <= 0 or preco_total_ajustado <= 0:
                context = {
                    'message': 'A quantidade não pode ser menor ou igual a 0. Por favor tente novamente.'
                }
                return render(self.request, 'error.html', context)
            else:
                ativo.update(quantidade=qtd_total_ativo,
                             preco_total=preco_total_ajustado)
                nota.create(ativo=ativo_bonificado.ativo, quantidade=qtd_ajustada, preco=custo_atribuido, data=data, tipo='B', total_compra=total_compra,
                            identificador=ativo_bonificado.ativo+' BONIFICAÇÃO', corretagem=0.0, emolumentos=0.0, tx_liquida_CBLC=0.0, user=self.request.user)

        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()

        return super().form_valid(form)

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(BonificacaoCreate, self).get_form_kwargs(
            *args, **kwargs)
        kwargs['user'] = self.request.user
        return kwargs

# Lista de bonificação do usuario


class BonificacaoList(LoginRequiredMixin, ListView):
    login_url = reverse_lazy('account_login')
    model = Bonificacao
    template_name = 'listar/bonificacao.html'

    def get_queryset(self):
        self.object_list = Bonificacao.objects.filter(
            user=self.request.user).order_by('-data')
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
        bonificacao = Bonificacao.objects.filter(
            user=self.request.user, id=kwargs['pk'])
        bonificacao = list(bonificacao)
        ativo_b = bonificacao[0].ativo
        data = bonificacao[0].data

        ativo = Ativo.objects.filter(
            user=self.request.user, quantidade__gt=0, ativo=ativo_b)
        nota = Nota.objects.filter(
            user=self.request.user, quantidade__gt=0, ativo=ativo_b, data=data, tipo='B')

        qtd_ajustada_ativo = 0
        preco_ajustado_ativo = 0

        # Desfazendo a bonificação das notas registradas
        for i, j in zip(ativo, nota):
            qtd_ajustada_ativo = i.quantidade-j.quantidade
            preco_ajustado_ativo = i.preco_total - j.total_compra
        #  se os valores forem menores ou igual a 0 renderiza para pagina de erro
        if qtd_ajustada_ativo <= 0 and preco_ajustado_ativo <= 0:
            context = {
                'message': 'A quantidade não pode ser menor ou igual a 0. Por favor tente novamente.'
            }
            return render(self.request, 'error.html', context)
        else:
            # apagando a bonificação lançada nas notas
            nota.delete()
            # alterando as quantidades e o preco do ativo
            Ativo.objects.filter(user=self.request.user, ativo=ativo_b).update(
                quantidade=qtd_ajustada_ativo, preco_total=preco_ajustado_ativo)

        return super(BonificacaoDelete, self).delete(*args, **kwargs)

# Cadastrado de Grupamento


class GrupamentoCreate(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Grupamento
    form_class = GrupamentoForm
    template_name = 'cadastros/grupamento.html'
    success_url = reverse_lazy('cadastrar-grupamento')
    success_message = "Grupamento registrado com sucesso!"

    def form_valid(self, form):
        if form.cleaned_data['a_cada'] <= 0 or form.cleaned_data['agrupa_se'] <= 0:
            context = {
                'message': 'A quantidade não pode ser igual ou menor que 0. Por favor tente novamente.'
            }
            return render(self.request, 'error.html', context)
        else:
            a_cada = form.cleaned_data['a_cada']
            agrupa_se = form.cleaned_data['agrupa_se']
            ativo = Ativo.objects.filter(
                user=self.request.user, quantidade__gt=0, ativo=form.cleaned_data['ativo'])
            nota = Nota.objects.filter(user=self.request.user, quantidade__gt=0,
                                       ativo=form.cleaned_data['ativo'], data__lte=form.cleaned_data['data'])
            qtd_ajustada_ativo = 0
            qtd_ajustada_ativo_venda = 0
            qtd_nota_c = 0
            qtd_nota_v = 0
            ativo = list(ativo)
            ativo = ativo[0].quantidade

            for i in nota:
                qtd_ajustada = int((i.quantidade / a_cada)*agrupa_se)
                preco_ajustado = i.total_compra / qtd_ajustada
                Nota.objects.filter(user=self.request.user, id=i.id).update(
                    quantidade=qtd_ajustada, preco=preco_ajustado)
                if i.tipo == 'C' or i.tipo == 'B':
                    qtd_nota_c += i.quantidade
                    qtd_ajustada_ativo += qtd_ajustada
                else:
                    qtd_nota_v += i.quantidade
                    qtd_ajustada_ativo_venda += qtd_ajustada
                qtd_ajustada_ativo = (
                    qtd_ajustada_ativo-qtd_ajustada_ativo_venda)

            # calculando a diferença de quantidade da nota e do ativo e somando com o desdobramento
            qtd_ajustada_ativo = qtd_ajustada_ativo + \
                (ativo - (qtd_nota_c-qtd_nota_v))
            Ativo.objects.filter(user=self.request.user).update(
                quantidade=qtd_ajustada_ativo)

        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()

        return super().form_valid(form)

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(GrupamentoCreate, self).get_form_kwargs(*args, **kwargs)
        kwargs['user'] = self.request.user
        return kwargs

# Lista de desdobramento do usuario


class GrupamentoList(LoginRequiredMixin, ListView):
    login_url = reverse_lazy('account_login')
    model = Grupamento
    template_name = 'listar/grupamento.html'

    def get_queryset(self):
        self.object_list = Grupamento.objects.filter(
            user=self.request.user).order_by('-data')
        return self.object_list

# Deletar Grupamento


class GrupamentoDelete(LoginRequiredMixin, DeleteView):
    login_url = reverse_lazy('account_login')
    model = Grupamento
    template_name = 'cadastros/form-excluir-grupamento.html'
    success_url = reverse_lazy('listar-grupamento')
    success_message = "%(ativo)s foi desfeito e excluído com sucesso!"

    def delete(self, *args, **kwargs):
        grupamento = Grupamento.objects.filter(
            user=self.request.user, id=kwargs['pk'])
        grupamento = list(grupamento)
        ativo_g = grupamento[0].ativo
        a_cada = grupamento[0].a_cada
        agrupa_se = grupamento[0].agrupa_se
        data = grupamento[0].data

        # consultando os ativos e as notas
        ativo = Ativo.objects.filter(
            user=self.request.user, quantidade__gt=0, ativo=ativo_g)
        nota = Nota.objects.filter(
            user=self.request.user, quantidade__gt=0, ativo=ativo_g, data__lte=data)
        qtd_ajustada_ativo = 0
        qtd_ajustada_ativo_venda = 0
        qtd_nota_c = 0
        qtd_nota_v = 0
        ativo = list(ativo)
        ativo = ativo[0].quantidade
        # Desfazendo o desdobramento das notas registradas
        for i in nota:
            qtd_ajustada = int((i.quantidade / agrupa_se)*a_cada)
            preco_ajustado = i.total_compra / qtd_ajustada
            Nota.objects.filter(user=self.request.user, id=i.id, data__lte=data).update(
                quantidade=qtd_ajustada, preco=preco_ajustado)
            if i.tipo == 'C' or i.tipo == 'B':
                qtd_nota_c += i.quantidade
                qtd_ajustada_ativo += qtd_ajustada
            else:
                qtd_nota_v += i.quantidade
                qtd_ajustada_ativo_venda += qtd_ajustada
            qtd_ajustada_ativo = (qtd_ajustada_ativo -
                                  qtd_ajustada_ativo_venda)

        # calculando a diferença de quantidade da nota e do ativo e somando com o desdobramento
        qtd_ajustada_ativo = qtd_ajustada_ativo + \
            (ativo - (qtd_nota_c - qtd_nota_v))
        Ativo.objects.filter(user=self.request.user).update(
            quantidade=qtd_ajustada_ativo)

        return super(GrupamentoDelete, self).delete(*args, **kwargs)

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(
            cleaned_data,
            ativo=self.object.ativo,
        )


# função para enviar email com contato
def contato(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = ContatoForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            form.send_mail()
            messages.success(request, "Mensagem enviada com sucesso.")
            form = ContatoForm()
            return HttpResponseRedirect('/contact')
        else:
            messages.error(
                request, "Não foi possivel enviar a mensagem, por favor tente mais tarde.")
            return HttpResponseRedirect('/contact')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = ContatoForm()

    return render(request, 'contact.html', {'form': form})

def save_to_s3(file, bucket_name, key_name):
    s3 = boto3.client('s3')
    try:
        s3.upload_fileobj(file.file, bucket_name, key_name)
        print("Upload realizado com sucesso!")
        return True
    except FileNotFoundError as e:
        print("Arquivo não encontrado.", e)
        return False
    except NoCredentialsError as e:
        print("Credenciais inválidas.", e)
        return False


from django.conf import settings

def generate_unique_filename(filename):
    extension = filename.split('.')[-1]
    new_filename = f"{uuid.uuid4().hex}.{extension}"
    return new_filename

@login_required
def edit_profile(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile(user=request.user)
        profile.save()

    user_form = UserForm(instance=request.user)
    profile_form = ProfileForm(instance=profile)

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(
            request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()

            s3 = boto3.client('s3')
            if 'image' in request.FILES:
                file = request.FILES['image']
                if profile.image:
                    # Delete the old file
                    s3.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=profile.image.name)
                # Save the new file
                file_name = generate_unique_filename(file.name)
                s3.upload_fileobj(file, settings.AWS_STORAGE_BUCKET_NAME, file_name)
                profile.image = file_name
            else:
                # Delete the old file
                if profile.image:
                    s3.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=profile.image.name)
                profile.image = None
            
            profile = profile_form.save(commit=False)
            profile.save()

            messages.success(request, 'Seu perfil foi atualizado com sucesso!')
            return redirect('edit_profile')

    return render(request, 'account/edit_profile.html', {'user_form': user_form, 'profile_form': profile_form})


@login_required
def grafico_proventos(request):
    # Define o locale como o Brasil para exibir os valores em reais
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

    data = Proventos.objects.all().filter(user=request.user)
    data_dict = {}
    for d in data:
        if d.ativo not in data_dict:
            data_dict[d.ativo] = {'D': 0, 'J': 0}
        if d.tipo_provento == 'D':
            data_dict[d.ativo]['D'] += d.valor
        elif d.tipo_provento == 'J':
            data_dict[d.ativo]['J'] += d.valor

    x = []
    y1 = []
    y2 = []
    for key, value in data_dict.items():
        x.append(key)
        y1.append(value['D'])
        y2.append(value['J'])

    # Formata os valores em reais
    y1_reais = [locale.currency(v, grouping=True, symbol="R$") for v in y1]
    y2_reais = [locale.currency(v, grouping=True, symbol="R$") for v in y2]

    trace1 = go.Bar(x=x, y=y1, name='Dividendos',
                    text=y1_reais, textposition='auto')
    trace2 = go.Bar(x=x, y=y2, name='Juros Compostos',
                    text=y2_reais, textposition='auto')
    data1 = [trace1, trace2]

    # Gráfico de total por mês do ano
    data2 = []
    meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
             'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    for m in meses:
        total = data.filter(data__month=meses.index(
            m) + 1).aggregate(Sum('valor'))['valor__sum'] or 0
        total_reais = locale.currency(total, grouping=True, symbol="R$")
        data2.append(go.Bar(x=[m], y=[total], text=[
                     total_reais], textposition='auto'))

    # Gráfico de total por ano
    data3 = []
    anos = data.dates('data', 'year')

    for a in anos:
        total = data.filter(data__year=a.year).aggregate(
            Sum('valor'))['valor__sum'] or 0
        total_reais = locale.currency(total, grouping=True, symbol="R$")
        data3.append(go.Bar(x=[a.year], y=[total], text=[
                     total_reais], textposition='auto'))

    # Primeiro grafico
    layout1 = go.Layout(barmode='stack')
    fig1 = go.Figure(data=data1, layout=layout1)
    total1 = sum(y1) + sum(y2)
    total1_reais = locale.currency(total1, grouping=True, symbol="R$")
    fig1.update_layout(
        title=f'Total de proventos por ativo {total1_reais}',
        xaxis_title='Ativos',
        yaxis_title='Valor total em reais',
    )

    # Segundo grafico
    layout2 = go.Layout(title='Total de proventos por mês do ano')
    fig2 = go.Figure(data=data2, layout=layout2)
    total2 = sum([d['y'][0] for d in data2])
    total2_reais = locale.currency(total2, grouping=True, symbol="R$")
    fig2.update_layout(
        xaxis_title='Mês',
        yaxis_title='Valor total em reais',
        annotations=[dict(
            x=meses.index('Dezembro'),
            y=data2[meses.index('Dezembro')]['y'][0],
            name=meses.index('Dezembro'),
            text=f'Total: {total2_reais}',
            showarrow=True,
            arrowhead=1
        )]
    )
    fig2.update_traces(showlegend=False)

    # Terceiro grafico
    layout3 = go.Layout(title='Total de proventos por ano')
    fig3 = go.Figure(data=data3, layout=layout3)
    total3 = sum([d['y'][0] for d in data3])
    total3_reais = locale.currency(total3, grouping=True, symbol="R$")
    # fig3.update_layout(
    #     xaxis_title='Ano',
    #     yaxis_title='Valor total em reais',
    #     annotations=[dict(
    #         x=anos.count() - 1,
    #         y=data3[-1]['y'][0],
    #         text=f'Total: {total3_reais}',
    #         showarrow=True,
    #         arrowhead=1
    #     )]
    # )
    fig3.update_traces(showlegend=False)

    # Converte os gráficos para HTML
    div1 = plot(fig1, output_type='div')
    div2 = plot(fig2, output_type='div')
    div3 = plot(fig3, output_type='div')

    # Renderiza o template e passa as variáveis para a página
    return render(request, 'proventos/grafico_proventos.html', {'div1': div1, 'div2': div2, 'div3': div3})

# relatorio de custo, lucro bruto, liquido e receitas
@login_required
def relatorio(request):
    if request.method == 'POST':
        ano_base = request.POST.get('ano_base')
        user = request.user

        # Filtra os proventos pelo ano selecionado
        proventos = Proventos.objects.filter(
            user=user, data__year=ano_base).aggregate(Sum('valor'))

        # Filtra as notas de compra e venda pelo ano selecionado
        notas_compra = Nota.objects.filter(
            user=user, tipo='C', data__year=ano_base)
        notas_venda = Nota.objects.filter(
            user=user, tipo='V', data__year=ano_base)

        # Calcula o custo total das notas de compra
        custo_total = notas_compra.aggregate(Sum('total_custo'))[
            'total_custo__sum'] or 0

        # Calcula a receita total das notas de venda
        venda_total = notas_venda.aggregate(Sum('total_compra'))['total_compra__sum'] or 0

        # Calcula o lucro líquido
        lucro_bruto = venda_total - custo_total
        # Calcula o lucro líquido
        # exemplo de impostos aplicando 15% no lucro bruto
        impostos = Decimal('0.15') * lucro_bruto
        lucro_liquido = lucro_bruto - impostos

        # Cria uma lista de anos para preencher o campo de seleção no formulário
        years = range(datetime.now().year - 5, datetime.now().year + 1)

        # Passa os dados do relatório e a lista de anos para o template
        context = {'proventos': proventos['valor__sum'] or 0,
                   'custo_total': custo_total,
                   'venda_total': venda_total,
                   'lucro_liquido': lucro_liquido,
                   'lucro_bruto': lucro_bruto,
                   'years': years,
                   'ano_base': ano_base}
        return render(request, 'relatorio_ir.html', context)

    # Cria uma lista de anos para preencher o campo de seleção no formulário
    years = range(datetime.now().year - 5, datetime.now().year + 1)

    # Renderiza o formulário com a lista de anos
    return render(request, 'relatorio_ir_form.html', {'years': years})

# Gerando grafico de compra e venda de ações 
class SalesChartJSONView(BaseLineChartView):
    def get_labels(self):
        anos = []
        for nota in Nota.objects.filter(user=self.request.user):
            if nota.data.year not in anos:
                anos.append(nota.data.year)
        anos.sort()
        return anos

    def get_providers(self):
        return ['Vendas', 'Compras']

    def get_data(self):
        anos = self.get_labels()
        data_vendas = []
        data_compras = []
        for ano in anos:
            notas_venda = Nota.objects.filter(user=self.request.user, data__year=ano, tipo='V').aggregate(Sum('total_compra'))
            venda_total = notas_venda['total_compra__sum'] or 0
            notas_compra = Nota.objects.filter(user=self.request.user, data__year=ano, tipo='C').aggregate(Sum('total_compra'))
            compra_total = notas_compra['total_compra__sum'] or 0
            data_vendas.append(venda_total)
            data_compras.append(compra_total)
        return [data_vendas, data_compras]


def compare(request):
    if request.method == 'POST':
        stock1 = request.POST.get('stock1')
        stock2 = request.POST.get('stock2')

        ticker1 = yf.Ticker(stock1)
        ticker2 = yf.Ticker(stock2)

        stock_data1 = ticker1.info
        stock_data2 = ticker2.info

        indicators = {
            'P_L': 'trailingPE',
            'DY': 'dividendYield',
            'P_VPA': 'priceToBook',
            'EV_EBITDA': 'enterpriseToEbitda',
            'P_A': 'priceToSalesTrailing12Months',
            'ROE': 'returnOnEquity',
            'Divida_Liquida_Patrimonio_Liquido': 'debtToEquity',
            'Margem_Bruta': 'grossMargins',
            'Margem_Liquida': 'profitMargins',
        }

        data = {}

        for indicator, value in indicators.items():
            data[indicator] = {
                stock1: stock_data1.get(value),
                stock2: stock_data2.get(value),
            }
        print(data)

        return render(request, 'listar/compare.html', {'data': data})
    
    return render(request, 'listar/compare.html')


# Renderezação de erros
def error_500(request):
    return render(request, '500.html')


def error_404(request, exception):
    return render(request, '404.html')
