import calendar
import locale
from dash import html, dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objs as go
from dash_bootstrap_templates import ThemeSwitchAIO
from django.db.models import Q

from orcamento.models import Categoria, Lancamento, Subcategoria

card_icon = {
    'color': 'white',
    'textAlign': 'center',
    'fontSize': 30,
    'margin': 'auto',
}

card_style_light = {'padding-left': '10px', 'padding-top': '10px'}
card_style_dark = {'padding-left': '10px', 'padding-top': '10px',
                   "backgroundColor": "rgb(48 48 48)", "color": "#FFFFFF"}


df = px.data.stocks()
# =========  Layout  =========== #
layout = dbc.Col([
    dbc.Row([
        dbc.Col([
            dbc.CardGroup([
                dbc.Card([
                    html.Legend('Saldo'),
                    html.H5('-', id='p-saldo-dahsboard', style={})
                ], id='card-saldo', style={'padding-left': '10px', 'padding-top': '10px'}),
                dbc.Card(
                    html.Div(className='fa fa-university', style=card_icon),
                    color='primary',
                    style={'maxWidth': 75, 'height': 100,
                           'margin-left': '-10px'},
                )
            ])
        ], width=4),
        dbc.Col([
            dbc.CardGroup([
                dbc.Card([
                    html.Legend('Receita'),
                    html.H5('-', id='p-receita-dahsboard', style={})
                ], id='card-receita', style={'padding-left': '10px', 'padding-top': '10px'}),
                dbc.Card(
                    html.Div(
                        className='fa-solid fa-hand-holding-dollar', style=card_icon),
                    color='success',
                    style={'maxWidth': 75, 'height': 100,
                           'margin-left': '-10px'},
                )
            ])
        ], width=4),
        dbc.Col([
            dbc.CardGroup([
                dbc.Card([
                    html.Legend('Despesa'),
                    html.H5('-', id='p-despesa-dahsboard', style={})
                ], id='card-despesa', style={'padding-left': '10px', 'padding-top': '10px'}),
                dbc.Card(
                    html.Div(className='fa-solid fa-sack-xmark',
                             style=card_icon),
                    color='danger',
                    style={'maxWidth': 75, 'height': 100,
                           'margin-left': '-10px'},
                )
            ])
        ], width=4)
    ], style={'margin': '10px'}),
    dbc.Row([
        dbc.Col(
            dbc.Card(dcc.Graph(id='chart1'), id='card-chart1', style={'height': '100%', 'padding': '10px'}), width=12
        )
    ], style={'margin': '10px'}),
    dbc.Row([
        dbc.Col(dbc.Card(dcc.Graph(id='chart2'), id='card-chart2',
                style={'padding': '10px'}), width=6),
        dbc.Col(dbc.Card(dcc.Graph(id='chart3'), id='card-chart3',
                style={'padding': '10px'}), width=6),
    ], style={'margin': '10px'})
])

# =========  Callbacks  =========== #


def register_callback_dashboard(app):
    @app.callback(
        Output("chart1", "figure"),
        [
            Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
            Input('dropdown-categoria', 'value'),
            Input('dropdown-subcategoria', 'value'),
        ],
    )
    def update_graph1_theme(toggle, categoria_select, subcategoria_select):
        template = "bootstrap" if toggle else "darkly"
        # Obtenha os dados para o gráfico a partir do seu modelo
        if categoria_select or subcategoria_select:
            categorias = Categoria.objects.filter(Q(id__in=categoria_select) | Q(subcategoria__in=subcategoria_select),
                lancamento__isnull=False).distinct()
        else:
            categorias = Categoria.objects.filter(
                lancamento__isnull=False).distinct()
        receitas = []
        despesas = []

        for categoria in categorias:
            lancamentos = Lancamento.objects.filter(categoria=categoria)
            total = sum(lancamento.valor for lancamento in lancamentos)

            if categoria.tipo == '1':
                receitas.append(total)
            elif categoria.tipo == '2':
                despesas.append(total)

        # Crie o gráfico de barras
        trace1 = go.Bar(
            x=[categoria.nome for categoria in categorias if categoria.tipo == '1'],
            y=receitas,
            name='Receitas',
            text=[locale.currency(valor, grouping=True)
                  for valor in receitas],  # Formatar como moeda
            textposition='auto'  # Exibir rótulo do dado
        )
        trace2 = go.Bar(
            x=[categoria.nome for categoria in categorias if categoria.tipo == '2'],
            y=despesas,
            name='Despesas',
            text=[locale.currency(valor, grouping=True)
                  for valor in despesas],  # Formatar como moeda
            textposition='auto'  # Exibir rótulo do dado
        )

        data = [trace1, trace2]
        layout = go.Layout(
            template=template,
            barmode='group',
            title='Relação de Receitas e Despesas por Categoria'
        )

        fig = go.Figure(data=data, layout=layout)
        return fig

    @app.callback(
        Output("chart2", "figure"),
        [
            Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
            Input('dropdown-categoria', 'value'),
            Input('dropdown-subcategoria', 'value'),
        ],
    )
    def update_graph2_theme(toggle, categoria_select, subcategoria_select):
        template = "bootstrap" if toggle else "darkly"

        # Obtenha os dados para o gráfico a partir do seu modelo
        if categoria_select:
            subcategorias = Subcategoria.objects.filter( Q(categoria__in=categoria_select),
            lancamento__isnull=False).distinct()
        
        if subcategoria_select:
            subcategorias = Subcategoria.objects.filter(Q(id__in=subcategoria_select),
            lancamento__isnull=False).distinct()

        else:
            subcategorias = Subcategoria.objects.filter(
                lancamento__isnull=False).distinct()
        despesas = []

        for subcategoria in subcategorias:
            lancamentos = Lancamento.objects.filter(subcategoria=subcategoria)
            total = sum(lancamento.valor for lancamento in lancamentos)

            if subcategoria.categoria.tipo == '2':
                despesas.append((subcategoria.nome, total))

        # Ordenar a lista de despesas pelo valor total em ordem decrescente
        despesas = sorted(despesas, key=lambda x: x[1], reverse=False)

        # Crie o gráfico de barras
        trace = go.Bar(
            y=[item[0] for item in despesas],
            x=[item[1] for item in despesas],
            orientation='h',
            name='Despesas',
            text=[locale.currency(item[1], grouping=True)
                  for item in despesas],  # Formatar como moeda
        )

        data = [trace]
        layout = go.Layout(
            template=template,
            title='Relação de Despesas por Subcategoria'
        )

        fig = go.Figure(data=data, layout=layout)
        return fig

    @app.callback(
        Output("chart3", "figure"),
        [
            Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
            Input('dropdown-categoria', 'value'),
            Input('dropdown-subcategoria', 'value'),
        ],
    )
    def update_graph3_theme(toggle, categoria_select, subcategoria_select):
        template = "bootstrap" if toggle else "darkly"

        # Obtenha os dados para o gráfico a partir do seu modelo
        if categoria_select or subcategoria_select:
            lancamentos = Lancamento.objects.filter(Q(categoria__id__in=categoria_select) | Q(categoria__subcategoria__id__in=subcategoria_select),
            categoria__tipo='2') 
        else:
            lancamentos = Lancamento.objects.filter(
                categoria__tipo='2')  # Filtrar apenas as despesas
        # Dicionário para armazenar os gastos por mês
        gastos_por_mes = {month: 0 for month in range(1, 13)}

        for lancamento in lancamentos:
            mes = lancamento.data.month
            gastos_por_mes[mes] += lancamento.valor

        # Filtrar apenas os meses com valor
        meses_com_valor = [calendar.month_name[month]
                           for month, valor in gastos_por_mes.items() if valor > 0]
        gastos_com_valor = [
            valor for valor in gastos_por_mes.values() if valor > 0]

        # Criar o gráfico de barras
        trace = go.Bar(
            x=meses_com_valor,
            y=gastos_com_valor,
            name='Gastos',
            text=[locale.currency(valor, grouping=True)
                  for valor in gastos_com_valor],  # Formatar como moeda
            textposition='auto'  # Exibir rótulo do dado
        )

        data = [trace]
        layout = go.Layout(
            template=template,
            title='Total de Gastos por Mês do Ano',
            xaxis=dict(title='Mês'),
            yaxis=dict(title='Valor')
        )

        fig = go.Figure(data=data, layout=layout)
        return fig

    def calculate_total_receitas():
        receitas = Lancamento.objects.filter(
            categoria__tipo='1')  # Filtrar apenas as receitas
        total_receitas = sum(lancamento.valor for lancamento in receitas)
        return total_receitas

    def calculate_total_despesas():
        despesas = Lancamento.objects.filter(
            categoria__tipo='2')  # Filtrar apenas as despesas
        total_despesas = sum(lancamento.valor for lancamento in despesas)
        return total_despesas

    def calculate_total_saldo():
        total_saldo = calculate_total_receitas() - calculate_total_despesas()
        return total_saldo

    @app.callback(
        Output("p-saldo-dahsboard", "children"),
        Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
    )
    def update_receita_theme(toggle):
        template = "bootstrap" if toggle else "darkly"
        total_saldo = calculate_total_saldo()
        saldo_formatted = locale.currency(total_saldo, grouping=True)
        return saldo_formatted

    @app.callback(
        Output("p-receita-dahsboard", "children"),
        Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
    )
    def update_despesa_theme(toggle):
        template = "bootstrap" if toggle else "darkly"
        total_receitas = calculate_total_receitas()
        saldo_formatted = locale.currency(total_receitas, grouping=True)
        return saldo_formatted

    @app.callback(
        Output("p-despesa-dahsboard", "children"),
        Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
    )
    def update_saldo_theme(toggle):
        template = "bootstrap" if toggle else "darkly"
        total_despesas = calculate_total_despesas()
        saldo_formatted = locale.currency(total_despesas, grouping=True)
        return saldo_formatted

    @app.callback(
        Output("card-saldo", "style"),
        Output("card-receita", "style"),
        Output("card-despesa", "style"),
        Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
    )
    def update_card_style_theme(toggle):
        if toggle:
            return card_style_light, card_style_light, card_style_light
        else:
            return card_style_dark, card_style_dark, card_style_dark

    @app.callback(
        Output("card-chart1", "style"),
        Output("card-chart2", "style"),
        Output("card-chart3", "style"),
        Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
    )
    def update_card_chart_style_theme(toggle):
        if toggle:
            return card_style_light, card_style_light, card_style_light
        else:
            return card_style_dark, card_style_dark, card_style_dark
