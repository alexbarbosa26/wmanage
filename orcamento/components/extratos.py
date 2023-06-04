from dash import html, dcc
from dash.dependencies import Input, Output, State
from datetime import date, datetime, timedelta
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import calendar



# =========  Layout  =========== #
layout = dbc.Col([
    dbc.Row([
        html.Legend('Tabela de desapesas'),
        html.Div(id='tabela-despesas',className='dbc')
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='bar-chart', style={'margin-right':'20px'})
        ], width=9),
        dbc.Col([
            dbc.Card(
                dbc.CardBody([
                    html.H4('Despesas'),
                    html.Legend('R$ 5.000,00', id='valor_despes_card', style={'font-size':'60px'}),
                    html.H6('Total Despesas'),

                ], style={'text-align':'center', 'padding-top':'30px'})
            )
        ], width=3)
    ])
], style={'padding':'10px'})



# =========  Callbacks  =========== #
