from django.http import HttpResponse
from django.views import View
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from .models import Nota


def render_to_pdf(request):
    notas = Nota.objects.all().filter(user=request.user)
    notas_data = []

    for nota in notas:
        notas_data.append([
            nota.ativo,
            nota.quantidade,
            nota.preco,
            nota.data.strftime("%d/%m/%Y"),
            nota.tipo,
            nota.total_compra,
            nota.identificador,
            nota.corretagem,
            nota.emolumentos,
            nota.tx_liquida_CBLC,
            nota.IRRF_Final,
            nota.Lucro_Day_Trade,
            nota.IRRF_Day_Trade,
            nota.total_custo,
            nota.corretora,
            nota.data_instante.strftime("%d/%m/%Y %H:%M:%S")
        ])

    doc = SimpleDocTemplate("notas.pdf", pagesize=landscape(letter))
    elements = []

    style = getSampleStyleSheet()
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), style['Background']),
        ('TEXTCOLOR', (0, 0), (-1, 0), style['TextColor']),
        ('FONTNAME', (0, 0), (-1, 0), style['FontName']),
        ('FONTSIZE', (0, 0), (-1, 0), style['FontSize']),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), style['AlternateBackground']),
        ('TEXTCOLOR', (0, 1), (-1, -1), style['TextColor']),
        ('FONTNAME', (0, 1), (-1, -1), style['FontName']),
        ('FONTSIZE', (0, 1), (-1, -1), style['FontSize']),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, style['GridColor']),
        ('BOX', (0, 0), (-1, -1), 0.25, style['GridColor'])
    ])

    notas_table = Table([
        ['Ativo', 'Quantidade', 'Preço', 'Data', 'Tipo', 'Total Compra', 'Identificador',
            'Corretagem', 'Emolumentos', 'Taxa Líquida CBLC', 'IRRF Final', 'Lucro Day Trade',
            'IRRF Day Trade', 'Total Custo', 'Corretora', 'Data/Hora'],
        *notas_data
    ])
    notas_table.setStyle(table_style)
    elements.append(notas_table)

    doc.build(elements)
    with open("notas.pdf", 'rb') as file:
        response = HttpResponse(file.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="notas.pdf"'
        return response


def render_to_excel(request):
        notas = Nota.objects.all().filter(user=request.user)
        notas_data = []

        for nota in notas:
            notas_data.append({
                'ativo': nota.ativo,
                'quantidade': nota.quantidade,
                'preco': nota.preco,
                'data': nota.data,
                'tipo': nota.tipo,
                'total_compra': nota.total_compra,
                'identificador': nota.identificador,
                'corretagem': nota.corretagem,
                'emolumentos': nota.emolumentos,
                'tx_liquida_CBLC': nota.tx_liquida_CBLC,
                'IRRF_Final': nota.IRRF_Final,
                'Lucro_Day_Trade': nota.Lucro_Day_Trade,
                'IRRF_Day_Trade': nota.IRRF_Day_Trade,
                'total_custo': nota.total_custo,
                'corretora': nota.corretora,
                'data_instante': nota.data_instante
            })

        df = pd.DataFrame(notas_data)
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="notas.xlsx"'
        df.to_excel(response, index=False)

        return response