from dash import html, dcc
from dash.dependencies import Input, Output, State
from datetime import date, datetime, timedelta
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import calendar

card_icon = {
    'color': 'white',
    'textAlign': 'center',
    'fontSize': 30,
    'margin': 'auto',
}

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
        dbc.Col([
            dbc.Card([
                html.Legend('Filtrar lançamentos', className='card-title'),
                html.Label('Categoria das receitas',
                           style={'margin-top': '10px'}),
                html.Div(
                    dcc.Dropdown(
                        id='dropdown-receita',
                        clearable=False,
                        style={'with': '100%'},
                        persistence=True,
                        persistence_type='session',
                        multi=True
                    )
                ),
                html.Label('Categoria das despesas',
                           style={'margin-top': '10px'}),
                    dcc.Dropdown(
                        id='dropdown-despesa',
                        clearable=False,
                        style={'width': '100%'},
                        persistence=True,
                        persistence_type='session',
                        multi=True),
                html.Legend('Período de Análise',
                            style={'margin-top':'10px'}),
                    dcc.DatePickerRange(
                        id='date-picker-config',
                        month_format='Do MMM, YY',
                        end_date_placeholder_text='Data...',
                        start_date=datetime(2023,1,1),
                        end_date=datetime.today() + timedelta(days=31),
                        updatemode='singledate',
                        style={'z-index': '100'},
                        display_format='DD/MM/YYYY' 
                    ),
            ], style={'height':'100%', 'padding':'25px'})
        ], width=4),
        dbc.Col(
            dbc.Card(dcc.Graph(id='chart1'), style={'height':'100%', 'padding':'10px'}), width=8
        )
    ], style={'margin':'10px'}),
    dbc.Row([
        dbc.Col(dbc.Card(dcc.Graph(id='chart2'), style={'padding':'10px'}), width=6),
        dbc.Col(dbc.Card(dcc.Graph(id='chart3'), style={'padding':'10px'}), width=3),
        dbc.Col(dbc.Card(dcc.Graph(id='chart4'), style={'padding':'10px'}), width=3)
    ], style={'margin':'10px'})
])

# =========  Callbacks  =========== #
