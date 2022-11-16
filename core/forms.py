from django import forms
from core.models import Ativo, Bonificacao, Desdobramento, Grupamento
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

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(BonificacaoForm, self).__init__(*args, **kwargs)
        self.fields['ativo'].queryset  = Ativo.objects.filter(user=self.user, quantidade__gt=0)

    ativo = forms.ModelChoiceField(queryset=None, widget=Select(attrs={'data-live-search': 'true', 'Class':'selectpicker border rounded', 'autofocus':''}))
    data = forms.DateField(widget=DatePickerInput(format='%d/%m/%Y',options={'locale':'pt-br'}, attrs={'placeholder':'DD/MM/AAAA'}))
    
class GrupamentoForm(forms.ModelForm):
    class Meta:
        model = Grupamento
        exclude = ('user',)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(GrupamentoForm, self).__init__(*args, **kwargs)
        self.fields['ativo'].queryset = Ativo.objects.filter(user=self.user, quantidade__gt=0)
    
    ativo = forms.ModelChoiceField(queryset=None, widget=Select(attrs={'data-live-search': 'true', 'Class':'selectpicker border rounded', 'autofocus':''}))
    data = forms.DateField(widget=DatePickerInput(format='%d/%m/%Y',options={'locale':'pt-br'}, attrs={'placeholder':'DD/MM/AAAA'}))
    

# class CustomUserCreationForm(UserCreationForm):
#     class Meta:
#         model = get_user_model()
#         fields = ('email', 'username', 'avatar')

#     def clean_avatar(self):
#         avatar = self.cleaned_data['avatar']

#         try:
#             w, h = get_image_dimensions(avatar)

#             # validate dimensions
#             max_width = max_height = 100
#             if w > max_width or h > max_height:
#                 raise forms.ValidationError(
#                     u'Please use an image that is '
#                     '%s x %s pixels or smaller.' % (max_width, max_height))

#             # validate content type
#             main, sub = avatar.content_type.split('/')
#             if not (main == 'image' and sub in ['jpeg', 'pjpeg', 'gif', 'png']):
#                 raise forms.ValidationError(u'Please use a JPEG, '
#                                             'GIF or PNG image.')

#             # validate file size
#             if len(avatar) > (20 * 1024):
#                 raise forms.ValidationError(
#                     u'Avatar file size may not exceed 20k.')

#         except AttributeError:
#             """
#             Handles case when we are updating the user profile
#             and do not supply a new avatar
#             """
#             pass

#         return avatar

# class CustomUserChangeForm(UserChangeForm):
#     class Meta:
#         model = get_user_model()
#         fields = ('email', 'username', 'avatar')

#     def clean_avatar(self):
#         avatar = self.cleaned_data['avatar']

#         try:
#             w, h = get_image_dimensions(avatar)

#             # validate dimensions
#             max_width = max_height = 100
#             if w > max_width or h > max_height:
#                 raise forms.ValidationError(
#                     u'Please use an image that is '
#                     '%s x %s pixels or smaller.' % (max_width, max_height))

#             # validate content type
#             main, sub = avatar.content_type.split('/')
#             if not (main == 'image' and sub in ['jpeg', 'pjpeg', 'gif', 'png']):
#                 raise forms.ValidationError(u'Please use a JPEG, '
#                                             'GIF or PNG image.')

#             # validate file size
#             if len(avatar) > (20 * 1024):
#                 raise forms.ValidationError(
#                     u'Avatar file size may not exceed 20k.')

#         except AttributeError:
#             """
#             Handles case when we are updating the user profile
#             and do not supply a new avatar
#             """
#             pass

#         return avatar