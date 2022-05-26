from django import forms
from core.models import Ativo, Desdobramento
from django.forms.widgets import Select

class DateForm(forms.ModelForm):
    data_inicio = forms.DateField(widget=forms.DateInput(attrs={'type':'date'}))
    data_fim = forms.DateField(widget=forms.DateInput(attrs={'type':'date'}))

class CustomModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, ativo):
        return "%s" % ativo.ativo

class DesdobramentoForm(forms.ModelForm):    

    def __init__(self, user=None, *args, **kwargs):

        # self.request = kwargs.pop('request')
        super(DesdobramentoForm, self).__init__(*args, **kwargs)
        self.fields['ativo'].queryset = Ativo.objects.filter(user=user, quantidade__gt=0)

    class Meta:
        model= Desdobramento
        fields = '__all__'

    ativo = CustomModelChoiceField(queryset=None, widget=Select(attrs={'data-live-search': 'true', 'Class':'selectpicker border rounded'}))
    data = forms.DateField(widget=forms.DateInput(attrs={'type':'date'}))