from dash import html, dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import ThemeSwitchAIO
from datetime import datetime, timedelta
from orcamento.models import Categoria, Subcategoria

card_style_light = {"height": "100vh", "margin": "0px",'margin-top': '10px', "padding": "10px"}
card_style_dark = {'padding-left': '10px', 'padding-top': '10px', "backgroundColor": "rgb(48 48 48)", "color": "#FFFFFF"}

# ========= Layout ========= #
layout = dbc.Card([
    html.H2('MBManage', className='text-primary'),
    html.P('by wmanage', className='text-info'),
    ThemeSwitchAIO(aio_id="theme", themes=[dbc.themes.COSMO, dbc.themes.CYBORG]),
    html.Hr(),    
    # ========= Seção Nova =========== #    
    dbc.Nav([
        dbc.NavLink("Dashboard", href="/dashboards/", active=True),
    ], vertical=True, pills=True, id='nav_buttons', style={'margin-bottom': '0px'}),
        # ========= Seção Nova =========== #
    html.Hr(),
    dbc.Row([
        dbc.Col([
            html.Label('Categorias', style={'margin-top': '0px'}),
            html.Div(
                dcc.Dropdown(
                    id='dropdown-categoria',
                    clearable=False,
                    style={'with': '100%', "font-size":'10pt'},
                    persistence=True,
                    persistence_type='session',
                    multi=True
                )
            ),
            html.Label('Subcategorias', style={"margin-top":"10px"}),
            dcc.Dropdown(
                id='dropdown-subcategoria',
                clearable=False,
                style={'width': '100%', 'font-size':'9pt'},
                persistence=True,
                persistence_type='session',
                multi=True),
            html.Label('Período de Análise',style={'margin-top': '10px'}),
            dcc.DatePickerRange(
                id='date-picker-config',
                month_format='Do MMM, YY',
                end_date_placeholder_text='Data...',
                start_date=datetime(2023, 1, 1),
                end_date=datetime.today() + timedelta(days=31),
                updatemode='singledate',
                style={'z-index': '100'},
                display_format='DD/MM/YYYY'
            ),
        ]),
    ]),
], id='sidebar_completa', style={"height": "100vh", "margin": "0px",'margin-top': '10px', "padding": "10px"})


def register_callback_sidebar(app):
    @app.callback(
        Output("sidebar_completa", "style"),
        Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
    )
    def update_card_style_theme(toggle):
        if toggle:
            return card_style_light
        else:
            return card_style_dark
        
    # Callback para preencher o dropdown de categorias e subcategorias
    @app.callback(
        [Output('dropdown-categoria', 'options'),
         Output('dropdown-subcategoria', 'options')],
        [Input('date-picker-config', 'start_date'),
         Input('date-picker-config', 'end_date'),
         Input('dropdown-categoria', 'value'),
         Input('dropdown-subcategoria', 'value'),]
    )
    def update_dropdowns(start_date, end_date, categoria_select, subcategoria_select):        

        if categoria_select:
            subcategorias = Subcategoria.objects.filter(categoria_id__in=categoria_select)
        else:            
            subcategorias = Subcategoria.objects.all()

        if subcategoria_select:
            categorias = Categoria.objects.filter(subcategoria__in=subcategoria_select)
        else:
            categorias = Categoria.objects.all()            

        options_categoria = [{'label': cat.nome, 'value': cat.id} for cat in categorias]
        options_subcategoria = [{'label': subcat.nome, 'value': subcat.id} for subcat in subcategorias]
        
        return options_categoria, options_subcategoria

