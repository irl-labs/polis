import pandas as pd
import plotly.express as px
import textwrap
from numpy import minimum, maximum

def boxplot ( df : pd . DataFrame , params : dict  ) -> px . box :
    fig = px . box ( df,
                     x = params [ 'x' ] ,
                     y = params [ 'y' ] ,
                     color = params [ 'color' ] ,
                     category_orders  =  { params['color']: list(df[params['color']].sort_values().unique()) } ,                                      
                     hover_data = params [ "hover_data" ],
                     points = "all"
    )
    
    fig.update_layout(
        #             title={'text': params['title'],'font':{'size':20}},
        yaxis_tickprefix = '$',
        xaxis_title="Year",
        yaxis_range=params['y_range'],
        yaxis_title=params['y'],
        legend_title=params["color"],
        autosize  =  True,
        margin    = {"r":20,"t":25,"l":0,"b":0},
        font=dict(
            #family="Courier New, monospace",
            family="Roboto",
            size=16,  # Set the font size here
            color="Black"
        )
    )

    if 'traces_visible' in params:

        initial_traces_visible = params['traces_visible']
        if len(initial_traces_visible) != 0:
            fig . for_each_trace (
                lambda trace : trace . update ( visible = "legendonly" )
                if trace . name not in  initial_traces_visible  else ( )
            )

    ##wrap trace names for graph-display size consistency
    fig . for_each_trace (
        lambda trace : trace . update (
            name = '<br>'.join(textwrap.wrap(trace.name, width=25))
        )
    )

    return fig


def line_chart_simple (
        df : pd . DataFrame ,
        params : dict
) -> px . line :

    if 'color' in params:
        fig = px.line (
            df ,
            x=params['XY'][0], 
            y=params['XY'][1],
            color= params['color'],
            category_orders  =  {
                params['color']: list(df[params['color']].sort_values().unique())
            }
        )
    else:
        fig = px.line (
            df ,
            x=params['XY'][0], 
            y=params['XY'][1]
        )

    fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1d", step="day", stepmode="backward"),
                dict(count=7, label="1w", step="day", stepmode="backward"),
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=1, label="YTD", step="year", stepmode="todate"),
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(step="all")
            ])
        )
    )

    ## provide room at top of graph-display for dash figure toolbar
    fig.update_layout(
        autosize  =  True,
        margin    = {"r":20,"t":25,"l":0,"b":0},
        yaxis_range = params["yaxis_range"]
    )
    
    return fig


def line_chart (
        df : pd . DataFrame ,
        params : dict,
        item : str
) -> px . line :
          
    fig = px.line (
        df ,

        x=params['XY'][0], 
        y=params['XY'][1] if params['XY'][1]!='item' else item,
        
        color= params['color'],
        markers=True,
        category_orders  =  {
            params['color']: list(df[params['color']].sort_values().unique())
        }
    )

    ##grey out all traces except params traces_visible
    if 'traces_visible' in params:
        initial_traces_visible = params['traces_visible']
        if len(initial_traces_visible) != 0:
            fig . for_each_trace (
                lambda trace : trace . update ( visible = "legendonly" )
                if trace . name not in  initial_traces_visible  else ( ) ,
            )

    ## provide room at top of graph-display for dash figure toolbar
    fig.update_layout(  autosize  =  True,
                        margin    = {"r":20,"t":25,"l":0,"b":0},
                        font=dict(
                            #family="Courier New, monospace",
                            family="Roboto",
                            size=16,  # Set the font size here
                            color="Black"
                        )
    )

    ##wrap trace names for graph-display size consistency
    fig . for_each_trace (
        lambda trace : trace . update (
            name = '<br>'.join(textwrap.wrap(trace.name, width=25))
        )
    )
    
    fig.update_traces(
        line=dict(width=3),
        marker=dict(
            size=12,
            line=dict(
                width=2,
                color='DarkSlateGrey')
        )
        #selector=dict(mode='markers')
    )
    
    return fig


def histogram ( df : pd . DataFrame , params : dict  ) -> px . histogram :
    order = {
        params [ 'color' ] : list (
            df [params [ 'color' ] ] . sort_values ( ) .unique ( ) )
    }
    minimum_value=params['range_x'][0]
    maximum_value=params['range_x'][1]
    if ('_chg_' in params['x'] or
        params['x'] in
        ['amps','left_sidewalk', 'right_sidewalk']
    ):
        minimum_value=params['range2_x'][0]
        maximum_value=params['range2_x'][1]
            
    df[params['x']] = [minimum(maximum_value, num)
                       for num in df[params['x']]]
    df[params['x']] = [maximum(minimum_value, num)
                       for num in df[params['x']]]
            
    if 'y' in params:
        
        if params['color'] == 'date':
            params['traces_visible'] = [df.date.sort_values().unique()[-1].strftime('%Y-%m-%d')]
        
        fig = px . histogram ( df ,
                                x          =  params['x'],
                                y          =  params['y'], 
                                color      =  params['color'],
                                nbins      =  100, 
                                barmode    =  params['barmode'],
                                category_orders  =  order ,
                                range_x    =  params['range_x'],
        )
    else:
        fig = px . histogram ( df ,
                                x          =  params['x'],
                                color      =  params['color'],
                                category_orders  =  order ,
                                nbins      =  100,#params['nbins'], 
                                barmode    =  params['barmode'],
                                #range_x    =  params['range_x'],
                              
        )


    #fig . update_traces (
    #    xbins = dict (size=params['xbins_size']))

    def adjust_histogram_data(xaxis, xrange):
        x_values_subset = x_values[np.logical_and(xrange[0] <= x_values,
                                                  x_values <= xrange[1])]
        fig.data[1].x = x_values_subset

        
    fig.layout.xaxis.on_change(adjust_histogram_data, 'range')

    #fig.layout.legend.entrywidth=10

    if 'traces_visible' in params:
        initial_traces_visible = params['traces_visible']
        if len(initial_traces_visible) != 0:
            fig . for_each_trace (
                lambda trace : trace . update ( visible = "legendonly" )
                if trace . name not in  initial_traces_visible  else ( )
            )

    if 'annotate' in params:
        series_metrices = []
        series_colors = []
        fig . for_each_trace (
            lambda trace : series_metrices.append(trace.name) if trace.visible is None else ()
            
        )
        fig . for_each_trace (
            lambda trace : series_colors.append(trace.marker['color']) if trace.visible is None else ()
            
        )
        idx = 0
        for series_metric in series_metrices:
            mask = (df.dor=='Arlington')&(df.dor_databank_series==series_metric)
            zscore = df[mask].zscore.iloc[-1]
            fig.add_annotation(x=zscore,y=0,
                               text=df[mask].dor.values[0] + ' ' + str(round(zscore,2)),
                               font={'color':'black','size':20},
                               #font={'color':series_colors[idx],'size':15},
                               showarrow=True,arrowhead=2)
            idx+=1

    fig.update_layout (
        autosize  =  True,
        margin    = {"r":20,"t":25,"l":0,"b":0},
        font=dict(
            #family="Courier New, monospace",
            family="Roboto",
            size=16,  # Set the font size here
            color="Black"
        )
    )
    
    fig . for_each_trace (
        lambda trace : trace . update (
            name = '<br>'.join(textwrap.wrap(trace.name, width=25)
            )
        )
    )
    
        
    return fig


import plotly.graph_objects as go

def scatter_chart ( x : pd . DataFrame , y : pd . DataFrame, 
                   municipality : str,
                   xaxis_column_name : str ,
                   yaxis_column_name : str ,
                   xaxis_type : str,
                   yaxis_type : str
                  ) -> px . scatter :
    fig = px . scatter (
        x = x [ 'value' ] ,
        y = y [ 'value' ] ,
        hover_name = y [ 'municipality' ]
    )
    
    fig.update_traces(customdata=y['municipality'])
    
    x1 = x[x.municipality==municipality]['value'].values
    y1 = y[y.municipality==municipality]['value'].values
    
    ##need to add customdata to star marker for timeseries to trigger on hoverData
    
    #fig.update_layout(showlegend=False,height=600)
    fig.update_traces(
        line=dict(width=3),
        marker=dict(
            size=12,
            line=dict(
                width=2,
                color='DarkSlateGrey')
        )
    )

    fig.add_trace(go.Scatter(x=x1, y=y1, mode = 'markers',
                             marker_symbol = 'star',
                             marker_size = 20))
    
    fig.update_xaxes(title=xaxis_column_name, type='linear' if xaxis_type == 'Linear' else 'log')
    
    fig.update_yaxes(title=yaxis_column_name, type='linear' if yaxis_type == 'Linear' else 'log')
    
    fig.update_layout(
        showlegend=False,
        height=600,
        margin    = {"r":20,"t":25,"l":0,"b":0},
        hovermode='closest',
        font=dict(
            family="Roboto",
            size=16,  # Set the font size here
            color="Black"
        )
    )
    
    return fig




def create_time_series(dff, axis_type, title):
    
    fig = px.scatter(dff, x='year', y='value')
    
    fig.update_traces(mode='lines+markers')

    fig.update_traces(
        line=dict(width=3),
        marker=dict(
            size=12,
            line=dict(
                width=2,
                color='DarkSlateGrey')
        )
    )
    
    fig.update_xaxes(showgrid=False)
    
    fig.update_yaxes(type='linear' if axis_type == 'Linear' else 'log')
    
    fig.add_annotation(x=0, y=0.85, xanchor='left', yanchor='bottom',
                       xref='paper', yref='paper', showarrow=False, align='left',
                       text=title)
    
    fig.update_layout(
        #height=225,
        height=300,
        margin={'l': 20, 'b': 30, 'r': 10, 't': 10}        
    )
    
    return fig

