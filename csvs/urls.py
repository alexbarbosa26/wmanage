from django.urls import path
from .views import upload_files_view, upload_files_view_cotacao, upload_files_view_proventos


# app_name='csvs'

urlpatterns = [
    path('csv/import-notas/', upload_files_view, name='upload-view'),
    path('csv/import-cotacao/', upload_files_view_cotacao, name='upload-view-cotacao'),
    path('csv/import-provento/', upload_files_view_proventos, name='upload-view-provento'),
]