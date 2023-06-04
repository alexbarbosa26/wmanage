import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from django.db.models import Sum
from django_plotly_dash import DjangoDash
from gestao_orcamento.models import Categoria, Despesas, Ganhos
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go

from .components import sidebar, dashboards, extratos
from .components.sidebar import register_callback_sidebar

app = DjangoDash('SimpleExample', external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME, '/static/style/styles.css'])

content = html.Div(id="page-content")

app.layout = dbc.Container(children=[
    dbc.Row([
        dbc.Col([
            # Componente oculto para armazenar o ID do usuário
            dcc.Input(id='user-id', type='hidden', value=''),
            dcc.Location(id='url'),
            sidebar.layout
        ], md=2),
        dbc.Col([
            content
        ],md=10)
    ])
], fluid=True,)

# =========  Callbacks  =========== #
@app.callback(Output('page-content','children'), [Input('url', 'pathname')])
def page_render(pathname):
    if pathname=='/dashboards':
        return dashboards.layout
    
    if pathname=='/extrato':
        return extratos.layout
    
    return dashboards.layout

# Callback para atualizar o ID do usuário
@app.callback(Output('user-id', 'value'), Input('user-id', 'value'))
def update_user_id(user_id):
    print(user_id)
    return user_id

register_callback_sidebar(app)