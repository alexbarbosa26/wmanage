from dash import dcc, html
import dash_bootstrap_components as dbc
from django_plotly_dash import DjangoDash
from dash.dependencies import Input, Output
from .components import sidebar, dashboards, extratos
from .components.sidebar import register_callback_sidebar

app = DjangoDash('SimpleExample', external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME, '/static/style/styles.css'])

content = html.Div(id="page-content")

app.layout = dbc.Container(children=[
    dbc.Row([
        dbc.Col([
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
    if pathname=='/dashboard/':
        return dashboards.layout
    
    if pathname=='/extrato/':
        return extratos.layout
    
    return dashboards.layout

register_callback_sidebar(app)