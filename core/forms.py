from django import forms
from core.models import Ativo, Bonificacao, Desdobramento, Grupamento, Proventos, Profile
from django.forms.widgets import Select
from bootstrap_datepicker_plus import DatePickerInput
from django.core.mail import EmailMessage
from django.contrib.auth.models import User

class CompararAcoesForm(forms.Form):
    acao1 = forms.CharField(label='Ação 1', max_length=10)
    acao2 = forms.CharField(label='Ação 2', max_length=10)
    start_date = forms.DateField(label='Data Inicial', widget=forms.widgets.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(label='Data Final', widget=forms.widgets.DateInput(attrs={'type': 'date'}))

class CalculadoraForm(forms.Form):
    ticker = forms.CharField(max_length=10)
    acoes = forms.IntegerField()

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('image',)

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

    ativo = forms.ModelChoiceField(queryset=None, widget=Select(attrs={'data-live-search': 'true', 'Class':'selectpicker border rounded col-md-12', 'autofocus':''}))
    data = forms.DateField(widget=DatePickerInput(format='%d/%m/%Y',options={'locale':'pt-br'}, attrs={'placeholder':'DD/MM/AAAA'}))

class BonificacaoForm(forms.ModelForm):
    class Meta:
        model = Bonificacao
        exclude = ('user',)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(BonificacaoForm, self).__init__(*args, **kwargs)
        self.fields['ativo'].queryset  = Ativo.objects.filter(user=self.user, quantidade__gt=0)

    ativo = forms.ModelChoiceField(queryset=None, widget=Select(attrs={'data-live-search': 'true', 'Class':'selectpicker border rounded col-md-12', 'autofocus':''}))
    data = forms.DateField(widget=DatePickerInput(format='%d/%m/%Y',options={'locale':'pt-br'}, attrs={'placeholder':'DD/MM/AAAA'}))
    
class GrupamentoForm(forms.ModelForm):
    class Meta:
        model = Grupamento
        exclude = ('user',)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(GrupamentoForm, self).__init__(*args, **kwargs)
        self.fields['ativo'].queryset = Ativo.objects.filter(user=self.user, quantidade__gt=0)
    
    ativo = forms.ModelChoiceField(queryset=None, widget=Select(attrs={'data-live-search': 'true', 'Class':'selectpicker border rounded col-md-12', 'autofocus':''}))
    data = forms.DateField(widget=DatePickerInput(format='%d/%m/%Y',options={'locale':'pt-br'}, attrs={'placeholder':'DD/MM/AAAA'}))

class ProventosForm(forms.ModelForm):
    class Meta:
        model = Proventos
        exclude = ('user',)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(ProventosForm, self).__init__(*args, **kwargs)
        self.fields['ativo'].queryset = Ativo.objects.filter(user=self.user, quantidade__gt=0)
    
    ativo = forms.ModelChoiceField(queryset=None, widget=Select(attrs={'data-live-search': 'true', 'Class':'selectpicker border rounded col-md-12', 'autofocus':''}))
    data = forms.DateField(widget=DatePickerInput(format='%d/%m/%Y',options={'locale':'pt-br'}, attrs={'placeholder':'DD/MM/AAAA'}))

class ContatoForm(forms.Form):
    nome = forms.CharField(label="Nome", max_length=150)
    email = forms.EmailField(label="E-mail", max_length=150)
    assunto = forms.CharField(label="Assunto", max_length=250)
    mensagem = forms.CharField(label="mensagem", widget=forms.Textarea())

    def send_mail(self):
        nome = self.cleaned_data['nome']
        email = self.cleaned_data['email']
        assunto = self.cleaned_data['assunto']
        mensagem = self.cleaned_data['mensagem']

        corpo = f"Nome: {nome}\nE-mail: {email}\n{mensagem}"

        mail = EmailMessage(
            subject=assunto,
            from_email='abarbosasilva7@gmail.com',
            to=[email,],
            body=corpo,
            headers={
                'Replay-To':'abarbosasilva7@gmail.com'
            }
        )
        mail.send()