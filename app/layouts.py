from dash import html, dcc
import dash_bootstrap_components as dbc
from dash_bootstrap_components import themes, Row, Col
from pandas import DataFrame


from components import *


# Arrange the layout by including the data_store component


def app_layout ( params : dict, data_store : dcc.Store ) -> html.Div :
    return html . Div ( [
        data_store, 
        solar_modal_layout(),
        people_modal_layout(),
        generic_modal_layout(),
        recent_sales_modal_layout(),
        # sidebar
        dbc. Container(
            children = [
                html.Div(
                    id="page-display",
                    style={"border": "1px solid lightgray",
                           "width": "98%", "height": "98vh",
                           "margin": "auto"},
                    children=[
                        pageNavbar(params),
                        pageSidebar(params),
                        pageContent(params),
                        pageFooter(),
                    ],
                ),
            ],
            fluid=True,
        ),
    ])


def solar_modal_layout():
    import json
    from textwrap import dedent as d
    
    styles = {
        "image":{
            "width": "30%", 
            "height":"30%",
            "display": "inline-block",
            "verticalAlign": "top"
        },
        "pre":{
            "width": "30%", 
            "height":"30%",
            "display": "inline-block",
            "align":"left",
            "border": "thin lightgrey solid", 
            "overflowX": "scroll",
        }
    }
    
    return html.Div(
        [
            dbc.Modal(
                [
                    dbc.ModalHeader(
                        html.Div([
                            dbc.ModalTitle(id = 'solar_modal-header',children = "HEADER"),
                            html.Br(),
                            html.H6(id = 'solar_modal-header2',children = "SUB HEADER"),
                        ])
                    ),
                    dbc.ModalBody(
                        html.Div(
                            [
                                html.Pre(id="solar_modal-body", style=styles['pre']),
                                html.Img(id='solar_modal-image-1',src=None,className="zoom",style=styles['image']),
                                html.Img(id='solar_modal-image-2',src=None, style=styles['image']),
                                html.Div('',id='solar_modal-production'),
                            ],
                            style={"display": "inline-block"}
                        ) 
                    ),
                ],
                  id="solar_modal",
                  is_open=False, 
                  size="xl",  # "sm", "lg", "xl"
                  backdrop=True,  # backdrop close
                  scrollable=True,  # Scrollable
                  centered=True,  # Vertically center modal 
                  keyboard=True,  # Close modal when escape is pressed
                  fade=True,  # Let the modal fade instead of appear.
            ),
        ]
    )


def people_modal_layout():

    return html.Div([

        dbc.Modal(children = [
            dbc.ModalBody(
                dbc.Container(
                    [
                        #dbc.Row([html.Div("",id='people-modal-header')]),
            html.Center(),
                        dbc.Row(
                            html.Center(
                                children = [
                                    html.H5(
                                        dcc . Markdown (
                                            "",
                                            id = 'people-modal-header'
                                        )
                                        ,id='people-modal-header-h4'
                                    ),
                                    html . Div (
                                        '',
                                        id = 'people-modal-table',
                                        style={'width':'80%',
                                               'display':'none'}
                                    ),
                                ]
                            ),
                        ),
                    ],
                    fluid = True,
                    className = "dbc",
                )
            ),
        ],
                  id="people_modal",
                  is_open=False, 
                  size="xl",  # "sm", "lg", "xl"
                  backdrop=True,  # backdrop close
                  scrollable=True,  # Scrollable
                  centered=True,  # Vertically center modal 
                  keyboard=True,  # Close modal when escape is pressed
                  fade=True,  # Let the modal fade instead of appear.
        ),
    ]) ##end Div


def generic_modal_layout():
    styles = {
        "image":{
            "width": "100%", 
            "height":"100%",
            "display": "inline-block",
            "vertical-align": "top"
        },
        "pre":{
            "width": "30%", 
            "height":"30%",
            "display": "inline-block",
            "align":"left",
            "border": "thin lightgrey solid", 
            "overflowX": "scroll"
        }
    }
    tables      =  dbc.Card('',id = 'generic-modal-table',   body=True)

    charts = dbc.Card(id='generic-modal-chart-card', children=[
        html.Div([
            html.H6(
                dcc . Markdown (
                    '', id = 'generic-modal-chart-title-contents')
                ,id='generic-modal-chart-title-header'),
            dcc.Graph(id='generic-modal-chart',
                       figure={},
                       config={'displayModeBar': False},
                       style={'width': '100%', #'height': '50vh',
                              'display': 'none'},
            ),
            ]
        )
    ],body=True)

    images = dbc.Card(id = 'generic-modal-image-card', children=[
        html.Div([
            html.Img(src='',id='generic-modal-image',
                     style={'width': '60%', #'height': '50vh',
                            'display': 'none'}),
            html.Img(src='',id='generic-modal-sketch',
                     style={'width': '40%', #'height': '50vh',
                            'display': 'none'})
        ])
    ],body=True)
 
    return html.Div([
            dbc.Modal(children = [
                dbc.ModalHeader(
                    Row([
                        Col(
                            html.Div(
                                ["ADDRESS"],
                                id='generic-modal-address',
                                style={'fontSize':'20px'}
                            )
                        ),
                        Col(children=[
                            dcc.Dropdown (
                                options = [],
                                value = 0,
                                id='generic-modal-selected-units',
                                clearable=False,
                                style={
                                    'width':'70px',
                                    'float':'left',
                                    "borderColor"  : "white",
                                    #"fontSize"     : "20px",
                                    "verticalAlign":"top",
                                }
                            ),
                        ],
                            id='generic-modal-units-container-style',
                            style={'display':'none','width':'200px'}
                        ),
                        #Col(
                        #    html.Div(
                        #        ["OWNER"],
                        #        id='generic-modal-owner',
                        #        style={'fontSize':'20px'}
                        #    )
                        #),
                    ])  #end row
                ),
                dbc.ModalBody(
                    dbc.Container(
                        [
                            dbc.Row('',id='generic-modal-subheader'),
                            dbc.Row(
                                [
                                    dbc.Col([
                                        dbc.Row(
                                            html.Div(
                                                [''],
                                                id='generic-modal-col1-row1',
                                                style={
                                                    "border": "1px solid lightgray",
                                                    "margin": "auto"
                                                },
                                            )
                                        ),
                                        dbc.Row([
                                            html.Div([
                                                html.Img(
                                                    id='generic-modal-col1-row2-image',
                                                    src=None,
                                                    className="zoom",
                                                    style=styles['image']
                                                )
                                            ],
                                            id='generic-modal-col1-row2'),
                                        ])],
                                        id='generic-modal-col1',
                                        width = 4),
                                    dbc.Col([
                                        dbc.Row('',
                                                id='generic-modal-col2-row1'),
                                    ],
                                            id='generic-modal-col2',
                                            width = 8),
                                ]
                            ),
                        ],
                        fluid = True,
                        className = "dbc",
                    )
                ),
            ],
                      id="generic-modal",
                      is_open=False, 
                      size="xl",  # "sm", "lg", "xl"
                      backdrop=True,  # backdrop close
                      scrollable=True,  # Scrollable
                      centered=True,  # Vertically center modal 
                      keyboard=True,  # Close modal when escape is pressed
                      fade=True,  # Let the modal fade instead of appear.
            ),
        ]) ##end Div



    
### Gallery
def recent_sales_modal_layout():
    return html.Div(
        children = [
            dbc.Modal(
                [
                    dbc.ModalHeader("Property Details"),
                    dbc.ModalBody([
                        dbc.CardImg(id='rs-src',src='', top=True,
                                    className='img-fluid mb-2',
                                    style={"width":"auto",
                                           "height":"auto",
                                           "maxWidth":"500px",
                                           "maxHeight":"500px",
                                    }),
                        html.Div("", className='mb-1',id='line1'),
                        html.Div("", className='card-text',id='line2'),
                        html.Div("", className='card-text',id='line2a'),
                        html.Div("", className='card-text',id='line1a'),
                        html.Div("", className='card-text',
                                 id='line3',
                                 style={"textAlign":"left","fontSize":"15px"}),
                        html.Div("", className='card-text',
                                 id='line3a',
                                 style={"textAlign":"left","fontSize":"15px"}),
                    ]),
                ],
                id='recent-sales-modal',
                is_open=False, 
                size="lg",  # "sm", "lg", "xl"
                backdrop=True,  # backdrop close
                scrollable=True,  # Scrollable
                centered=True,  # Vertically center modal 
                keyboard=True,  # Close modal when escape is pressed
                fade=True,  # Let the modal fade instead of appear.
            )
        ])

