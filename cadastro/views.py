from .models import Ativo, Nota, Proventos, Cotacao
import json
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

#Set Locale
locale.setlocale(locale.LC_ALL, 'pt_BR')

#Create
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

        if ativo_reg == [] and form.cleaned_data['tipo'] == 'V':
            context ={
                'message':'Não foi possível registrar sua ordem, por favor verifique a quantidade correta informada.'
            }
            return render(self.request, 'error.html', context)

        elif ativo_reg == [] and form.cleaned_data['tipo'] == 'C' and form.cleaned_data['quantidade'] > 0 and cotacao_reg == []:
            Ativo.objects.create(ativo=form.cleaned_data['ativo'],  quantidade=form.cleaned_data['quantidade'], preco_total=form.cleaned_data['quantidade']*form.cleaned_data['preco'], user=self.request.user)
            Cotacao.objects.create(acao=form.cleaned_data['identificador'], ativo=form.cleaned_data['ativo'])

        elif ativo_reg == [] and form.cleaned_data['tipo'] == 'C' and form.cleaned_data['quantidade'] > 0 and cotacao_reg != []:
            Ativo.objects.create(ativo=form.cleaned_data['ativo'],  quantidade=form.cleaned_data['quantidade'], preco_total=form.cleaned_data['quantidade']*form.cleaned_data['preco'], user=self.request.user)
            Cotacao.objects.create(acao=form.cleaned_data['identificador'], ativo=form.cleaned_data['ativo'])        

        elif form.cleaned_data['tipo'] == 'C' and form.cleaned_data['quantidade'] > 0 and cotacao_reg == []:
            ativo_reg[0]['quantidade'] = ativo_reg[0]['quantidade'] + form.cleaned_data['quantidade']
            ativo_reg[0]['preco_total'] = ativo_reg[0]['preco_total'] + (form.cleaned_data['quantidade']*form.cleaned_data['preco'])
            Ativo.objects.filter(ativo=form.cleaned_data['ativo'], user=self.request.user).update(ativo=form.cleaned_data['ativo'], quantidade=ativo_reg[0]['quantidade'], preco_total=ativo_reg[0]['preco_total'], user=self.request.user)
            Cotacao.objects.create(acao=form.cleaned_data['identificador'], ativo=form.cleaned_data['ativo'])

        elif form.cleaned_data['tipo'] == 'C' and form.cleaned_data['quantidade'] > 0 and cotacao_reg != []:
            ativo_reg[0]['quantidade'] = ativo_reg[0]['quantidade'] + form.cleaned_data['quantidade']
            ativo_reg[0]['preco_total'] = ativo_reg[0]['preco_total'] + (form.cleaned_data['quantidade']*form.cleaned_data['preco'])
            Ativo.objects.filter(ativo=form.cleaned_data['ativo'], user=self.request.user).update(ativo=form.cleaned_data['ativo'], quantidade=ativo_reg[0]['quantidade'], preco_total=ativo_reg[0]['preco_total'], user=self.request.user)
        
        elif form.cleaned_data['tipo'] == 'V' and form.cleaned_data['quantidade'] <= ativo_reg[0]['quantidade']:
            ativo_reg[0]['quantidade'] = ativo_reg[0]['quantidade'] - form.cleaned_data['quantidade']
            ativo_reg[0]['preco_total'] = ativo_reg[0]['preco_total'] - (form.cleaned_data['quantidade']*form.cleaned_data['preco'])
            Ativo.objects.filter(ativo=form.cleaned_data['ativo'], user=self.request.user).update(ativo=form.cleaned_data['ativo'], quantidade=ativo_reg[0]['quantidade'], preco_total=ativo_reg[0]['preco_total'], user=self.request.user)

        else:
            context ={
                'message':'Não foi possível registrar sua ordem, por favor verifique a quantidade correta e tente novamente'
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
        self.object_list = Nota.objects.filter(user=self.request.user).order_by('data')
        return self.object_list


# Delete
class NotaDelete(GroupRequiredMixin, LoginRequiredMixin, DeleteView):
    login_url = reverse_lazy('account_login')
    group_required = u'Administrador'
    model = Nota
    template_name = 'cadastros/form-excluir.html'
    success_url = reverse_lazy('listar-ordens')
    success_message = "%(ativo)s deletado com sucesso!"

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
        qtd_antigo = Nota.objects.values('quantidade','total_compra').filter(id=self.object.id, user=self.request.user)
        qtd_antigo = list(qtd_antigo)
        
        ativo_reg = Ativo.objects.values().filter(ativo=form.cleaned_data['ativo'], user=self.request.user)
        ativo_reg = list(ativo_reg)

        if ativo_reg[0]['quantidade'] == 0:
            context ={
                'message':'Seu saldo é 0 por favor lance uma nota de compra.'
            }
            return render(self.request, 'error.html', context)

        elif ativo_reg == [] and form.cleaned_data['tipo'] == 'V' and form.cleaned_data['quantidade'] < 0:
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
        status_fechado_aberto = 'Aguardando o cadastro de ações'
        x = 0
        y = 0
        v = 0
        result_compra = Nota.objects.values('ativo').annotate(qt=Sum('quantidade'), preco_f=Sum('total_compra'), custos=Sum('total_custo'), preco_m=Sum('preco'), v_mercado=Sum('preco'), lucro=Sum('preco'), variacao_mercado_1=Count('identificador'), variacao_mercado_2=Count('identificador')).filter(tipo='C', user=self.request.user)
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
            # else:
            #     pass

        pro = 0
        pro_result = []
        pro_result = 0
        proventos = Proventos.objects.filter(user=self.request.user)
        for i in proventos:
            pro = i.valor + pro

        pro_result = locale.currency(pro, grouping=True)
        
        context = {
            'result_c' : r_result,
            'total_lucro' : total_lucro,
            'total_investido' : total_investido,
            'total_v_mercado' : total_v_mercado,
            'total_proventos' : pro_result,
            'status_fechado_aberto' : status_fechado_aberto,
            'ultima_atualizacao': ultima_atualizacao,
            'porcentagem_lucro': porcentagem_lucro,            
        }
        
        return context

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

class ProventosList(LoginRequiredMixin,ListView):
    login_url = reverse_lazy('account_login')
    model = Proventos
    template_name = 'listar/proventos.html'

    def get_queryset(self):
        self.object_list = Proventos.objects.filter(user=self.request.user).order_by('data')
        return self.object_list

# Delete
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
        r_result = []
        status_fechado_aberto = []
        status_fechado_aberto = 'Aguardando o cadastro de ações'
        x = 0
        y = 0
        v = 0
        result_compra = Nota.objects.values('ativo').annotate(qt=Sum('quantidade'), preco_f=Sum('total_compra'), custos=Sum('total_custo'), preco_m=Sum('preco'), v_mercado=Sum('preco'), lucro=Sum('preco'), variacao_mercado_1=Count('identificador'), variacao_mercado_2=Count('identificador')).filter(tipo='C', user=self.request.user)
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

                compra['lucro'] = locale.currency(compra['lucro'], grouping=True)
                compra['preco_m'] = locale.currency(Decimal(preco_mercado.fechamento_ajustado.replace(",",".")), grouping=True)
                compra['preco_f'] = locale.currency(compra['preco_f'], grouping=True)
                compra['custos'] = locale.currency(compra['custos'], grouping=True)
                compra['variacao_1'] = preco_mercado.variacao_1
                compra['variacao_2'] = preco_mercado.variacao_2
                

                r_result.append(compra)
            else:
                pass
        names = []
        prices = []
        for i in r_result:
            
            names.append(i['ativo'])
            prices.append(i['qt'])
        
        context = {
            'names' : json.dumps(names),
            'prices' : json.dumps(prices)
        }
        
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

def export_proventos_xls(request):
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

    rows = Proventos.objects.all().values_list('ativo', 'tipo_provento', 'data', 'valor')
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response