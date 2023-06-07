import locale
from dash import html, dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objs as go
from dash_bootstrap_templates import ThemeSwitchAIO

from orcamento.models import Categoria, Lancamento, Subcategoria

card_icon = {
    'color': 'white',
    'textAlign': 'center',
    'fontSize': 30,
    'margin': 'auto',
}

df = px.data.stocks()
# =========  Layout  =========== #
layout = dbc.Col([
    dbc.Row([
        dbc.Col([
            dbc.CardGroup([
                dbc.Card([
                    html.Legend('Saldo'),
                    html.H5('R$ 5.000,00', id='p-saldo-dahsboard', style={})
                ], style={'padding-left': '10px', 'padding-top': '10px'}),
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
                    html.H5('R$ 5.000,00', id='p-receita-dahsboard', style={})
                ], style={'padding-left': '10px', 'padding-top': '10px'}),
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
                    html.H5('R$ 5.000,00', id='p-despesa-dahsboard', style={})
                ], style={'padding-left': '10px', 'padding-top': '10px'}),
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
            dbc.Card(dcc.Graph(id='chart1'), style={'height': '100%', 'padding': '10px'}), width=12
        )
    ], style={'margin': '10px'}),
    dbc.Row([
        dbc.Col(dbc.Card(dcc.Graph(id='chart2'),
                style={'padding': '10px'}), width=6),
        dbc.Col(dbc.Card(dcc.Graph(id='chart3'),
                style={'padding': '10px'}), width=6),
    ], style={'margin': '10px'})
])

# =========  Callbacks  =========== #


def register_callback_dashboard(app):
    @app.callback(
        Output("chart1", "figure"),
        Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
    )
    def update_graph1_theme(toggle):
        template = "bootstrap" if toggle else "darkly"
        # Obtenha os dados para o gráfico a partir do seu modelo
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
            text=[locale.currency(valor, grouping=True) for valor in receitas],  # Formatar como moeda
            textposition='auto'  # Exibir rótulo do dado
        )
        trace2 = go.Bar(
            x=[categoria.nome for categoria in categorias if categoria.tipo == '2'],
            y=despesas,
            name='Despesas',
            text=[locale.currency(valor, grouping=True) for valor in despesas],  # Formatar como moeda
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
        Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
    )
    def update_graph2_theme(toggle):
        template = "bootstrap" if toggle else "darkly"
        
        # Obtenha os dados para o gráfico a partir do seu modelo
        subcategorias = Subcategoria.objects.filter(lancamento__isnull=False).distinct()
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
            text=[locale.currency(item[1], grouping=True) for item in despesas],  # Formatar como moeda
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
        Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
    )
    def update_graph3_theme(toggle):
        template = "bootstrap" if toggle else "darkly"
        # Obtenha os dados para o gráfico a partir do seu modelo
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
            name='Receitas'
        )
        trace2 = go.Bar(
            x=[categoria.nome for categoria in categorias if categoria.tipo == '2'],
            y=despesas,
            name='Despesas'
        )

        data = [trace1, trace2]
        layout = go.Layout(
            template=template,
            barmode='group',
            title='Relação de Receitas e Despesas por Categoria'
        )

        fig = go.Figure(data=data, layout=layout)
        return fig
