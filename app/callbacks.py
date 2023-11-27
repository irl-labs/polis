from components import *
from utils      import *
from tables     import *
from maps       import *
from charts     import *

from pandas import DataFrame, to_datetime, isnull
from json import dumps, loads
from textwrap import dedent as d

def get_callbacks(app, params,
                  int_value_pairs, attributes, addresses,street_search,
                  loc_pid, loc_polygons,solar,dor_series,recent_sales,
                  db_connection):
    from dash import Input, Output, State, ALL, no_update, callback_context
    from dash.exceptions import PreventUpdate

    # collapse sidebar, needs to be change to expand content area into sidebar
    @app.callback(
        Output("sidebar-collapse", "is_open"),
        Input("controls-button", "n_clicks"),
        State("sidebar-collapse", "is_open"),
    )
    def toggle_sidebar(n, is_open):
        if n:
            return not is_open
        return is_open


    # Callback to store the selected dataset and views in the data store
    @app.callback(
        Output("polis-data-store", "data"),
        Input("selected-ppt", "value"),
        Input("controls-dropdown-town", "value"),
        Input("controls-radiobuttons-datasets", "value"),
        Input("controls-radiobuttons-tabs", "value"),
        Input("controls-radiobuttons-views", "value"),
        Input("controls-radiobuttons-groups", "value"),
        Input("controls-radiobuttons-metrics", "value"),
        Input("controls-dropdown-series-types", "value"),
        Input("controls-dropdown-series", "value"),
        
        State("polis-data-store", "data"),
    )
    def store_selected_data(ppt, town, dataset, tab, view,
                            group, metric, series_type, series,
                            data):

        if town is not None and dataset is not None and tab is not None and view is not None:
            extra_params   = params[ppt][dataset][tab][view]
        else:
            extra_params   = {}


        municipalities = int_value_pairs [
            int_value_pairs . item == 'dor'
        ] [ 'value' ] . to_list ( )
        dor_scatter_series = list(dor_series.dor_databank_series.unique())

        return {
            "params":params,
            #"int_value_pairs" :  int_value_pairs.to_dict('records'),
            "selected-ppt": ppt,
            "controls-dropdown-town": town,
            "controls-radiobuttons-datasets":dataset,
            "controls-radiobuttons-tabs":tab,
            "controls-radiobuttons-views":view,
            "controls-radiobuttons-groups":group,
            "controls-radiobuttons-metrics":metric,
            "controls-dropdown-series-types":series_type,
            "controls-dropdown-series":series,
            "extra-params":extra_params,
            "municipalities":municipalities,
            "dor_scatter_series":dor_scatter_series
        }


    def address_search_zoom(mapp, streetname, streetnum,lat,lon,zoom):
        mask = (addresses.streetName==streetname)&\
            (addresses.streetNum==streetnum)
        if mask.any():
            pid = addresses[mask].iloc[0].pid

            loc_id=loc_pid[loc_pid.pid==pid].iloc[0].loc_id
            found = loc_polygons[loc_polygons.loc_id==loc_id].iloc[0]
            polygon = [
                {
                    "source": found["geometry"].__geo_interface__,
                    "type": "line",
                    "line": {"width":2.5},
                    "color": "red",
                },
                {
                    "source": found["geometry"].__geo_interface__,
                    "type": "fill",
                    "color": "yellow",
                    "opacity":0.20,
                },
            ]

            mapp = mapp.update_layout  (
                mapbox  =  {
                    "center" :  { "lat" : found.lat,
                                  "lon" : found.lon },
                    "zoom"   :  17.5 ,
                    "layers" : polygon
                })
        else:
            mapp = mapp.update_layout  (
                mapbox  =  {
                    "center" :  { "lat" : lat, "lon" : lon },
                    "zoom"   :  zoom ,
                })

        return mapp
        

    @app.callback(
        Output("loading-output" , "children" ) ,
        Output("content-title", "children"),
        Output("table-container", "children"),
        Output("table-container", "style"),
        Output("graph-display", "figure"),
        Output("graph-container", "style"),
        Output('scatter-container', 'style'),
        Output("recent-sales-gallery-container","style"),
        Input("selected-ppt", "value"),
        Input("controls-dropdown-town", "value"),
        Input("controls-radiobuttons-datasets", "value"),
        Input("controls-radiobuttons-tabs", "value"),
        Input("controls-radiobuttons-views", "value"),
        Input("controls-radiobuttons-groups", "value"),
        Input("controls-radiobuttons-metrics", "value"),
        Input("controls-dropdown-series-types", "value"),
        Input("controls-dropdown-series", "value"),
        Input("controls-date-slider", "value"),
        Input("controls-street-name-dropdown","value"),
        Input("controls-street-number-dropdown","value"),
        
        State("table-container", "style"),
        State("graph-container", "style"),
        State("scatter-container", "style"),
        State("recent-sales-gallery-container","style"),
        State("polis-data-store", "data"),
    )
    def update_page_content(ppt, town, dataset, tab, view,
                            group, metric,
                            series_type, series, date,
                            streetname, streetnum,
                            table_style, graph_style, scatter_style,
                            gallery_style,
                            data):

        if data == {}:
            raise PreventUpdate

        loading_div = html . Div ( id = "loading-output" ),

        table_style['display']='none'
        graph_style['display']='none'
        scatter_style['display']='none'
        gallery_style['display']='none'
        content = html.Center([html.Br(),html.Br(),html.H4("Coming Soon")])
        figure = {}

        dict = data['params'][ppt][dataset][tab][view]
        query = dict['query']
        if ppt=='governance' and view=='DOR scatter':
            scatter_style['display']='block'
            

        if 'query_dates' in dict :
            
            if '{item}' in dict [ 'query_dates' ] :
                
                dates = get_data_from_db (
                    dict [ 'query_dates' ] . format ( item = group ),
                    db_connection
                ) [ 'dates' ] . to_list ( )
                
                dict [ 'dates' ] =\
                    [ x if type ( x ) == int
                      else x . strftime ( '%Y-%m-%d' ) for x in dates ]

        if 'dates' in dict.keys():
            date = dict['dates'][date]

        ## update color on maps for change in controls Groups (options traces)
        if 'color' in dict.keys():
            if ppt != 'people':
                dict['color']=group

        df = get_data_from_db (
            query.format(
                year=date,
                series_type=series_type,
                series_metric=series.replace('%','%%'),
                date=date,
                item=group
            ),
            db_connection
        )


        if len(df)==0:
            table_style['display']='block'
            title = get_title (
                df, dict,
                town, ppt, dataset, tab, view,
                group, metric,
                series_type, series, date
            )       
            return (
                loading_div,
                title,
                content,
                table_style,
                figure,
                graph_style,
                scatter_style,
                gallery_style
            )
        
        df = df_transform (
            df,
            ppt, dataset, tab, view, group, date,
            int_value_pairs,
            attributes,
            addresses,
        )
        
        title = get_title (
            df, dict,
            town, ppt, dataset, tab, view,
            group, metric,
            series_type, series, date
        )       

            
        #messed up; title needs pivot first
        if tab == "tables":
            if ((dataset == "schools" and view == "summary")
            or (dataset == "financials" and view == "DOR")):

                    title = get_title (
                        df, dict,
                        town, ppt, dataset, tab, view,
                        group, metric,
                        series_type, series, date
                    )       
                    

        if tab == "maps" :
            if view != ' Solar systems':
                if 'pid' in df . columns:
                    df = df_maps (
                        dataset,
                        group,
                        df,
                        loc_pid,
                        loc_polygons
                    )
            
        
        if tab=='charts':
            if 'chart_type' in dict:
                graph_style['display']='block'
                if dict['chart_type']=='line':
                    if view=='mcas':
                        df = df_pivot(df,'mcas')
                    figure = line_chart(df,dict,metric)
                elif dict['chart_type']=='boxplot':
                    figure = boxplot(df,dict)
                elif dict['chart_type']=='histogram':
                    if metric is not None:
                        dict['x']=metric
                    figure = histogram(df,dict)
                elif dict['chart_type']=='scatter':
                    graph_style['display']='none'
                    scatter_style['display']='block'
                    

        elif tab == 'maps':

            if dataset=='water':
                dict['range_color'] = dict['range_color_'+group]

            graph_style['display']='block'
            map_params = {
                'color' :  dict[ 'color'] if 'color' in dict else '',
                'geometry_key' :  dict[ 'geometry_key']
                if 'geometry_key' in dict else '',
                'range_color' :  dict[ 'range_color']
                if 'range_color' in dict else [-2,2],
                'lat'   :  dict[ 'lat'  ] if 'lat'   in dict else '',
                'lon'   :  dict[ 'lon'  ] if 'lon'   in dict else '',
                'zoom'  :  dict[ 'zoom' ] if 'zoom'  in dict else 12.5,
                'traces_visible'  :  dict[ 'traces_visible' ]
                if 'traces_visible'  in dict else None,
            }
            if 'map_type' in dict:
                if dict['map_type']=='mapbox_line':
                    figure = mapbox_line ( df, map_params )
                if dict['map_type']=='mapbox_choropleth':
                    if view == ' Solar systems':
                        figure = mapbox_choropleth ( solar , map_params )
                    else:
                        figure = mapbox_choropleth ( df , map_params )
            else:
                figure = mapbox_scatter ( df , map_params )

            if streetname!='' and streetname is not None:
                if streetnum!='' and streetnum is not None:
                    lat  = dict['lat']
                    lon  = dict['lon']
                    zoom = dict['zoom']
                    figure = address_search_zoom(
                        figure,
                        streetname,
                        streetnum,
                        lat,lon,zoom
                    )

                    
        elif tab=='tables':

            table_style['display']='block'
            if dataset == 'sales' and view == 'Recent':
                table_style['display']='none'
                gallery_style['display']='block'
                #content = recent_sales_generate_gallery(recent_sales,1)
            elif dataset == 'meetings' and view == 'transcripts':
                tmp = df[metric][0]
                if tmp is not None:
                    if metric == 'outline':
                        tmp = tmp.iloc[0].replace("   ","   \n")
                    
                        tree = parse_markdown_tree(tmp)
                        content = tree_to_dash(tree)

                    elif metric == "Q&A":
                        bodies = []
                        for dict in tmp:
                            bodies.append(
                                display_pieces(
                                    dict["Q"],[html.Br(),
                                               dcc.Markdown(dict["A"])]
                                )
                            )
                        content = bodies

                    elif metric == "raw":
                        content = tmp
                else:
                    content = html.Center([html.Br(),html.Br(),html.H4("Coming Soon")])
                        
            else:
                content = display_table ( df )


        return (
            loading_div,
            title,
            content,
            table_style,
            figure,
            graph_style,
            scatter_style,
            gallery_style
        )


    
    # Navigation and Controls data ######################################

    # Callback to create dates slider
    @app.callback(
        Output('controls-date-slider-container','style'),
        Output("controls-date-slider", "min"),
        Output("controls-date-slider", "max"),
        Output("controls-date-slider", "value"),
        Output("controls-date-slider", "marks"),
        Input("selected-ppt", "value"),
        Input("controls-dropdown-town", "value"),
        Input("controls-radiobuttons-datasets", "value"),
        Input("controls-radiobuttons-tabs", "value"),
        Input("controls-radiobuttons-views", "value"),
        Input("controls-radiobuttons-groups", "value"),
        Input("controls-radiobuttons-metrics", "value"),
        Input("controls-dropdown-series-types", "value"),
        Input("controls-dropdown-series", "value"),
        State("controls-date-slider-container", "style"),
        State("polis-data-store", "data"),
    )
    def create_dates_slider(ppt, town, dataset, tab, view,
                            group, metric, series_type, series,
                            style, data):
        if data=={}:
            raise PreventUpdate

        dict = data['params'][ppt][dataset][tab][view]

        if 'dates' not in dict.keys():
            style['display']='none'
            return style, None, None, None, {}


        style['display']='block'
        current_date=''
        dates, date_idx, marks = format_date_slider(dict,group,current_date,db_connection)
        return style, dates[0], len(dates)-1, date_idx, marks

    
    

    @app.callback(
        Output("controls-radiobuttons-datasets", "options"),
        Output("controls-radiobuttons-datasets", "value"),
        Output("controls-datasets-header", "children"),
        Input("selected-ppt", "value"),
        State("polis-data-store", "data"),
    )
    def update_dataset_options(ppt, data):
        if data == {}:
            raise PreventUpdate

        options = sorted(list(data['params'][ppt].keys()))
        return options, options[0],ppt.title()+' Datasets:'

    @app.callback(
        Output("controls-radiobuttons-tabs", "options"),
        Output("controls-radiobuttons-tabs", "value"),
        Input("selected-ppt", "value"),
        Input("controls-radiobuttons-datasets", "value"),
        State("polis-data-store", "data"),
    )
    def update_tab_options(ppt, dataset, data):
        if data =={}:#is None:
            raise PreventUpdate

        options = sorted(list(data['params'][ppt][dataset].keys()))[::-1]
        value = data["controls-radiobuttons-tabs"]
        if value is None:
            value = options[0]
        if value not in options:
            value = options[0]
        return options, value

    
    @app.callback(
        Output("controls-radiobuttons-views", "options"),
        Output("controls-radiobuttons-views", "value"),
        Output("controls-views-header", "children"),
        Input("selected-ppt", "value"),
        Input("controls-radiobuttons-datasets", "value"),
        Input("controls-radiobuttons-tabs", "value"),
        State("polis-data-store", "data"),
    )
    def update_view_options(ppt, dataset, tab, data):
        if data == {}:
            raise PreventUpdate

        options = sorted(list(data['params'][ppt][dataset][tab].keys()))
        if (ppt != 'governance') and (dataset != 'schools') and (tab == 'charts'):
            options = options[::-1]
        return options, options[0],tab[:-1].title() + ' Views:'

    
    @app.callback(
        Output("controls-radiobuttons-groups", "options"),
        Output("controls-radiobuttons-groups", "value"),
        Output("controls-groups", "style"),
        Input("selected-ppt", "value"),
        Input("controls-radiobuttons-datasets", "value"),
        Input("controls-radiobuttons-tabs", "value"),
        Input("controls-radiobuttons-views", "value"),
        State("polis-data-store", "data"),
        State("controls-groups", "style"),
    )
    def update_group_options(ppt, dataset, tab, view, data, style):

        if data=={}:
            raise PreventUpdate
        
        dict = data['params'][ppt][dataset][tab][view]
        
        if dict is None:
            raise PreventUpdate

        options = []
        style['display']='none'
        
        if 'traces' in dict.keys():
            options = sorted(dict['traces'])
            style['display']='block'
        else:
            return [],None,style

        value = data['controls-radiobuttons-groups'] 
        if value is None:
            value = options[0]
        if value not in options:
            value = options[0]

        return options, value, style

    @app.callback(
        Output("controls-radiobuttons-metrics", "options"),
        Output("controls-radiobuttons-metrics", "value"),
        Output("controls-metrics", "style"),
        Input("selected-ppt", "value"),
        Input("controls-radiobuttons-datasets", "value"),
        Input("controls-radiobuttons-tabs", "value"),
        Input("controls-radiobuttons-views", "value"),
        State("polis-data-store", "data"),
        State("controls-metrics", "style"),
    )
    def update_group_options(ppt, dataset, tab, view, data, style):

        if data=={}:
            raise PreventUpdate
        
        dict = data['params'][ppt][dataset][tab][view]
        
        if dict is None:
            raise PreventUpdate

        options = []
        style['display']='none'
        
        if 'metrics' in dict.keys():
            options = sorted(dict['metrics'])
            style['display']='block'
        else:
            return [],None,style

        value = data['controls-radiobuttons-metrics'] 
        if value is None:
            value = options[0]
        if value not in options:
            value = options[0]

        return options, value, style

    
    @app.callback(
        Output("controls-dropdown-series-types", "options"),
        Output("controls-dropdown-series-types", "value"),
        Output("controls-series-types", "style"),
        Input("selected-ppt", "value"),
        Input("controls-radiobuttons-datasets", "value"),
        Input("controls-radiobuttons-tabs", "value"),
        Input("controls-radiobuttons-views", "value"),
        State("polis-data-store", "data"),
        State("controls-series-types", "style"),
    )
    def update_series_types_options(ppt, dataset, tab, view, data, style):

        if data == {}:
            raise PreventUpdate
            
        dict = data['params'][ppt][dataset][tab][view]
        
        if dict is None:
            raise PreventUpdate

        options = []
        style['display']='none'
        
        if 'series' in dict.keys():
            options = sorted(dict['series'])
            style['display']='block'
        else:
            return [],None,style

        value = data['controls-dropdown-series-types'] 
        if value is None:
            value = "GeneralFunds"#options[0]
        if value not in options:
            value = options[0]

        return options, value, style
  

    @app.callback(
        Output("controls-dropdown-series", "options"),
        Output("controls-dropdown-series", "value"),
        Output("controls-series", "style"),
        Input("controls-dropdown-series-types", "value"),
        State("controls-radiobuttons-tabs", "value"),
        State("polis-data-store", "data"),
        State("controls-series", "style"),
    )
    def update_series_options(series_type, tab, data, style):

        if data =={}:
            raise PreventUpdate

        if series_type is None:
            style['display']='none'
            return [],'',style

        series = series_type_2_series(
            int_value_pairs,
            series_type
        )

        options = sorted(series)
        style['display']='block'

        value = data['controls-dropdown-series'] 
        if value is None:
            value = options[0]
        if value not in options:
            value = options[0]

        if tab in ['charts','tables']:
            style['display']='none'

        return options, value, style

    



    def display_pieces(summary,piece,dataset='entity'):
        return html.Div([html.Details([
            html.Summary(summary),
            html.Div(piece, id='display-pieces', style={"paddingLeft":"20px"})
        ],open=False if summary != dataset\
                            .replace('deeds','deeds_details')\
                            .replace('parcels','assessments')
                            else True
        )
        ],style={"paddingLeft":"20px"})

    @app.callback(
        Output("solar_modal", "is_open"),
        Output("solar_modal-header", "children"),
        Output("solar_modal-header2", "children"),
        Output("solar_modal-body", "children"),
        Output("solar_modal-image-1", "src"),
        Output("solar_modal-image-2", "src"),
        Output("solar_modal-production", "children"),
        Input("graph-display", "clickData"),
        State("controls-radiobuttons-tabs", "value"),
        State("controls-radiobuttons-views", "value"),
        State("solar_modal", "is_open"),
    )
    def toggle_solar_modal(clickData, tab, view, is_open):
        if tab != "maps":
            raise PreventUpdate
        if view != " Solar systems":
            raise PreventUpdate
        
        # is it a click or hover event?
        ctx = callback_context

        if ctx.triggered[0]["prop_id"] == "graph-display.clickData":
            if clickData:
                cols = [x for x in list(solar.columns) if x!='geometry']
                customdata = dict(zip(cols,clickData["points"][0]['customdata']))
            
                img_roof = "data:image/png;base64," +b64image(customdata['roof_image'])
                img_house = customdata['house_image']

                chart_params = {
                    'title' : """
                    {col} History
                    """,
                    'XY':('timestamp','kwh'),
                }

                bodies = []

                for col in ['watts','financials','entity','joules','amps']:
                    if customdata[col] is not None:
                        bodies.append(display_pieces(col,d(dumps(customdata[col],indent=2))))

                production = get_solar_production(customdata['pid'], db_connection)
                chart = ''
                if production is not None:
                    if len(production)>0:
                        chart_params["yaxis_range"]=[0,200]
                        chart_fig = line_chart_simple(
                            production,
                            chart_params
                        )
                        
                        chart = modal_charts(
                            chart_fig,
                            chart_params['title'].format(col='Solar Production')
                        )
                    
                    
                        #bodies.append(display_pieces('production',chart))
                
                header = f"{customdata['address']} - {customdata['owner']}"
                header2 = f"{customdata['panels']} panels, {customdata['watt']/1000:.2f}kW on {customdata['date']} for ${customdata['cost']:,.0f}"

                return not is_open, header, header2, bodies, img_roof, img_house, chart

        return is_open, None, None, None, None, None, None



    @app.callback(Output("graph-tooltip", "show"), 
                  Output("graph-tooltip", "bbox"),
                  Output("graph-tooltip", "children"), 
                  Input("graph-display", "hoverData"),
                  State("graph-display", "figure"),
                  State("controls-radiobuttons-datasets", "value"),
                  State("controls-radiobuttons-tabs", "value"),
                  State("controls-radiobuttons-views", "value"),
    )
    def display_hover(hoverData,map_data,dataset,tab,view):
        if tab == 'charts':
            raise PreventUpdate
        if hoverData is None:
            return False, no_update, no_update

        #if view != ' Solar systems':
        #    return False, no_update, no_update

        # is it a click or hover event?
        ctx = callback_context

        if ctx.triggered[0]["prop_id"] == "graph-display.clickData":
            ##open modal
            return True,  no_update, no_update
    
        elif ctx.triggered[0]["prop_id"] == "graph-display.hoverData":
            pt = hoverData["points"][0]
            bbox = pt["bbox"]

            if view == ' Solar systems':

                df_row = solar.iloc[pt["pointNumber"]]
                img_src = "data:image/png;base64," +b64image(df_row['roof_image'])

                string = (f"{df_row['address']} - {df_row['owner']}\n"
                          f"{df_row['panels']} panels, {df_row['watt']/1000:.2f}kW"
                          f" on {df_row['date']} for ${df_row['cost']:,.0f}"
                )
        
                children = [
                    html.Div([
                        html.Img(
                            src=img_src,
                            style={"width": "100%", "height":"80%",
                                   'display': 'block', 'margin': '0 auto'}
                        ),
                        html.P(
                            string
                        ),
                    ], style={'width': '500px', 'white-space': 'normal'})
                ]
            elif dataset in ['financials']:
                customdata = hoverData['points'][0]['customdata']

                string3 = f"Value: ${customdata[2]:,.0f}"
                if '%' in customdata[1]:
                    string3 = f"Value: {customdata[2]/100}%"

                children = [
                    html.Div([
                        html.P([
                            f"Town: {customdata[0]}",
                            html.Br(),
                            f"Series: {customdata[1]}",
                            html.Br(),
                            string3,
                            html.Br(),
                            f"Z-score: {customdata[3]:.3f}",
                        ],
                               style={"textAlign":"left","fontSize":"15px"}
                        ),
                    ])
                ]
                
                return True,  bbox, children

            elif dataset in ["elections","registered","residents"]:
                customdata = hoverData['points'][0]['customdata']
                loc_id = customdata[0]
                name = customdata[1]
                address = list(set(customdata[2]))

                string1 = f"Names: {', '.join(name)}"
                string2 = f"Address:  {', '.join(address)}"

                if len(name)>2:
                    string1=f'Name: {name[0]},{name[1]} and {len(name)-2} more names'
                if len(address)>2:
                    string2=f'Address: {address[0]},{address[1]} and {len(address)-2} more addresses'
                children = [
                    html.Div([
                        html.P([
                            string1,
                            html.Br(),
                            string2
                        ],
                               style={"textAlign":"left","fontSize":"15px"}
                        ),
                    ])
                ]
                
                return True,  bbox, children

            elif dataset in ["parcels","deeds","permits","sales",
                             "meetings","water","business","energy"]:
                customdata = hoverData['points'][0]['customdata']

                if dataset=='deeds':
                    cols =  ['loc_id','deed_type', 'year', 'date', 'book',
                             'page', 'docno', 'consideration',
                             'address','grant_type', 'name'
                    ]
                elif dataset=='permits':
                    cols = ['loc_id', 'permit_type','year', 'date','permit',
                            'description', 'name','contractor', 
                            'permit_value', 'permit_fee','address'
                    ]
                elif dataset=='sales':
                    cols =  ['year','date','address','price',
                             'buyer','seller','sale_type',
                             'land_use','loc_id'
                    ]
                elif dataset=='business':
                    cols =  ['business_type','name','date','address',
                             'loan','forgiven',
                             'num1','num2','num3','num4','num5','num6',
                             'race','race2','race3','race4',
                             'fins','industry','address2','loc_id']
                    cols =  ['loc_id','address','name','BusinessType',
                             'industry',
                             'date','employees','loan','forgiven']
                elif dataset=='meetings':
                    cols =  ['loc_id','name','address','precinct']
                elif dataset=='water':
                    cols =  ['loc_id','address','name','account','date','amount','usage']
                elif dataset=='parcels':
                    cols = ['loc_id','address','name','building','land','assessed','land_use',
                            'zoning','year_built','decade','living_area','style','precinct']
                elif dataset=='energy':
                    if view == 'Power Plants':
                        cols = ['plant_code','technology',
                                'plant_name','utility_name',
                                'address','MW','generators']
                    if view == 'EV chargers':
                        cols = ['year','date','permit_type','permit',
                                'address','name','contractor','description',
                                'permit_value']
                    if view == 'Heat Pumps':
                        cols = ['year','received','date','total','occupants',
                                'footage','fuel','rebate','ac','heating_costs',
                                'outdoor_units','indoor_units','capacity',
                                'installer','backup','address','manufacturer',
                                'streetnum','streetname','streetsuffix','unit']
                    if view == 'Heat Pumps 2':
                        cols = ['year','date','permit',
                                'address','name','contractor','description',
                                'permit_value']
                    if view == 'Solar - Groups':
                        cols = ['address',
                                'year','date','watt','panels','inverters',
                                'efficiency','kwh','cost','permit_date',
                                'permit_values','owner','rps_type','entity',
                                'name','contractor','pts','rps_installer'
                                'rebate','srec','permits','description',
                                'pts_module_mfgr','pts_inverter_mfgr',
                                'pts_meter_mfgr']



                df = dict(zip(cols,customdata))

                string1 = ''
                address = df['address']
                if type(address)==list:
                    string1 = f"Address: {', '.join(address)}"
                    if len(address)>2:
                        string1=f'Address: {address[0]},{address[1]} and {len(address)-2} more addresses'
                else:
                    string1 = f"Address: {address}"

                        
                string2 = ''
                name = df['name'] if 'name' in cols else ''
                if type(name)==list:
                    string2 = f"Owner: {', '.join(name)}"
                    if len(name)>2:
                        string2=f'Owner: {name[0]},{name[1]} and {len(name)-2} more names'
                else:
                    string2 = f"Owner: {name}"

                string3 = ''
                if 'assessed' in cols:
                    assessed = df['assessed']
                    if type(assessed)==list:
                        try:
                            assessed = sum(assessed)
                        except:
                            assessed = None
                    string3 = f"Assessed: ${assessed:,.0f}"
                        
                if "description" in cols:
                    string3 = f"Desc: {df['description']}"
                if "consideration" in cols:
                    string3 = f"Consideration: ${df['consideration']:,.0f}"
                if "permit_value" in cols:
                    string3 = f"Permit Value: ${df['permit_value']:,.0f}"
                if "cost" in cols:
                    string3 = f"Cost: ${df['cost']:,.0f}"
                if "buyer" in cols:
                    string2 = f'Buyer: {df["buyer"]} Seller: {df["seller"]}'
                    string3 = f"Price: ${df['price']:,.0f}"
                if 'usage' in cols:
                    string3 = f"Usage: {df['usage']:,.0f} CCF - Amount: ${df['amount']:,.2f}"
                if 'loan' in cols:
                    string3 = f"Loan: ${df['loan']:,.0f} - Employees: {df['employees']}"

                string4 = ''
                if 'plant_name' in cols:
                    print(df)
                    string2 = string1
                    string1 = f"Plant: {df['plant_name']} - Utility: {df['utility_name']}"
                    string3 = f"{df['generators']} Generators - Capacity: {df['MW']:,.2f}MW"
                    string4 = f"Technology: {df['technology']}"
                children = [
                    html.Div([
                        html.P([
                            string1,
                            html.Br(),
                            string2,
                            html.Br(),
                            string3,
                            html.Br(),
                            string4
                        ],
                               style={"textAlign":"left","fontSize":"15px"}
                        ),
                    ])
                ]
                
                return True,  bbox, children
            else:
                return False, no_update, no_update


                
        return True,  bbox, children


    @app.callback(
        Output("people_modal", "is_open"),
        Output("people-modal-header", "children"),
        Output("people-modal-table", "children"),
        Output("people-modal-table", "style"),
        Input("graph-display", "clickData"),
        State('graph-display', 'figure'),   
        State("controls-radiobuttons-tabs", "value"),
        State("controls-radiobuttons-datasets", "value"),
        State("controls-date-slider", "value"),
        State("people-modal-table", "style"),
        State("people_modal", "is_open"),
        State("polis-data-store", "data"),
    )
    def toggle_people_modal(clickData, map_data,
                            tab, dataset, date, 
                            style, is_open, data):
        if tab != "maps":
            raise PreventUpdate
        if dataset not in ['elections','registered','residents']:
            raise PreventUpdate

        style['display']='none'

        # is it a click or hover event?
        ctx = callback_context

        if ctx.triggered[0]["prop_id"] == "graph-display.clickData":
            if clickData:
                cnum         =  clickData['points'][0]['curveNumber']
                pointNumber  =  clickData['points'][0]['pointNumber']

                df = DataFrame(map_data['data'][cnum]['customdata'])
                df = df[df.index==pointNumber]

                df.columns = ['loc_id','name','address','precinct',
                              'party','age']


                if len(df)>0:
                    explosive = [x for x in df.columns
                                 if type(df[x].iloc[0])==list]
                    if len(explosive)>0:
                        df = df.explode(explosive)
                        
                    table  = display_table(df)
                    style['display']='block'

                    ## date is incorrect on Group changes
                    date = to_datetime(
                        data['extra-params']['dates'][date]
                    )\
                    .strftime('%b. %-d, %Y')

                    people_modal_header = data['extra-params']['title']\
                        .split('[src]')[0]\
                        .format(
                            count=len(df),
                            date=date
                        )\
                        .replace('Voters','Voters at this address')\
                        .replace('Residents','Residents at this address')

            
                    return not is_open, people_modal_header, table, style

        return is_open, None, None, style


    def get_property_data(query):
        df  =  get_data_from_db ( query , db_connection )

        for col in df.columns:
            if list in df[col].apply(type).unique():
                df.drop(col,axis=1,inplace=True)
                
        for col in [x for x in df.columns
                    if x in list(int_value_pairs.item.unique())
        ]:
            df = merge_int_value ( df , int_value_pairs , col )

        return df
        
    
    
    @app.callback(
        Output("generic-modal-col1-row1", "children"),
        Output("generic-modal-col1-row2-image", "src"),
        Output("generic-modal-col2-row1", "children"),
        Input("generic-modal-selected-units", "value"),
        State("controls-radiobuttons-datasets", "value"),
        State("controls-date-slider", "value"),
        State("polis-data-store", "data"),
    )
    def update_from_selected_pid(pid,dataset,date,data):
        date = data['extra-params']['dates'][date]
        if type(date)!=int:
            date=2023
        if date<2018:
            date=2023

        query = """
        SELECT  a.pid, a.owner, a.land_use, a.style, a.land, a.total, 
        	a.year_built, a.rooms, a.units, a.living_area, a.area,
		room2.bedrooms, (p.interior->>'Full Baths') as baths,
                p.image
        FROM property.assessments a
        LEFT JOIN property.patriot p on p.year=2023 and p.pid=a.pid
        CROSS  JOIN LATERAL (
        SELECT 
			sum((COALESCE(obj))::int) AS bedrooms
        FROM   JSONB_ARRAY_ELEMENTS(p.rooms->'Bedrooms') obj
        ) room2
        WHERE a.year={date}
        AND a.pid = '{pid}'
        ;
        """.format(date=date,pid=pid)

        df = get_property_data ( query ) . iloc [ 0 ]
        col1_row1 = property_summary ( df )
        col1_row2 = f"https://arlington.patriotproperties.com/image/{df['image']}.JPG"


        chart_params = {
            'title' : """
            {col} history
            """,
            'color':'series',
            'XY':('date','value'),
            'traces_visible': [
                'building','land','total',
                'water_bill','ttm_water_bill',
                'daily_cost','ttm_daily_cost'
            ]
        }

        
        col2_row1 = []
        for col in ['permits','deeds_details','sales']:
            query = data['params']['property'][col.replace('_details','')]['tables']['detail']['query']\
                .replace('where','WHERE')
            idx = query.find('WHERE')
            query = query[:idx] + " where pid='{pid}' order by date desc". format(pid=pid)

            df = get_property_data ( query )

            if df is not None:
                if len(df)>0:
                    df = df.drop('address',axis=1)
                    col2_row1.append(display_pieces(col,display_table(df),dataset))

        for col in ['assessments','water','electric','gas','consumption']:
            if col == 'water':
                df = get_water_bill_history(pid, db_connection)
                
            elif col == 'assessments':
                df = get_assessment_history(pid, db_connection).rename(columns={'year':'date'})
            elif col in ['gas','electric']:
                df = get_utilities_history(pid, db_connection)
                df = df[df.service==col].drop('service',axis=1)

            elif col in ['consumption']:
                df = get_iotawatt_history(pid, db_connection)
                
            if df is not None:
                if len(df)>0:
                    if col == 'consumption':

                        chart_params["yaxis_range"]=[0,10]
                        chart_params['XY']=('timestamp','kWh')
                        chart_params['color']='series'

                        chart_fig = line_chart_simple(
                            df,
                            chart_params
                        )
                    else:
                        chart_fig = line_chart(df,chart_params,'dates')

                    chart = modal_charts(
                        chart_fig,
                        chart_params['title'].format(col=col.title())
                    )
                    
                    
                    col2_row1.append(display_pieces(col,chart,dataset))

        return col1_row1, col1_row2, col2_row1
    
    
    @app.callback(
        Output("generic-modal", "is_open"),
        Output("generic-modal-address", "children"),
        Output("generic-modal-selected-units", "options"),
        Output("generic-modal-selected-units", "value"),
        Output("generic-modal-units-container-style", "style"),
        Output("generic-modal-subheader", "children"),
        Input("graph-display", "clickData"),
        State("controls-radiobuttons-tabs", "value"),
        State("controls-radiobuttons-datasets", "value"),
        State("controls-date-slider", "value"),
        State("generic-modal-units-container-style", "style"),
        State("generic-modal", "is_open"),
        State("polis-data-store", "data"),
    )
    def toggle_generic_modal(clickData, 
                             tab, dataset, date,
                             selected_units_style,
                             is_open, data):
        if tab != "maps":
            raise PreventUpdate
        if dataset not in ['deeds','parcels','permits','sales','water']:
            raise PreventUpdate

        # is it a click or hover event?
        ctx = callback_context

        if ctx.triggered[0]["prop_id"] == "graph-display.clickData":
            if clickData:
                customdata = clickData['points'][0]['customdata']

                ##badness
                if dataset == "sales":
                    loc_id = customdata[-1]
                else:
                    loc_id = customdata[0]
                    
                pids    =  loc_pid[loc_pid.loc_id==loc_id].pid.to_list()

                ##strftime to %Y for water bills and year
                date = data['extra-params']['dates'][date]
                ##badness
                if type(date)==int:
                    if date<2018:
                        date = 2023

                if dataset!='water':
                    query = """
                    SELECT streetname,streetnum,unit,pid,owner 
                    FROM  property.assessments
                    WHERE pid in ({pids})
                    and year = {date}
                    ;
                    """.format(
                        #dataset=dataset if dataset!='parcels' else 'assessments',
                        pids=','.join(f"'{x}'" for x in pids),
                        date=date
                    )
                else:
                    query = """
                    SELECT streetname,streetnum,unit,pid,owner 
                    FROM  property.assessments
                    WHERE pid in ({pids})
                    and year = date_part('year',cast('{date}' as date))::INT 
                    ;
                    """.format(
                        pids=','.join(f"'{x}'" for x in pids),
                        date=date
                    )
                    
                try:
                    df = get_property_data(query)
                except:
                    try:
                        df = get_property_data(
                            query\
                            .replace('streetname','streetName')\
                            .replace('streetnum','streetNum'))
                    except:
                        print('Failed',query)
                
                subheader = ''

                address = (df.streetnum.fillna('') +\
                           ' ' + df.streetname.fillna('')
                ).unique()[0]
                selected_units = [] 
                selected_unit = pids[0]
                selected_units_style['display'] = 'none'

                if len(pids)>1:
                    unit2pid = dict(zip(df.unit.values,df.pid.values))
                    try: 
                        selected_units =\
                            [
                                {'label':x if x is not None else 0,
                                 'value':unit2pid[x]}
                                for x in sorted(list(unit2pid.keys()),
                                                key=natural_sort_key)
                                
                            ]
                    except:
                        selected_units =\
                            [
                                {
                                    'label': x  if x is not None else 0,
                                    'value': unit2pid[x]
                                }
                                for x in sorted(list(unit2pid.keys()))
                            ]
                        
                    selected_unit = selected_units[0]['value']
                    selected_units_style['display'] = 'block'
                
                return (
                    not is_open,
                    address,
                    selected_units, selected_unit, selected_units_style,
                    subheader,
                )
            
        return is_open, None, None, None, None, None

    @app.callback (
        #Address Search
        Output ("controls-address-search-container", "style"  ),
        Output ("controls-street-name-dropdown"    , "options"),
        Output ("controls-street-name-dropdown"    , "value"  ),
        Output ("controls-street-number-dropdown"  , "options"),
        Output ("controls-street-number-dropdown"  , "value"  ),
        Input  ("controls-radiobuttons-tabs"       , "value"  ),
        Input  ("controls-radiobuttons-views"      , "value"  ),
        Input  ("controls-street-name-dropdown"    , "value"  ),
        Input  ("controls-street-number-dropdown"  , "value"  ),
        State  ("controls-address-search-container", "style"  ),
    )
    def street_search_populate(tab, view, streetname, streetnum, style):
        if tab is None:
            raise PreventUpdate

        streetNames = list(street_search.streetName)
        if streetname=='' or streetname is None:
            streetname='MASS AVE'
        if streetname !='' and streetname is not None:
            mask = street_search.streetName==streetname
            streetNums = list(street_search[mask].iloc[0].streetNum)
            streetNums.sort(key=natural_sort_key)
        else:
            streetNums = None

        style['display']='none'
        if tab=='maps':
            if view!='state':
                style['display']='inline-block'
                return style, streetNames, streetname, streetNums, streetnum
        
        return  style, [], None, [], None

        
    @app.callback(
        Output('crossfilter-xaxis-column', 'options'),
        Output('crossfilter-yaxis-column', 'options'),
        Output('crossfilter-town--dropdown', 'options'),
        Output('crossfilter-town--dropdown', 'value'),

        Input('selected-ppt', 'value'),
        Input("controls-radiobuttons-views", "value"),
        State('polis-data-store', 'data'),
    )
    def update_scatter_layout_dropdowns(
            ppt, view, data
    ):
        #if ppt!='governance':
        #    raise PreventUpdate
        #if view!='scatter':
        #    raise PreventUpdate
        if data =={}:
            raise PreventUpdate

        return (
            sorted(data['dor_scatter_series']),
            sorted(data['dor_scatter_series']),
            data['municipalities'],
            'Arlington'
        )

        
    @app.callback(
        Output('crossfilter-indicator-scatter', 'figure'),
        Input('crossfilter-xaxis-column', 'value'),
        Input('crossfilter-yaxis-column', 'value'),
        Input('crossfilter-xaxis-type', 'value'),
        Input('crossfilter-yaxis-type', 'value'),
        Input("controls-date-slider", "value"),
        Input('crossfilter-town--dropdown', 'value'),
        State('selected-ppt', 'value'),
        State('controls-radiobuttons-views', 'value'),
        State('polis-data-store', 'data'),
    )
    def update_graph(xaxis_column_name, yaxis_column_name,
                     xaxis_type, yaxis_type,
                     year_value, municipality,
                     ppt, view,data):
        if ppt!='governance' or view!='DOR scatter':
            raise PreventUpdate
        if year_value is None:
            raise PreventUpdate

        year_value = data['params']['governance']['financials']['charts']['DOR scatter']['dates'][year_value]

        dff = dor_series [ (dor_series [ 'year' ] == year_value)]

        x = dff [ dff ['dor_databank_series'] == xaxis_column_name ]
        y = dff [ dff ['dor_databank_series'] == yaxis_column_name ]

        x =  x [ x.municipality.isin(y.municipality) ]
        y =  y [ y.municipality.isin(x.municipality) ]

        return scatter_chart(
            x,y,municipality,
            xaxis_column_name, yaxis_column_name,
            xaxis_type, yaxis_type
        )




    @app.callback(
        Output('x-time-series', 'figure'),
        Input('crossfilter-indicator-scatter', 'hoverData'),
        Input('crossfilter-xaxis-column', 'value'),
        Input('crossfilter-xaxis-type', 'value')
    )
    def update_y_timeseries(hoverData, xaxis_column_name, axis_type):       
        if 'customdata' not in hoverData['points'][0]:
            return no_update
        country_name = hoverData['points'][0]['customdata']

        dff = dor_series[dor_series['municipality'] == country_name]
        dff = dff[dff['dor_databank_series'] == xaxis_column_name]
        title = '<b>{}</b><br>{}'.format(country_name, xaxis_column_name)
        return create_time_series(dff, axis_type, title)


    @app.callback(
        Output('y-time-series', 'figure'),
        Input('crossfilter-indicator-scatter', 'hoverData'),
        Input('crossfilter-yaxis-column', 'value'),
        Input('crossfilter-yaxis-type', 'value')
    )
    def update_x_timeseries(hoverData, yaxis_column_name, axis_type):
        if 'customdata' not in hoverData['points'][0]:
            return no_update
        country_name = hoverData['points'][0]['customdata']
        dff = dor_series[dor_series['municipality'] == hoverData['points'][0]['customdata']]
        dff = dff[dff['dor_databank_series'] == yaxis_column_name]
        return create_time_series(dff, axis_type, yaxis_column_name)


    ##RECENT SALES
    
    @app.callback(
        Output('gallery-container', 'children'),
        Input('pagination', 'active_page'),
        Input('controls-radiobuttons-datasets','value'),
        Input('controls-radiobuttons-views','value'),
    )
    def recent_sales_update_page(current_page, dataset, view):
        if dataset!='sales':
            if view!='Recent':
                raise PreventUpdate
        
        if current_page:
            return recent_sales_generate_gallery(recent_sales, current_page)
        return  recent_sales_generate_gallery(recent_sales, 1)

    
    @app.callback(
        Output('recent-sales-modal', 'is_open'),
        Output('line1','children'),
        Output('line1a','children'),
        Output('line2','children'),
        Output('line2a','children'),
        Output('line3','children'),
        Output('line3a','children'),
        Output('rs-src', 'src'),       
        Input({"type": "image-card", "index": ALL}, 'n_clicks'),
        State('recent-sales-modal', 'is_open'),
        State('pagination', 'active_page'),
        prevent_initial_call=True
    )
    def toggle_recent_sales_modal(
            image_clicks,
            is_open,
            page_number
    ):

        if all(x is None for x in image_clicks):
            raise PreventUpdate
        
        ctx = callback_context

        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
        triggered_type = loads(triggered_id)["type"]
            
        if triggered_type == "image-card":
    
            if 'index' not in triggered_id:
                return False, None,  None, None, None, None, None, None
            
            page_size = 8  ##need to pass
            if page_number:
                s_idx = (page_number - 1) * page_size
            else:
                s_idx = 0

            e_idx = s_idx + page_size
                
                
            idx = loads(triggered_id)["index"]
            item = recent_sales[s_idx:e_idx][idx]
            line1, line1a,line2,line2a, line3,line3a = recent_sales_format_data(item)
            return not is_open, line1, line1a,line2,line2a, line3,line3a , item['img_url']

        return False, None,  None, None, None, None, None, None
