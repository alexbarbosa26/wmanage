from django.views.generic import TemplateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from .forms import ProfileForm


class HomePageView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('account_login')
    template_name = "home.html"


# Edit Profile View
class ProfileView(UpdateView):
    model = User
    form_class = ProfileForm
    success_url = reverse_lazy('listar-ordens')
    template_name = 'account/profile.html'
