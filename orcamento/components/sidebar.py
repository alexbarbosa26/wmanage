from dash import html, dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import ThemeSwitchAIO
from datetime import datetime, timedelta
from orcamento.models import Categoria

# ========= Layout ========= #
layout = dbc.Card([
    html.H2('MBManage', className='text-primary'),
    html.P('by wmanage', className='text-info'),
    ThemeSwitchAIO(aio_id="theme", themes=[dbc.themes.COSMO, dbc.themes.CYBORG]),
    html.Hr(),    
    # ========= Seção Nova =========== #    
    dbc.Nav([
        dbc.NavLink("Dashboard", href="/dashboards", active='exact'),
        dbc.NavLink("Extrato", href="/extrato", active="exact"),
    ], vertical=True, pills=True, id='nav_buttons', style={'margin-bottom': '0px'}),
        # ========= Seção Nova =========== #
    html.Hr(),
    dbc.Row([
        dbc.Col([
            html.Label('Categoria das receitas', style={'margin-top': '10px'}),
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
            html.Label('Categoria das despesas'),
            dcc.Dropdown(
                id='dropdown-despesa',
                clearable=False,
                style={'width': '100%'},
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
], id='sidebar_completa', style={'margin-top': '10px'})


def register_callback_sidebar(app):
    # pop-up receita
    @app.callback(
        Output('modal-novo-receita', 'is_open'),
        Input('open-novo-receita', 'n_clicks'),
        State('modal-novo-receita', 'is_open')
    )
    def toggle_modal(n1, is_open):
        if n1:
            return not is_open

    # pop-up despesa
    @app.callback(
        Output('modal-novo-despesa', 'is_open'),
        Input('open-novo-despesa', 'n_clicks'),
        State('modal-novo-despesa', 'is_open')
    )
    def toggle_modal(n1, is_open):
        if n1:
            return not is_open

    # Salvar categoria da receita

    @app.callback(
        Output('id_teste_receita', 'children'),
        Input('add-categoria-receita', 'n_clicks'),
        State('input-add-receita', 'value'),
        State('user-id', 'value')
    )
    def save_categoria_receita(n_clicks, categoria, user_id):
        if n_clicks:
            print(user_id)
            categoria = Categoria(nome=categoria, tipo='1')
            categoria.save()
            opt_receita = [{"label": i, "value": i}
                           for i in Categoria.objects.filter(tipo='1')]
            return f"A categoria {categoria} foi salva!"
