import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from django_plotly_dash import DjangoDash
from dash.dependencies import Input, Output

from orcamento.models import Lancamento
from .components import sidebar, dashboards
from .components.sidebar import register_callback_sidebar
from .components.dashboards import register_callback_dashboard

app = DjangoDash('SimpleExample', external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME, '/static/style/styles.css'])

content = html.Div(id="page-content")

app.layout = dbc.Container(children=[
    html.Div(id="output-one"),
    dbc.Row([
        dbc.Col([
            dcc.Location(id='url'),
            sidebar.layout
        ], md=2),
        dbc.Col([
            content
        ],md=10)
    ])
], fluid=True, className="dbc")

@app.callback(Output('page-content','children'), [Input('url', 'pathname')])
def page_render(pathname):
    if pathname=='/dashboard/':
        return dashboards.layout
    
    if pathname=='/extratos/':
        return extratos.layout
    
    return dashboards.layout

register_callback_sidebar(app)
register_callback_dashboard(app)




