import pandas as pd
import plotly.express as px
from dash import dash_table

def display_table (
        df : pd . DataFrame,
        data_dict : pd . DataFrame
) -> dash_table . DataTable :
    
    money       =  dash_table . FormatTemplate . money ( 0 )
    cash        =  dash_table . FormatTemplate . money ( 2 )
    percentage  =  dash_table . FormatTemplate . percentage ( 1 )
    precision   =  dash_table . Format . Format  ( precision=2, scheme=dash_table.Format.Scheme.fixed )

    ##omg fugly
    columns = []

    for col in ['eia_','rps_','pts_','bnl_','checkbook_']:
        df.columns = df.columns.str.replace(col,'')
    df.columns = df.columns.str.replace('_',' ')

    mask = data_dict.series.isin(list(df.columns))
    tmp = data_dict[mask].reset_index(drop=True).copy()

    hidden_columns = ['lat','lon','geometry','people id','LOC ID','loc id','pid','parcel','account']
    for col in df.columns:
        if col not in hidden_columns:
            dick = {'name':col.title(),'id':col}
        
            if col in list(tmp.series):
                format   = tmp.loc[tmp.series==col,'format'].iloc[0]
                if format=='date':
                    df[col] = pd.to_datetime(df[col],unit='s').dt.strftime('%Y-%m-%d')
            
                exponent = int(tmp.loc[tmp.series==col,'exponent'].iloc[0])
                if exponent>0:
                    df.loc[:,col]=df.loc[:,col]/pow(10,exponent)

                if format in ['float','money','cash','percentage']:
                    dick['type']='numeric'
                    dick['format']=precision if format=='float' else eval(format)
            
            columns.append(dick)
    

    table =  \
        dash_table . DataTable (
            df . to_dict ( 'records' ) ,
            columns = columns ,
            id = 'displayTable',           
            #virtualization =  True     ,
            editable       =  False     ,
            filter_action  =  "native" ,
            sort_action    =  "native" ,
            sort_mode      =  "multi"  ,
            page_action    =  "native" ,
            page_current   =  0        ,
            page_size      =  30       ,
            export_format  =  "xlsx"   ,
            fixed_rows={ 'headers': True, 'data': 0 },
            css=[{'selector':'.export',
                 'rule':'position:absolute;right:50px;top:-40px'
            }],
            merge_duplicate_headers = True ,
            style_data = {
                'color' : 'black' ,
                'backgroundColor' : 'white',
                'whiteSpace': 'normal',
                'height': 'auto',
            },
            style_data_conditional = [
                {
                    'if' : { 'row_index' : 'odd' } ,
                    'backgroundColor' : 'rgb(230, 230, 230)',
                },                
            ],
            style_header={
                'backgroundColor': 'rgb(210, 210, 210)',
                'color': 'black',
                'textAlign'  : 'center' ,
                'fontWeight' : 'bold',
            },
            style_table={'overflowX': 'auto',
                         'overflowY': 'auto',
                         'maxHeight':'95vh'},
            style_cell={
                'height': 'auto',
                # all three widths are needed
                'minWidth': '30px', 'width': '150px', 'maxWidth': '150px',
                'whiteSpace': 'normal'
            },
        )         
    return table


