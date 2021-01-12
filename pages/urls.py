from django.urls import path
from cadastro.views import WalletView

app_name = "pages"

urlpatterns = [
    path('', WalletView.as_view(), name="home"),
]