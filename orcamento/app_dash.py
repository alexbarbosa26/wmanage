# views.py

from django_plotly_dash import DjangoDash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import ThemeSwitchAIO

app = DjangoDash('my_dash_app', external_stylesheets=[dbc.themes.COSMO])

app.layout = html.Div(    
    className="container",
    children=[
        ThemeSwitchAIO(aio_id="theme", themes=[dbc.themes.BOOTSTRAP, dbc.themes.DARKLY]),
        html.H1("Meu Aplicativo Dash"),
        html.Div(
            className="row",
            children=[
                html.Div(
                    className="col-md-6",
                    children=[
                        dcc.Graph(
                            figure={
                                'data': [
                                    {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
                                    {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': u'Montréal'},
                                ],
                                'layout': {
                                    'title': 'Gráfico de Barras'
                                }
                            }
                        )
                    ]
                ),
                html.Div(
                    className="col-md-6",
                    children=[
                        dcc.Graph(
                            figure={
                                'data': [
                                    {'x': [1, 2, 3], 'y': [1, 4, 1], 'type': 'line', 'name': 'SF'},
                                    {'x': [1, 2, 3], 'y': [2, 2, 3], 'type': 'line', 'name': u'Montréal'},
                                ],
                                'layout': {
                                    'title': 'Gráfico de Linhas'
                                }
                            }
                        )
                    ]
                )
            ]
        )
    ]
)
