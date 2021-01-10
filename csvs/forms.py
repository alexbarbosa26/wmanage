from django import forms
from .models import Csv

class CsvModelForm(forms.ModelForm):
    class Meta:
        model = Csv
        fields = ['file_name',]

        labels = {
            'file_name': ('Arquivo CSV'),
        }
        help_texts = {
            'file_name': ('Apenas importe arquivos (*.CSV), não pode conter espaço e os valores no formato decimal deve ter ponto ( . )'),
        }
        error_messages = {
            'file_name': {
                'max_length': ("This writer's name is too long."),
                'required': ("This writer's name is too long."),
            },
        }