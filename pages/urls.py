from django.urls import path
from cadastro.views import WalletView
from .views import ProfileView

app_name = "pages"

urlpatterns = [
    path('', WalletView.as_view(), name="home"),
    path('accounts/profile/<int:pk>/', ProfileView.as_view(), name='profile'),
]