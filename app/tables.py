import pandas as pd
import plotly.express as px
from dash import dash_table

def display_table ( df : pd . DataFrame ) -> dash_table . DataTable :
    money       =  dash_table . FormatTemplate . money ( 0 )
    cash        =  dash_table . FormatTemplate . money ( 2 )
    percentage  =  dash_table . FormatTemplate . percentage ( 1 )
    precision   =  dash_table . Format . Format  ( precision=2, scheme=dash_table.Format.Scheme.fixed )

    ##omg fugly
    columns = []
    
    df.columns=df.columns.str.replace('pts_','').str.replace('bnl_','').str.replace('checkbook_',' ').str.replace('_',' ')

    for col in df.columns[~df.columns.isin(['lat','lon','geometry','people id','LOC ID','loc id','pid','parcel','account'])]:
            
        if '#' in col:
            df[col]=df[col].fillna('0').astype(int)
            columns.append( {'name':col.title(),'id':col } )
        elif col == 'Date Certified':
            df[col] = pd.to_datetime(df[col],unit='s').dt.strftime('%Y-%m-%d')
            columns.append( {'name':col.title(),'id':col } )
        elif '%' in col:
            if col in ['CIP % of Total Value','R/O % of Total Value']:
                df[col]=df[col].fillna('0').astype(float)/10000
            #elif col in ['Debt Service as % of Budget']:
            #    df[col]=df[col].fillna('0').astype(float)                
            else:
                df[col]=df[col].fillna('0').astype(float)/100
            columns.append( {'name':col.title(),'id':col, 'type':'numeric', 'format':precision } )
        elif ' chg' in col:
            df[col]=df[col].fillna('0').astype(float)/100
            columns.append( {'name':col.title(),'id':col, 'type':'numeric', 'format':precision } )
        elif col in ['total kw installed','median kw installed']:
            df[col]=df[col].fillna('0').astype(float)
            columns.append( {'name':col.title(),'id':col, 'type':'numeric', 'format':precision } )
        elif col in ['efficiency']:
            df[col]=1.0*df[col].fillna('0').astype(float)
            columns.append( {'name':col.title(),'id':col, 'type':'numeric', 'format':precision } )
        elif col in ['Unemployment Rate','City/Town Accepted',
                     'DCR','Mass Highway','Total Miles','Unaccepted']:
            df[col]=df[col].fillna('0').astype(float)/100
            columns.append( {'name':col.title(),'id':col, 'type':'numeric', 'format':precision } )
        
        elif col in ['Lowest Residential Factor Allowed',
                'Max CIP Shift Allowed',
                'Residential Factor Selected','CIP Shift']:
            df[col]=df[col].fillna('0').astype(float)/1e6
            columns.append( {'name':col.title(),'id':col, 'type':'numeric', 'format':precision } )
        
        elif col in ['Average Single Family Value',
                     'DOR Income Per Capita',
                     'Single Famile Tax Bill*',
                     'Single Family Values',
                     'Education','Fire','Police','Culture and Recreation',
                     'Debt Service'
        ]:
            df[col]=df[col].fillna('0').astype(int)
            columns.append( {'name':col.title(),'id':col, 'type':'numeric', 'format':money } )
        elif df[col].dtype==object:
            columns.append( {'name':col.title(),'id':col } )
        else:
            if col not in ['check number',
                    'inverters','panels','panel watts',
                           'battery kw','battery kwh','kWh','kwh',
                    'Yes Votes','No Votes','W','est annual kwh','watt',
                    'kW','installs','MWh','MW','GWh','towns',
                    'mw installed','kw installed',
                    'Rank','Single Family Parcels','Moodys','S&P',
                    'cpi','price deflator','Population',
                    'Total Employees','Employed','Labor Force',
                    'Unemployed','','',
                    'Automobiles','Average Age','Heavy Trucks','Light Trucks',
                    'Luxury Vehicles','Motorcycles','Other','Total Vehicles',
                    'Trailers',
                    'All Other Registered Voters','Registered Democrat',
                    'Registered Republican','Total Registered Voters',
                    'ResidentBirths',
                    'fy','year','year built','count','CCF','deed types',
                            'permit','living area','area','acres','lot size','lotSize',
                            'usage','account','precinct','term',
                            'water usage','date',
                           'age','cards','lotsize','cards',
                           'amps','substation rating MVA',
                           'bulk substation voltage',
                           'bulk substation rating MVA',
                            'MVA','volts','bulk MVA',
                           'sections','segments',
                           'inverter quantity',
                           'module quantity',
                           'occupants','footage',
                            'indoor units','outdoor units',
                           'capacity','units','rooms',
                            'JobsReported','NAICSCode','employees',
                            'loan number','naics','book','page',
                            'docno','pages','registered',
                            'students',
                            'Total In-district FTEs','Total Pupil FTEs',
                            'PK','K','1','2','3','4','5','6','7','8','9','10','11','12','SP','Total',
                            'FTE Count',
                            'No. of Students Included',
                            'Avg. Scaled Score',
                            'Avg. SGP',
                            'Included In Avg. SGP',
                            'Avg.SGP',
                            'Included In Avg.SGP',
                            'Median SGP','Included In Median SGP','Ach. PCTL'
                            
            ] :
                columns.append( {'name':col.title(),'id':col, 'type':'numeric', 'format':money if col not in ['amount','water bill','cost per watt'] else cash } )
            else:
                columns.append( {'name':col.title(),'id':col } )

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


