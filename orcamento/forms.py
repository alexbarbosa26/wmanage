from django import forms
from .models import Categoria, Subcategoria, Lancamento

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nome', 'tipo']


class SubcategoriaForm(forms.ModelForm):
    class Meta:
        model = Subcategoria
        fields = ['nome', 'categoria']


class LancamentoForm(forms.ModelForm):
    data = forms.DateField(widget=forms.widgets.DateInput(attrs={'type': 'date'}))
    class Meta:
        model = Lancamento
        fields = ['descricao', 'categoria', 'subcategoria', 'valor', 'data']


        # widgets = {
        #     'subcategoria': autocomplete.ModelSelect2(url='orcamento:subcategoria-autocomplete')
        # }
