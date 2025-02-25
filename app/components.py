from dash import Dash, dcc,html
import dash_bootstrap_components as dbc

def selectTown ( ) :
    return html .Div ( 
        children = [ 
            dcc . Dropdown (
                [ 'ArlingtonMA' , 'BerkeleyCA', 'BostonMA' , 'CambridgeMA', 'PortsmouthNH'] ,
                'ArlingtonMA' ,
                id = 'controls-dropdown-town' ,
                clearable = False ,
                style  =  {
                    "borderColor"  : "white",
                    "fontSize"     : "20px",
                    "verticalAlign":"bottom",
                },
            ),
        ]
    )

def selectDataset ( ) :
    return html . Div (
        children = [
            html.Br ( ) ,
            html.H6('Datasets:',id="controls-datasets-header"),
            dcc . RadioItems (
                options  =  [],
                value    =  None,
                inline   =  True,
                id       =  'controls-radiobuttons-datasets',
                labelStyle = {'paddingRight': '20px','align':"left"},
            )
        ], id = 'controls-datasets'
    )

def selectTab ( ) :
    return html . Div (
        children = [
            html.Br ( ) ,
            html.H6('Displays:'),
            dcc . RadioItems (
                options  =  [],
                value    =  None,
                inline   =  True,
                id       =  'controls-radiobuttons-tabs',
                labelStyle = {'paddingRight': '20px','align':"left"},
            )
        ], id = 'controls-tabs'
    )

def selectView ( ) :
    return html . Div (
        children = [
            html.Br ( ) ,
            html.H6('Views:',id="controls-views-header"),
            dcc . RadioItems (
                options  =  [],
                value    =  None,
                inline   =  True,
                id       =  'controls-radiobuttons-views',
                labelStyle = {'paddingRight': '20px','align':"left"},
            )
        ], id = 'controls-views'
    )

def selectGroup ( ) :
    return html . Div (
        children = [
            html.Br ( ) ,
            html.H6('Groups:'),
            dcc . RadioItems (
                options  =  [],
                value    =  "",
                inline   =  True,
                id       =  'controls-radiobuttons-groups',
                labelStyle = {'paddingRight': '20px','align':"left"},
            )
        ], id = 'controls-groups',
        style={'display':'none'}
    )


def selectMetric ( ) :
    return html . Div (
        children = [
            html.Br ( ) ,
            html.H6('Metrics:'),
            dcc . RadioItems (
                options  =  [],
                value    =  "",
                inline   =  True,
                id       =  'controls-radiobuttons-metrics',
                labelStyle = {'paddingRight': '20px','align':"left"},
            )
        ], id = 'controls-metrics',
        style={'display':'none'}
    )

def selectSeriesType ( ) :
    return  html.Div (
        children = [
            html.Br ( ) ,
            html.H6('Series Types:'),
            dcc.Dropdown (
                options = [],
                value = "",
                id='controls-dropdown-series-types'
            )],
        id='controls-series-types',
        style={'display':'none','fontSize':'12px'}
    )

def selectSeries ( ) :
    return  html.Div (
        children = [
            html.Br ( ) ,
            html.H6('Series:'),
            dcc.Dropdown (
                options = [],
                value = 0,
                id='controls-dropdown-series'
            )],
        id='controls-series',
        style={'display':'none','fontSize':'10px'}
    )


def searchAddress ( ):
    return html.Div( id = 'controls-address-search-container', children = [
        html.Br ( ) ,
        html.H6('Address Search:'),
        
        dbc.Row(
            [
                dbc.Col(
                    dcc.Dropdown (
                        options = [],
                        value = '',
                        placeholder='Street Name...',
                        id='controls-street-name-dropdown',
                        style={'width':'150px','float':'left'}
                    ),
                ),
                dbc.Col(
                    dcc.Dropdown (
                        options = [],
                        value = '',
                        placeholder='Number',
                        id='controls-street-number-dropdown',
                        style={'width':'80px','float':'left'}
                    ),
                )
            ]
        )
    ], style = {'display':'inline-block'}
    ) 

def sidebar_layout ( params : dict ) -> dbc . Container :
    return dbc . Container(
        children = [
            html.Div(
                [
                    html.H4("Controls"),
                    selectTown ( ),
                    selectDataset ( ),
                    selectTab ( ),
                    selectView ( ),
                    selectGroup ( ),
                    selectMetric ( ),
                    selectSeriesType ( ),
                    selectSeries ( ),
                    searchAddress ( ),
                ],
                className="sidebar-container",
            )
        ]
    )
        


def pageNavbar ( params : dict ) -> dbc . NavbarSimple :
    return dbc.NavbarSimple(
        brand="Polis",
        brand_href="https://github.com/irl-labs/polis/",
        sticky = "top",
        color="primary",
        dark=True,

        children=[           
            dcc . Location ( id  =  'url' )   ,
            dcc . Loading  ( id  =  "loading" ,
                             children = html . Div (
                                 id = "loading-output"
                             ),
                             
            ) ,
            dbc.RadioItems(
                id       =  'selected-ppt',
                options=[
                    {
                        "label":x.title(),
                        "value":x
                    } for x in params.keys()
                ],
                value = list ( params.keys() ) [0] ,
                inline=True,
                labelStyle = {'color':'white',
                              'paddingRight':'20px',
                              'align':"left",'fontSize':'20px'},
                className="ml-auto",
            ),
            #dbc.Button(
            #    "Controls",
            #    id="controls-button",
            #    color="primary",
            #    className="ml-auto",
            #    style={"marginRight": "10px","paddingTop": "0px"},
            #),
            dbc.Button(
                "Help",
                id="help-button",
                color="primary",
                className="ml-auto",
                style={"marginRight": "10px","paddingTop": "0px"},
            ),
        ],
    )

def pageFooter():
    import datetime
    current_year = datetime.date.today().year
    
    return html.Footer(
        dbc.Container(
            dbc.Row(
                dbc.Col(
                    html.Small(
                        f"irl Labs - All Rights Reserved © {current_year}",
                        className="text-muted",
                    ),
                    style={"align":"left", "paddingTop": "0px"},
                ),
            ),
        ),
    )

def pageSidebar ( params : dict ) -> dbc . Card :
    return dbc.Card (
        id="sidebar-card",
        style={"height": "90vh", "width": "15%", "float": "left"},
        children=[
            dbc.Collapse(
                dbc.CardBody(
                    sidebar_layout(params),
                    style={"padding": "10px"}
                ),
                id = "sidebar-collapse",
                navbar=True,
                is_open=True,
            ),
        ],
    )


def pageContent ( params : dict ) -> dbc . Card :
    return  dbc.Card(
        id="content-card",
        children = [
            html.Div ( id='controls-date-slider-container',
                       style={'display':'block',
                              'width': '60%',
                              'padding': '10px 20px 40px 20px'},
                       children = [
                           dcc.Slider (
                               id='controls-date-slider',
                               min=0,
                               max=0,
                               step=1,
                               value=0,
                               tooltip={"placement": "bottom",
                                        "always_visible": False}
                           ),
                       ]),
            
            html.Center([html.H5(
                dcc . Markdown (
                    "",
                    id = 'content-title'
                )
                ,id='content-title-h4'
            )]),
            html . Div ( '',
                         id = 'table-container',
                         style={'width':'99%','height':'99vh',
                                'display':'none'}
            ),
            html.Center(
                children = [
                    html.Div([
                        html.Div(
                            [""],
                            id='gallery-container',
                            style={"display":"block"}
                        ),
                        dbc.Pagination(
                            id='pagination',
                            max_value=25,
                            fully_expanded=False,
                            first_last=True
                        )
                    ],
                             id = "recent-sales-gallery-container",
                             style={"display":"none"}
                    ),
                    html . Div ( id='scatter-container', children = [
                        scatter_charts(),
                    ], style =  {'display':'none',} ),
                    html . Div ( id='graph-container', children = [
                        dcc.Graph(id="graph-display",
                                  figure = {},
                                  style={'height':"70vh","width":"99%"},
                                  responsive=True,
                                  clear_on_unhover=True
                        ),
                        dcc.Tooltip(id="graph-tooltip"),
                    ], style =  {'display':'none',} ),
                ],
            ),
        ],
        style={
            "backgroundColor": "lightgray",
            "height": "90vh",
            "align": "center"
        },
    )


def property_summary(df) -> html.Div :
    styles = {}
    return html.Div(
        children = [
            html.H6(
                children = (
                    f'Owner: {df.owner}'
                ),
                style=styles
            ),
            html.H6(
                children = (
                    f'{df.land_use[6:]} '
                    f'{df["style"]} '
                    f'built in {df["year_built"]} '
                ),
                style=styles
            ),
            html.H6(
                children = (
                    f'{df["rooms"]} rooms / {df["bedrooms"]} beds'
                    f' / {df["baths"]} baths in {df["units"]} units'
                ),
                style=styles
            ),
            html.H6(
                children = (
                    f'Lot Size: {df["area"]:,.0f} ft\u00b2'
                ),
                style=styles
            ),
            html.H6(
                children = (
                    f'Finished Area: {df["living_area"]:,.0f} ft\u00b2'
                ),
                style=styles
            ),
            html.H6(
                children = (
                    f'Assessment : ${df["total"]:,.0f}'
                ),
                style=styles
            ),
            html.H6(
                children = (
                    f'Land Value : ${df["land"]:,.0f}'
                ),
                style=styles
            ),
        ]
    )


def modal_charts(figure,title):

    return dbc.Card(children=[
        html.Div([
            html.H6(
                dcc . Markdown ( title )
            ),
            dcc.Graph(figure=figure,
                      config={'displayModeBar': False},
                      style={'width': '100%', #'height': '50vh',
                             'display': 'block'},
            ),
        ]
        )
    ],body=True)


def scatter_charts():
    return html.Div([
        html.Div([

            html.Div([
                dcc.Dropdown(
                    [],'Average Single Family Value',  #series,
                    id='crossfilter-xaxis-column',
                    style={'textAlign':'left'}
                ),
                dcc.RadioItems(
                    ['Linear', 'Log'],
                    'Linear',
                    id='crossfilter-xaxis-type',
                    labelStyle={'display': 'inline-block', 'marginTop': '5px'}
                )
            ],
            style={'width': '49%', 'display': 'inline-block'}),

            html.Div([
                dcc.Dropdown(
                    [],'DOR Income Per Capita',  #series,
                    id='crossfilter-yaxis-column',
                    style={'textAlign':'left'}
                ),
                dcc.RadioItems(
                    ['Linear', 'Log'],
                    'Linear',
                    id='crossfilter-yaxis-type',
                    labelStyle={'display': 'inline-block', 'marginTop': '5px'}
                )
            ], style={'width': '49%', 'float': 'right', 'display': 'inline-block'})
        ], style={
            'padding': '10px 5px'
        }),

        html.Div([
            dcc.Graph(
                id='crossfilter-indicator-scatter',
                hoverData={'points': [{'customdata': 'Arlington'}]}
            )
        ], style={'width': '49%', 'display': 'inline-block', 'padding': '0 20'}),
        html.Div([
            dcc.Graph(id='x-time-series'),
            dcc.Graph(id='y-time-series'),
        ], style={'display': 'inline-block', 'width': '49%'}),

        html.Div ( [
            html.Div([
                dcc.Dropdown(
                    [],"Arlington",  #municipalities,
                    id='crossfilter-town--dropdown')
                ],style={'width':'50%','textAlign':'left'}), 
            ],style={'display': 'flex'}),        
        ],
                    id = 'scatter-layout-container',
                    style={'display':'block'}
    )


## RECENT SALES
def recent_sales_get_data(data):
    stub =  'https://arlington.patriotproperties.com/image/'
    data['img_url']=stub+data['image']+'.jpg'
    data['rooms']=data['rooms'].str.replace("\]|\[| ","",regex=True).str.replace(",","&").fillna('0')
    data['bedrooms']=data['bedrooms'].str.replace("\]|\[| ","",regex=True).str.replace(",","&").fillna('0')
    data['bathrooms']=data['bathrooms'].str.replace("\]|\[| ","",regex=True).str.replace(",","&").fillna('0')

    def unlist(bs):
        if type(bs)==list:
            return ', '.join([x.title() for x in set(bs)])
        return bs
    
    foo=data[['pid','grant_type','name']]
    foo=foo.explode(['grant_type','name'])
    foo['grant_type']=foo['grant_type'].replace({1:'Seller',0:'Buyer'})
    foo=foo.groupby(['pid','grant_type']).agg({
        'name':list
    }).reset_index()
    foo=foo.pivot(index='pid',columns='grant_type',values='name')
    data = data.merge(foo,on='pid',how='left')
    data['Buyer']=data['Buyer'].apply(unlist)
    data['Seller']=data['Seller'].apply(unlist)
    #print(data.iloc[0],type(data.iloc[0].Seller[0]))
    
    return data.to_dict(orient='records')



def recent_sales_format_data(item):
    from pandas import to_datetime
    line1 = f'{item["address"]}'
    line1a = f'{to_datetime(item["date"]).strftime("%b. %-d, %Y")} - ${item["price"]:,.0f}'
    line2 = f'{item["bedrooms"]}BR/{item["bathrooms"]}BA/{item["living_area"]:,.0f}ft\u00b2/{item["lot_size"]:,.0f}ft\u00b2 lot'
    line2a = f'{item["land_use"][6:]} - {item["style"]}'
    line3  = f'Buyer: {item["Buyer"]}'
    line3a = f'Seller: {item["Seller"]}'
    return line1, line2, line1a, line2a, line3, line3a


def recent_sales_create_card(idx, item):
    line1, line2, line1a, line2a, line3, line3a = recent_sales_format_data(item)
    
    card_content = html.Div([
        dbc.Card([
            dbc.CardHeader([html.H5(line1),html.H6(line1a)]),
            html.Center(dbc.CardImg(src=item['img_url'], bottom=True,
                        style={"width":"auto",
                               "height":"auto",
                               "maxWidth":"300px",
                               "maxHeight":"300px",
                        })),
            dbc.CardBody([
                html.Div(line2a, className='card-text'),
                html.Div(line2, className='card-text'),
            ])
        ], style={"cursor": "pointer"},
                 className='mb-1')
    ], id={"type": "image-card", "index": idx})

    return dbc.Col(card_content, width=3)


def recent_sales_generate_gallery(recent_sales,page_number=1, page_size=8):
    if len(recent_sales)==0:
        return None
    
    s_idx = (page_number - 1) * page_size
    e_idx = s_idx + page_size

    return html.Div([
        dbc.Row([
            recent_sales_create_card(idx, item)
            for idx, item in enumerate(recent_sales[s_idx:e_idx])
        ]),
    ])



def tree_to_dash(nodes, indentation_level=0):
    components = []
    INDENT_SIZE = 20  # Number of pixels for each indentation level.

    for node in nodes:
        children = [html.Summary(node['title'])]

        if node['children']:
            # Increment the indentation for nested children.
            children.append(tree_to_dash(node['children'], indentation_level + 1))

        style = {'paddingLeft': f'{INDENT_SIZE * indentation_level}px'}
        if node.get('content'):
            children.append(html.Div(node['content'], style=style))

        components.append(html.Details(children, style=style))

    return html.Div(components,style = {'paddingLeft':'20px'})


