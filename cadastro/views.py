from .models import Ativo, Nota

from django.shortcuts import render
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.edit import CreateView
from bootstrap_datepicker_plus import DatePickerInput
import locale

#Set Locale
locale.setlocale(locale.LC_ALL, '')

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

#Create
class NotaCreate(LoginRequiredMixin,SuccessMessageMixin, CreateView):
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
        ativo_reg = Ativo.objects.values().filter(ativo=form.cleaned_data['ativo'], user=self.request.user)
        ativo_reg = list(ativo_reg)

        if ativo_reg == [] and form.cleaned_data['tipo'] == 'V':
            context ={
                'message':'Não foi possível registrar sua ordem, por favor verifique a quantidade correta informada.'
            }
            return render(self.request, 'error.html', context)

        elif ativo_reg == [] and form.cleaned_data['tipo'] == 'C' and form.cleaned_data['quantidade'] > 0:
            Ativo.objects.create(ativo=form.cleaned_data['ativo'],  quantidade=form.cleaned_data['quantidade'], preco_total=form.cleaned_data['quantidade']*form.cleaned_data['preco'], user=self.request.user)
        
        elif form.cleaned_data['tipo'] == 'C' and form.cleaned_data['quantidade'] > 0 :
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
