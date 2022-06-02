from django import forms
from core.models import Ativo, Bonificacao, Desdobramento
from django.forms.widgets import Select
from bootstrap_datepicker_plus import DatePickerInput

class DateForm(forms.Form):
    data_inicio = forms.DateField(widget=forms.DateInput(attrs={'type':'date'}))
    data_fim = forms.DateField(widget=forms.DateInput(attrs={'type':'date'}))

class DesdobramentoForm(forms.ModelForm):    
    class Meta:
        model= Desdobramento
        exclude = ('user',)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(DesdobramentoForm, self).__init__(*args, **kwargs)
        self.fields['ativo'].queryset = Ativo.objects.filter(user=self.user, quantidade__gt=0)

    ativo = forms.ModelChoiceField(queryset=None, widget=Select(attrs={'data-live-search': 'true', 'Class':'selectpicker border rounded', 'autofocus':''}))
    data = forms.DateField(widget=DatePickerInput(format='%d/%m/%Y',options={'locale':'pt-br'}, attrs={'placeholder':'DD/MM/AAAA'}))

class BonificacaoForm(forms.ModelForm):
    class Meta:
        model = Bonificacao
        exclude = ('user',)

    def __ini__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(BonificacaoForm, self).__init__(*args, **kwargs)
        self.fields['ativo'].queryset  = Ativo.objects.filter(user=self.user, quantidade__gt=0)

    ativo = forms.ModelChoiceField(queryset=None, widget=Select(attrs={'data-live-search': 'true', 'Class':'selectpicker border rounded', 'autofocus':''}))
    data = forms.DateField(widget=DatePickerInput(format='%d/%m/%Y',options={'locale':'pt-br'}, attrs={'placeholder':'DD/MM/AAAA'}))
    
            