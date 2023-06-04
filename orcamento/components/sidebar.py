from dash import html, dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import ThemeChangerAIO
from datetime import date, timedelta
from django.contrib.auth.decorators import login_required
from django.contrib.auth.middleware import get_user

from gestao_orcamento.models import Categoria


# ========= Layout ========= #
layout = dbc.Card([
    html.H2('MBManage', className='text-primary'),
    html.P('by wmanage', className='text-info'),
    html.Hr(),

    # ========= Seção Nova =========== #
    dbc.Row([
        dbc.Col([
            dbc.Button(color='success', id='open-novo-receita',
                       children=['Receita'])
        ], width=6),
        dbc.Col([
            dbc.Button(color='danger', id='open-novo-despesa',
                       children=['Despesa'])
        ], width=6)
    ]),
    # ========= Modal Receita =========== #
    dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle('Adicionar receita')),
        dbc.ModalBody([
            dbc.Row([
                dbc.Col([
                    dbc.Label('Descrição: '),
                    dbc.Input(
                        placeholder='Ex: dividendos da bolsa, salario...', id='txt-receita')
                ], width=6),
                dbc.Col([
                    dbc.Label('Valor: '),
                    dbc.Input(placeholder='R$ 5.000,00',
                              id='valor_receita', value='')
                ], width=6)
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Label('Data: '),
                    dcc.DatePickerSingle(
                        id='data-receita',
                        min_date_allowed=date(2017, 1, 1),
                        max_date_allowed=date.today() + timedelta(1825),
                        date=date.today(),
                        style={'width': '100%'},
                        display_format='DD/MM/YYYY'
                    )
                ]),
                dbc.Col([
                    dbc.Label('Extras'),
                    dbc.Checklist(
                        options=[{'label': 'Foi recebido', 'value': 1},
                                 {'label': 'Receita Recorrente', 'value': 2}],
                        value=[1],
                        id='switches-input-receita',
                        switch=True,
                    )
                ], width=4),
                dbc.Col([
                    html.Label('Categorias da receita'),
                    dbc.Select(
                        id='select_receita',
                        options=[{'label':cat.nome, 'value':cat.id} for cat in Categoria.objects.filter(tipo='1')] ,
                        value=None
                    ) 

                ], width=4)
            ], style={'margin-top': '10px'}),
            dbc.Row([
                dbc.Accordion([
                    dbc.AccordionItem(children=[
                        dbc.Row([
                            dbc.Col([
                                html.Legend('Adicionar categoria',
                                            style={'color': 'green'}),
                                dbc.Input(placeholder='Nova categoria',
                                          id='input-add-receita', value=''),
                                html.Br(),
                                html.Button('Adicionar', className='btn btn-success',
                                            id='add-categoria-receita', style={'margin-top': '10px'}),
                                html.Br(),
                                html.Div(
                                    id='categoria-div-add-receita', style={}),
                            ], width=6),
                            dbc.Col([
                                html.Legend('Excluir categorias',
                                            style={'color': 'red'}),
                                dbc.Checklist(
                                    id='checklist-selected-style-receita',
                                    options=[],
                                    value=[],
                                    label_checked_style={'color': 'red'},
                                    input_checked_style={
                                        'backgroundColor': 'blue', 'borderColor': 'orange'}
                                ),
                                dbc.Button(
                                    'Remover', color='warning', id='remove-categoria-receita', style={'margin-top': '10px'})
                            ], width=6)
                        ])
                    ], title='Adicionar/Remover Categorias')
                ], flush=True, start_collapsed=True, id='accordion-receita'),

                html.Div(id='id_teste_receita', style={'padding-top': '20px'}),
                dbc.ModalFooter([
                    dbc.Button('Adicionar Receita',
                               id='salvar_receita', color='success'),
                    dbc.Popover(dbc.PopoverBody(
                        'Receita Salva'), target='salvar_receita', placement='left', trigger='click')
                ])
            ], style={'margin-top': '25px'})
        ])
    ], style={'backgroung-color': 'rgba(17, 140, 79, 0.05)'},
        id='modal-novo-receita',
        size='lg',
        is_open=False,
        centered=False,
        backdrop=True),
    # ========= Modal Despesa =========== #
    dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle('Adicionar despesa')),
        dbc.ModalBody([
            dbc.Row([
                dbc.Col([
                    dbc.Label('Descrição: '),
                    dbc.Input(
                        placeholder='Ex: Mercado, padaria, gasolina...', id='txt-despesa')
                ], width=6),
                dbc.Col([
                    dbc.Label('Valor: '),
                    dbc.Input(placeholder='R$ 5.000,00',
                              id='valor_despesa', value='')
                ], width=6)
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Label('Data: '),
                    dcc.DatePickerSingle(
                        id='data-despesa',
                        min_date_allowed=date(2017, 1, 1),
                        max_date_allowed=date.today() + timedelta(1825),
                        date=date.today(),
                        style={'width': '100%'},
                        display_format='DD/MM/YYYY'
                    )
                ]),
                dbc.Col([
                    dbc.Label('Extras'),
                    dbc.Checklist(
                        options=[{'label': 'Foi recebido', 'value': 1},
                                 {'label': 'Despesa Recorrente', 'value': 2}],
                        value=[1],
                        id='switches-input-despesa',
                        switch=True,
                    )
                ], width=4),
                dbc.Col([
                    html.Label('Categorias da despesa'),
                    dbc.Select(id='select_despesa', options=[], value=[])

                ], width=4)
            ], style={'margin-top': '10px'}),
            dbc.Row([
                dbc.Accordion([
                    dbc.AccordionItem(children=[
                        dbc.Row([
                            dbc.Col([
                                html.Legend('Adicionar categoria',
                                            style={'color': 'green'}),
                                dbc.Input(placeholder='Nova categoria',
                                          id='input-add-despesa', value=''),
                                html.Br(),
                                html.Button('Adicionar', className='btn btn-success',
                                            id='add-categoria-despesa', style={'margin-top': '10px'}),
                                html.Br(),
                                html.Div(
                                    id='categoria-div-add-despesa', style={}),
                            ], width=6),
                            dbc.Col([
                                html.Legend('Excluir categorias',
                                            style={'color': 'red'}),
                                dbc.Checklist(
                                    id='checklist-selected-style-despesa',
                                    options=[],
                                    value=[],
                                    label_checked_style={'color': 'red'},
                                    input_checked_style={"backgroundColor": "#fa7268","borderColor": "#ea6258"},
                                ),
                                dbc.Button(
                                    'Remover', color='warning', id='remove-categoria-receita', style={'margin-top': '10px'})
                            ], width=6)
                        ])
                    ], title='Adicionar/Remover Categorias')
                ], flush=True, start_collapsed=True, id='accordion-despesa'),

                html.Div(id='id_teste_despesa', style={'padding-top': '20px'}),
                dbc.ModalFooter([
                    dbc.Button('Adicionar Despesa',
                               id='salvar_despesa', color='success'),
                    dbc.Popover(dbc.PopoverBody(
                        'Despesa Salva'), target='salvar_despesa', placement='left', trigger='click')
                ])
            ], style={'margin-top': '25px'})
        ])
    ], style={'backgroung-color': 'rgba(17, 140, 79, 0.05)'},
        id='modal-novo-despesa',
        size='lg',
        is_open=False,
        centered=False,
        backdrop=True),
    # ========= Seção Nova =========== #
    html.Hr(),
    dbc.Nav([
        dbc.NavLink("Dashboard", href="/dashboards", active='exact'),
        dbc.NavLink("Extrato", href="/extrato", active="exact"),
    ], vertical=True, pills=True, id='nav_buttons', style={'margin-bottom': '50px'}),
    ThemeChangerAIO(aio_id="theme", radio_props={"value": dbc.themes.DARKLY}),

], id='sidebar_completa', style={'margin-top': '10px'}

)


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
            opt_receita = [{"label": i, "value": i} for i in Categoria.objects.filter(tipo='1')]
            return f"A categoria {categoria} foi salva!"
