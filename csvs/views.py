from decimal import *
from django.contrib.auth.models import User
from django.shortcuts import render
from .forms import CsvModelForm
from .models import Csv
from cadastro.models import Nota, Cotacao, Proventos
import csv

# Create your views here.
def upload_files_view(request):
    form = CsvModelForm(request.POST or None, request.FILES or None)
    
    if form.is_valid():              
        form.save()
        form = CsvModelForm()            
        obj = Csv.objects.get(activated=False)
        with open(obj.file_name.path, 'r', encoding="latin1") as f:
            reader = csv.reader(f)
            print(reader)
            for i, row in enumerate(reader):
                if i==0:
                    pass
                else:
                    row = "".join(row)
                    row = row.replace(";"," ")
                    row = row.split()
                    ativo = row[1].upper()

                    Nota.objects.create(
                        ativo = ativo,
                        quantidade = int(row[2]),
                        preco = Decimal(row[3]),
                        data = row[4],
                        tipo = row[5],
                        identificador = row[6],
                        corretagem= Decimal(row[7]),
                        emolumentos = Decimal(row[8]),
                        tx_liquida_CBLC = Decimal(row[9]),
                        user = request.user,
                    )
            obj.activated = True
            obj.save()
                    
    return render(request,'upload/upload.html',{'form':form})


# Create your views cotacão
def upload_files_view_cotacao(request):
    form_cotacao = CsvModelForm(request.POST or None, request.FILES or None)
    
    if form_cotacao.is_valid():              
        form_cotacao.save()
        form_cotacao = CsvModelForm()            
        obj = Csv.objects.get(activated=False)
        with open(obj.file_name.path, 'r') as f:
            reader = csv.reader(f)

            for i, row in enumerate(reader):
                if i==0:
                    pass
                else:
                    row = "".join(row)
                    row = row.replace(";"," ")
                    row = row.split()
                    acao = row[1].upper()
                    ativo = row[2].upper()

                    Cotacao.objects.create(
                        acao = acao,
                        ativo = ativo,
                        fechamento_ajustado = row[3],
                    )
            obj.activated = True
            obj.save()
                    
    return render(request,'upload/upload-cotacao.html',{'form_cotacao':form_cotacao})

# Create your views proventos
def upload_files_view_proventos(request):
    form_provento = CsvModelForm(request.POST or None, request.FILES or None)
    print(User.objects.values('username'))
        
    if form_provento.is_valid():              
        form_provento.save()
        form_provento = CsvModelForm()            
        obj = Csv.objects.get(activated=False)
        with open(obj.file_name.path, 'r') as f:
            reader = csv.reader(f)

            for i, row in enumerate(reader):
                if i==0:
                    pass
                else:
                    row = "".join(row)
                    row = row.replace(";"," ")
                    row = row.split()
                    ativo = row[1].upper()
                    tipo_provento = row[2].upper()

                    Proventos.objects.create(
                        ativo = ativo,
                        tipo_provento = tipo_provento,
                        data = row[3],
                        valor = row[4],
                        user = request.user,
                    )
            obj.activated = True
            obj.save()
                    
    return render(request,'upload/upload-provento.html',{'form_provento':form_provento})