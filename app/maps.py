import pandas as pd
import plotly.express as px
from dash import dash_table

import textwrap

def mapbox_line (
        df : pd . DataFrame ,
        params : dict
) ->  px . line_mapbox:
    
    fig = px \
        .line_mapbox( df,
                      lat='lats',
                      lon='lons',
                      hover_data=df.columns,
                      color=params['color'],
                      category_orders  =  {
                          params['color']: list(df[params['color']].sort_values().unique()) } ,
                      mapbox_style="open-street-map",
                     height=700,
        )
    fig . update_traces  ( line = { "width":3 } )

    fig . update_layout  (
            mapbox  =  {
                "center" :  {
                    "lat" : params[ 'lat' ],
                    "lon" : params[ 'lon' ]
                },
                "zoom"   :  params[ 'zoom' ],
            },
            autosize  =  True,
            margin    = {"r":20,"t":25,"l":0,"b":0}
        )

    fig . for_each_trace (
        lambda trace : trace . update (  name = '<br>'.join(textwrap.wrap(trace.name, width=25))
        )
    )

    return fig



def mapbox_scatter (
        df : pd . DataFrame ,
        params : dict
) ->  px . scatter_mapbox:
    from os import environ

    MAPBOX_TOKEN  =  environ.get("MAPBOX_TOKEN", "")
    MAPBOX_STYLE  =  environ.get("MAPBOX_STYLE", "open-street-map")

    order = {
        params [ 'color' ] : list (
            df [params [ 'color' ] ] . sort_values ( ) .unique ( ) )
    }
    if params [ 'color' ] == 'precinct' :
        df [ 'precinct' ] = df [  'precinct' ] . astype ( str )
        order = {
            params [ 'color' ] : list (
                df [ 'precinct' ] \
                . astype ( int ) \
                . sort_values ( ) \
                . unique ( ) \
                . astype ( str )
            )
        }

    px . set_mapbox_access_token(MAPBOX_TOKEN)

    hover_data = [ x for x in df.columns
                   if x not in  ['geometry','lat','lon',
                                 'pid']
    ]
    cols = hover_data
    hover_data = dict(zip(hover_data,[True]*len(hover_data)))

    fig = px \
        . scatter_mapbox (
            df  ,
            lat     =  'lat' ,
            lon     =  'lon' ,
            color   =  params['color'] ,
            hover_data = hover_data,
            custom_data = cols,
            category_orders  =  order ,
            mapbox_style= MAPBOX_STYLE,
        ) \
        . update_traces  (
            marker = {
                "size" : 12,
                'allowoverlap':True,
                'opacity':0.85
            }
        ) \
        . update_layout  (
            mapbox  =  {
                "center" :  {
                    "lat" : params[ 'lat' ],
                    "lon" : params[ 'lon' ]
                },
                "zoom"   :  params[ 'zoom' ],
            },
            autosize  =  True,
            margin    = {"r":20,"t":25,"l":0,"b":0}
        )
    
    fig.update_traces(hoverinfo="none", hovertemplate=None)

    fig . for_each_trace (
        lambda trace : trace . update (
            name = '<br>'.join (
                textwrap.wrap (
                    trace.name, width=25
                )
            )
        )
    )
    
    #if 'traces_visible' in params:
    #    initial_traces_visible = params ['traces_visible']
    #    fig . for_each_trace (
    #        lambda trace : trace . update ( visible = "legendonly" ) if trace . name not in  initial_traces_visible  else ( ) ,
    #    )

    return fig

    
def mapbox_choropleth (
        df: pd . DataFrame,
        params: dict
) -> px.scatter_mapbox:
    
    from os import environ

    MAPBOX_TOKEN  =  environ.get("MAPBOX_TOKEN", "")
    MAPBOX_STYLE  =  environ.get("MAPBOX_STYLE", "open-street-map")

    if MAPBOX_TOKEN!="":
        px . set_mapbox_access_token(MAPBOX_TOKEN)
                           
    opacity=0.55
    custom_data=list(df.columns[~df.columns.isin(['geometry','lat','lon'])])

    geojson = df.__geo_interface__
    featureidkey = "properties.{key}".format(key=params["geometry_key"])


    fig = px \
        . choropleth_mapbox ( df ,
                              geojson      = geojson,
                              locations    = params["geometry_key"],
                              featureidkey = featureidkey,
                              color        = params['color'] ,
                              range_color  = params['range_color'],
                              color_continuous_scale =  "thermal",
                              mapbox_style           =  MAPBOX_STYLE,
                              hover_data=[x for x in df.columns
                                          if x not in ['struct_id','geometry','lat','lon']],
                              custom_data            =  custom_data ,
                              opacity                =  0.55
        ) \
        . update_layout  (
            hovermode = 'closest',
            mapbox  =  {
                "center" :  {
                    "lat" : params[ 'lat' ],
                    "lon" : params[ 'lon' ]
                },
                "zoom"   :  params[ 'zoom' ],
            },
            autosize  =  True,
            margin    = {"r":20,"t":25,"l":0,"b":0}
        )
    
    ## dev callback for hoverdata
    fig.update_traces(hoverinfo="none", hovertemplate=None)

    fig . for_each_trace (
        lambda trace : trace . update (
            name = '<br>'.join (
                textwrap.wrap (
                    trace.name, width=25
                )
            )
        )
    )
    
    return fig
                           
