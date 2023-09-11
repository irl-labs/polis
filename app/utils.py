from pandas     import read_sql_query, DataFrame, unique
from geopandas  import GeoDataFrame, read_postgis
from sqlalchemy import create_engine

"""
Database 

1. connections
2. queries returning dataframe, geo_dataframe
3. parameters dictionary

"""

def get_db_connection ( dbname = 'ArlingtonMA' ) -> create_engine :

    from dotenv import load_dotenv, find_dotenv
    
    _ = load_dotenv (
        find_dotenv (
            usecwd = True
        ),
        override = True
    )

    from os import environ

    user     =  environ.get("POSTGRES_USERNAME", "postgres")
    pw       =  environ.get("POSTGRES_PASSWORD", "postgres")
    host     =  environ.get("POSTGRES_IPADDRESS", "localhost")
    port     =  environ.get("POSTGRES_PORT", "5432")

    return create_engine(f'postgresql://{user}:{pw}@{host}:{port}/{dbname}')


def get_params ( db_connection : create_engine ) -> dict :
    query = "select dict from common.parameters where parameter_type=1"

    return db_connection . execute ( query ) . fetchall ( ) [ 0 ] [ 0 ]


def get_data_from_db (
        query : str ,
        db_connection : create_engine
) -> DataFrame :
    # postgis 
    if 'geometry' in query:
        return read_postgis ( query,
                              geom_col='geometry',
                              con = db_connection
        )
    
    return read_sql_query ( query , db_connection )




""" 
(ref)[https://stackoverflow.com/questions/579310/formatting-long-numbers-as-strings]
"""
def human_format(num):
    num = float('{:.3g}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '${}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])


## sort key for mixed alphanumeric address numbers
import re
_nsre = re.compile('([0-9]+)')
def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split(_nsre, s)]   



def format_date_slider (
        params : dict,
        group : str,
        current_date,
        db_connection : create_engine
) :
    ##seems like a lot of work for dates; needs rethink

    ##dates from db query where the query_dates has a variable parameter 
    if 'query_dates' in params :
        
        if '{item}' in params [ 'query_dates' ] :
            
            dates = read_sql_query (
                params [ 'query_dates' ] . format ( item = group ),
                db_connection
            ) [ 'dates' ] . to_list ( )
            
            params [ 'dates' ] =\
                [ x if type ( x ) == int
                  else x . strftime ( '%Y-%m-%d' ) for x in dates ]
    
    marks = {}
    dates = [0]
    date_idx = -1
    
    if 'dates' in params:

        slider_container_style  =  {
            'display':'block','width': '60%',
            'padding': '10px 20px 40px 20px'
        }

        dates = list ( range ( len ( params [ 'dates' ]  ) ) )
        
        if current_date not in params [ 'dates' ] :
            current_date = params [ 'dates' ] [ -1 ]
        date_idx = params [ 'dates' ] . index ( current_date )  

        marks = {
            i : {
                'label': str(x), 
                'style': {"transform": "rotate(45deg)", 'marginTop': 10}
            } for i , x in enumerate ( params['dates'] )
        }

        ## display only every third mark (and last mark) to avoid bunching
        if len(marks)>20:
            marks = {
                k : marks [ k ] for k in marks . keys ( )
                    if k in list ( range ( 0 , len ( marks ) , 3 ) ) +
                [ list ( marks . keys ( ) ) [ -1 ] ]
            }

        return dates, date_idx, marks
    

## df aggregate multiple pids by loc_id
def df_aggregate (
        df : DataFrame
) -> DataFrame :
    return df

def aggregate_people(df):
    df = df.groupby('loc_id').agg({
        'name':list,
        'address':list,
        'precinct':'last',
        'party':list,
        'age':list
    }).reset_index()
    
    df['precinct']=df['precinct'].astype(str)

    return df

def aggregate_deeds(df, color='year'):

    if color=='year':
        cols = ['deed_type', 'date', 'book', 'page', 'docno', 'consideration',
                'address','grant_type', 'name', 'pid']
        df.year=df.year.astype(str)
    elif color=='deed_type':
        cols = ['year', 'date', 'book', 'page', 'docno', 'consideration',
                'address','grant_type', 'name', 'pid']
    else:
        return None

    ##exploding dataset then aggregating is stupid
    agg = dict(zip(cols,['last']*len(cols)))
    for col in ['grant_type','name']:
        agg[col]=list

    df = df[['loc_id',color]+cols].groupby(['loc_id',color]).agg(agg)

    return df.reset_index()

def aggregate_permits(df):

    cols = ['year','date', 'permit',
            'description', 'owner','contractor', 
            'permit_value', 'permit_fee','address']
    agg = dict(zip(cols,['last']*len(cols)))
    df = df[['loc_id','permit_type']+cols].groupby(['loc_id','permit_type']).agg(agg)

    return df.reset_index()

def aggregate_parcels(df):
    from pandas import concat
    mask = df.loc_id.duplicated(keep=False)

    df['address']=\
        (df['streetnum'] .fillna('')+ ' '+\
        df['streetname'].fillna('')+ ' '+\
        df['unit']      .fillna(''))\
    . str . strip ( ) . replace ( { ' +' : ' ' } , regex = True )
    
    cols = ['pid','address','owner','building', 'land', 'other', 'total',
           'area', 'last_sale_date', 'last_sale_price', 'land_use', 
           'zoning', 'year_built','decade_built',
           'building_area', 'units', 'living_area', 'style', 'rooms',
            'year','streetname','streetnum','unit','mbta']

    agg = dict(zip(cols,[list]*len(cols)))
    for col in [ 'zoning','area','style','land_use','decade_built',
                 'streetname','streetnum','unit','mbta']:
        agg[col]='last'

    multi = df[mask][cols+['loc_id']].groupby('loc_id').agg (agg).reset_index()

    multi = concat([multi,df[~mask][cols+['loc_id']]],ignore_index=True).reset_index(drop=True)
    multi = multi\
        . sort_values(['streetname','streetnum','unit'])\
        . reset_index(drop=True)\
        . drop(['streetname','streetnum','unit'],axis=1)

    cols = ['loc_id','pid','address','owner','building', 'land', 'total',
            'land_use','zoning', 'year_built','decade_built',
            'building_area', 'units', 'living_area', 'style', 'rooms','mbta']


    return multi[cols]


def aggregate_water(df):
    df = df.groupby('loc_id').agg({
        'address':list,
        'owner':list,
        'account':list,
        'date':'last',
        'amount':sum,
        'usage':sum
    }).reset_index()
    
    return df

def aggregate_business(df):
    df = df.groupby('loc_id').agg({
        'address':'last',
        'business':'last',
        'BusinessType':'last',
        'industry':'last',
        'date':'last',
        'employees':'last',
        'total':sum,
        'forgiven':sum
    }).reset_index()
    
    return df

def aggregate_tmm(df):
    df = df.groupby('loc_id').agg({
        'name':list,
        'address':list,
        'precinct':'last'
    }).reset_index()
    
    df['precinct']=df['precinct'].astype(str)

    return df


def df_maps (
        dataset : str,
        group : str,
        df : DataFrame,
        loc_pid : DataFrame,
        loc_polygons : DataFrame
) -> GeoDataFrame:
    gdf = df . merge ( loc_pid, on ='pid', how='left' )


    #gdf = df_aggregate ( gdf )
    if dataset == 'deeds':
        gdf = aggregate_deeds(gdf, group)
    elif dataset == 'permits':
        gdf = aggregate_permits(gdf)
    elif dataset == 'parcels':
        gdf = aggregate_parcels(gdf)
    elif dataset == 'water':
        gdf = aggregate_water(gdf)
    elif dataset == 'meetings':
        gdf = aggregate_tmm(gdf)
    elif dataset == 'business':
        gdf = aggregate_business(gdf)
    elif dataset in ['elections','registered','residents']:
        gdf = aggregate_people(gdf)

    if 'loc_id' in gdf.columns:

        gdf  =  GeoDataFrame (
            gdf . merge (
                loc_polygons,
                on='loc_id',
                how='left'
            ),
            geometry = 'geometry'
        )
        
    return gdf

    
## df transforms
def df_transform (
        df : DataFrame,
        ppt : str , dataset : str, tab : str, view : str, group : str, date,
        int_value_pairs   : DataFrame,
        people_attributes : DataFrame,
        addresses         : DataFrame
) -> DataFrame :

    if ppt == 'people':
        if (view != 'summary'):
            if (tab != 'charts'):
                df = people_expand ( df,
                                     people_attributes ,
                                     addresses,
                                     date)

    for col in [x for x in df.columns
                if x in list(int_value_pairs.item.unique())]:
        df = merge_int_value(df,int_value_pairs,col)

    if dataset=='schools':
        if view in ['summary']:
            df = df_pivot(df,view)

    if dataset=='financials':
        if view=='DOR':
            df = df_pivot(df,dataset)

    explosive = [x for x in df.columns
                 if type(df[x].iloc[0])==list]
    if len(explosive)>0:
        df = df.explode(explosive)

    if dataset=='business':
        explosive = [x for x in df.columns
                     if type(df[x].iloc[0])==list]
        if len(explosive)>0:
            df = df.explode(explosive)

    ## for display purposes
    df.columns = df . columns \
                    . str . replace ( 'bnl_' , '' )#\
                    #. str . replace ( 'pts_' , '' )\
                    #. str . replace ( 'checkbook_' , '' )

    return df
 

def merge_int_value (
        df : DataFrame ,
        int_value_pairs : DataFrame ,
        col : str
) -> DataFrame :

    def replace_grant_types(alist):
        return [str(x).replace('0','Grantee').replace('1','Grantor')
                for x in alist]

    if col == 'grant_type':
        df.grant_type=df.grant_type.apply(replace_grant_types)
        return  df
    
    orig_column_order = df.columns
    
    tmp = df\
        . merge(
            int_value_pairs[int_value_pairs.item==col][['key','value']],
            how      = 'left',
            right_on = 'key',
            left_on  = col
        )\
        . drop(
            [ 'key' , col ] , axis = 1
        )

    if 'value_y' in tmp.columns:
        tmp = tmp . rename(columns={'value_y':col,'value_x':'value'})
    else:
        tmp = tmp . rename(columns={'value':col})
        
    return tmp[orig_column_order]


def people_expand (
        peeps : DataFrame,
        attributes : DataFrame,
        addresses : DataFrame,
        date
) ->  DataFrame :
    from pandas import to_datetime, concat, isnull
    from numpy import timedelta64
    
    date = to_datetime(date).date()

    df = peeps.merge(attributes,how='left',on='people_id')

    ##tricksie
    for col in ['name','address_id','party','precinct']:
        df = df.explode([col,'date_'+col])

        mask = df['date_'+col]<= date
        a = df [  mask ] [ ~df [ mask ] . duplicated ( ['people_id'] , keep = 'last')]
        b = df [ ~mask ] [ ~df [ ~mask] . duplicated ( ['people_id'] , keep = 'first')]
        df = concat ( [ a , b [ ~b . people_id . isin ( a . people_id ) ] ] )
        
    df = df\
        . merge(addresses,on='address_id',how='left')\
        . replace({isnull:'',None:''})\
        . sort_values(['precinct','streetName','streetNum','unit'])
                      #key=natural_sort_key)

    ##needs work
    df [ 'address' ]  =  (\
                df [ 'streetNum'    ]  .map ( str , na_action = 'ignore' )  + ' ' +\
                df [ 'streetSuffix' ]  .map ( str , na_action = 'ignore' )  + ' ' +\
                df [ 'streetName'   ]  .map ( str , na_action = 'ignore' )  + ' ' +\
                df [ 'unit'         ]  .map ( str , na_action = 'ignore' )
                       ) . str . strip ( ) . replace ( { ' +' : ' ' } , regex = True )

    df [ 'age' ]  =  round(((to_datetime(date)-to_datetime(df['dob']))/ timedelta64(1, 'Y')),0).astype(float).fillna(0).astype(int)
    
    cols = ['name','address','precinct','party','sex', 'age', 'people_id','pid']
        
    return df[cols]


def get_dor_scatter_series(params, int_value_pairs, db_connection):
    df = get_data_from_db (
        params['governance']['financials']['charts']['DOR scatter']['query'],
        db_connection
    )

    for col in [x for x in df.columns
                if x in list(int_value_pairs.item.unique())]:
        df = merge_int_value(df,int_value_pairs,col)

    return df.rename(columns={'dor':'municipality'})



def df_pivot (
        df : DataFrame,
        category : str
) ->  DataFrame :

    if category == 'summary' :
        if df.columns[2]=='mcas_subject':
            index   =  [ 'school_id' , 'year','mcas_subject','mcas_grade']
            columns =  [ df.columns[4] ]
        else:
            index   =  [ 'school_id' , 'year' ]
            columns =  [ df.columns[2] ]
    elif category == 'mcas' :
        index   =  [ 'school_id', 'year', 'mcas_subject','mcas_grade' ]
        columns =  [ 'mcas' ]
    elif category == 'financials' :
        index   =  [ 'year' ]
        columns =  [ 'dor_databank_series' ]
    else :
        index   =  [ 'year' ]
        columns =  [ category ]

    df = df . pivot(columns =  columns,
                    values  =  [ 'value' ],
                    index   =  index )\
            . reset_index ( )


    df.columns = df . columns . get_level_values ( 1 )
    df.columns = index + list ( df . columns [ len ( index ) : ] )
    df = df \
        . sort_values ( [ 'year' ], ascending = False )\
        . reset_index ( drop = True )

    ## s/b replaced
    if columns == [ 'grade' ] :
        df = df [
            [
                'school_id','year',
                'Total','PK','K',
                '1','2','3','4','5',
                '6','7','8',
                '9','10','11','12',
                'SP'
            ]
        ]
        
    return df


def get_title ( df, specific_params,
                town, ppt, dataset, tab, view,
                group, metric,
                series_type, series, date
):
    from pandas import to_datetime
    
    if 'title' not in specific_params :
        return ""
    
    stats = {'count':0, 'groups':0, 'cats':0, 'total':0}
    
    stats [ 'count' ] = len ( df )
    stats [ 'total' ] = len ( df.columns ) - 1
    
    #if ppt != 'people':
    if 'color' in specific_params:
        stats [ 'groups' ] =len (
            df [ specific_params [ 'color' ] ] . unique ()
        )

        
    if 'watt' in df.columns:
        stats['cats'] = round (
            df . watt . fillna ( '0' ) . astype ( float ) . sum ( ) / 1e6 ,
            2
        )
            
    for col in ['total','permit_value','price','cost','amount',
                'assessed','consideration',
                'segments','sections']:
        if col in df.columns:
            stats['total'] = df [ col ] \
                . fillna ( '0' ) \
                . astype ( float ) \
                . sum ( ) \
                . astype ( int )
            
            
    if type(date)!=int:
        if date is not None:
            date = to_datetime(date).strftime('%b. %-d, %Y')
            
    title = specific_params['title']\
        . format (
            town  = town,
            ppt = ppt.title(),
            dataset = dataset.title(),
            series = series_type,
            metric = metric,
            series_metric = series,
            date  = date,
            trace = group if group is None else group.replace('-',' ').title(),
            groups = f'{stats["groups"]:,d}',
            count = f'{stats["count"]:,d}',
            cats =  f'{stats["cats"]:,.2f}',
            total = human_format(stats['total']) \
            if dataset not in ['roads','grid','schools']
            and view not in ['DOR']
            else stats['total']
        )
    
    if ' election' in title:
        if dataset == 'elections':
            if view != 'line':
                if group is not None:
                    title = title . replace(
                        ' election',
                        ' ' + group + ' election'
                    )

    title = title.replace('checkbook_','')

    return title


## sort of a mess
def series_type_2_series(ivp,series_type):
    mask = (ivp['item'] == 'dor_databank_series_type')&\
        (ivp['value']==series_type)
    
    return list(ivp[mask].merge(
        ivp[ivp['item'] == 'dor_databank_series_types'],
        left_on=['value'],
        right_on=['value'],
        suffixes=('', '_right'),
        how='left'
    ).merge(
        ivp[ivp.item=='dor_databank_series'],
        on='key',
        suffixes=('_left',''),
        how='left'
    )['value'])



#############  SOLAR  ##################
def b64image(png):
    from PIL import Image
    import io
    import base64
    
    b = io.BytesIO()
    try:
        im = Image.open(png)
        im.save(b, format="PNG")
        b64 = base64.b64encode(b.getvalue())
        return b64.decode("utf-8")
    except:
        return None


def get_ivp(db_connection):
    query = """
                select * 
                from common.int_value_pairs 
                where 
                    item like 'rps_%%' 
                or 
                    item like 'bnl_%%' 
                or 
                    item like 'pts_%%'
                or
                    item in ('BIPV','bifacial','technology')
            """
    int_value_pairs = read_sql_query(query,db_connection)\
        .replace({'bnl_module_model':'model',
                  'bnl_module_manufacturer':'manufacturer',
                  'bnl_technology_module':'technology'})
    
    return int_value_pairs.groupby('item')[['key','value']]\
           .apply(lambda x: x.set_index('key').to_dict()['value'])\
           .to_dict()


def update_keys_with_values(x,lookup_dict) :
    if x is None:
        return None
    for kitem in x.keys():
        value = x[kitem]
        if type(value)==list:
            for idx in range(len(value)):
                if type(value[idx])==dict:
                    for kitem2 in value[idx].keys():
                        if kitem2 in lookup_dict.keys():
                            x[kitem][idx][kitem2] = lookup_dict[kitem2][value[idx][kitem2]]
                else:
                    if kitem in lookup_dict.keys():
                        value[idx] = lookup_dict[kitem][value[idx]]
        else:
            if kitem in list(lookup_dict.keys()):
                x[kitem] = lookup_dict[kitem][value]
    
    
    return x


def get_solar_data(db_connection):

    from geopandas import read_postgis

    query = """
    select ss.struct_id,pp.address,pp.owner->>'owner1' as owner,
    pp.image,modules.panels as panels, s.*,ss.geometry
    from energy.solar s 
    left join common.structures ss on ss.pid = s.pid 
    and ss."area"=(select max(z."area") from common.structures z where z.pid=s.pid)
    left join property.patriot pp on pp.pid = s.pid
    CROSS  JOIN LATERAL (
    SELECT 
    sum((COALESCE(obj ->> 'quantity'))::int) AS panels
    FROM   JSONB_ARRAY_ELEMENTS(watts->'modules') obj
    ) modules
    where s.pid is not null 
    ORDER BY struct_id
    ;
    """
    df = read_postgis(query,geom_col='geometry',con=db_connection)
    
    df = df[~df.duplicated(['pid','date','watt','cost'],keep='first')].reset_index(drop=True)
    
    
    df = df[['pid','struct_id','address', 'owner','image','panels','date','watt','cost','watts','financials','entity','joules','amps','geometry']].copy()
    
    df['roof_image']='./images/'+df['struct_id']+'.png'

    df['house_image']='https://arlington.patriotproperties.com/image/'+df['image']+'.JPG'
    
    df = df.set_geometry('geometry')
    df = df.set_crs(df.crs)
    df = df.to_crs(4326)


    lookup_dict = get_ivp(db_connection)

    for d in ['financials', 'entity','amps', 'watts', 'joules']:
        df[d].apply(update_keys_with_values,lookup_dict=lookup_dict)

    return df


def get_solar_production(pid, db_connection):

    query = """
    select timestamp,kwh
    from energy.solar_production
    where pid='{pid}'
    order by timestamp
    """

    return read_sql_query(query.format(pid=pid),db_connection)

########### SINGLE PROPERTY

def get_water_bill_history(pid, db_connection):
    from pandas import concat, isnull

    query = """
        select w.date,w.usage as water_usage,w.amount as water_bill
        from infrastructure.water_bills w
        left join infrastructure.water_accounts a on a.account=w.account
        and a.date = (select max(z.date) from infrastructure.water_accounts z 
                        where z.account=w.account)
        where a.pid='{pid}'
        order by w.date desc
    """
    df = read_sql_query(query.format(pid=pid),db_connection)
    df = df.melt(['date'],var_name='series').sort_values(['series','date']).reset_index(drop=True)
    
    tmp = df.groupby(['series']).rolling(4, min_periods=4, on='date')['value'].mean().reset_index()
    tmp = tmp[~isnull(tmp.value)]
    tmp.series='ttm_'+tmp.series

    return concat([df,tmp])

def get_iotawatt_history(pid, db_connection):
    from pandas import concat, isnull
    query = """
                select * from energy.ohms

                WHERE pid='{pid}' ORDER by timestamp;
            """
    df = read_sql_query(query.format(pid=pid),db_connection)
    df = df.melt(['pid','timestamp'],var_name='series',value_name="kWh")

    return df[df.kWh>0]
    


def get_utilities_history(pid, db_connection):
    from pandas import concat, isnull
    
    query = """
    select 'electric' as service,
    date, kwh as usage,
    round((kwh*generation)::numeric,2) as supply,
    round((kwh*delivery+customer_charge)::numeric,2) as delivery,
    round((kwh*generation + kwh*delivery+customer_charge)::numeric,2) as total,
    round(((kwh::numeric)/(days::numeric))::numeric,1) as daily_usage,
    round(((kwh*generation + kwh*delivery+customer_charge)/(days::numeric))::numeric,2) as daily_cost
    from energy.electric_utility
    where pid = '{pid}'
    
    UNION
    select 'gas' as service,
    date, therms as usage,
    round((therms*cost_per_therm)::numeric,2) as supply,
    round((days*min_charge + therms*(tier1_delivery+tier1_del_adj))::numeric,2) as delivery,
    round((therms*cost_per_therm + days*min_charge + therms*(tier1_delivery+tier1_del_adj))::numeric,2) as total,
    round(((therms::numeric)/(days::numeric))::numeric,4) as daily_usage,
    round(((therms*cost_per_therm + days*min_charge + therms*(tier1_delivery+tier1_del_adj))/(days::numeric))::numeric,2) as daily_cost
    from energy.gas_utility
    where pid = '{pid}'
    order by service,date
    ;
    """
   
    df = read_sql_query(query.format(pid=pid),db_connection)
    df = df.melt(['service','date'],var_name='series')
    
    tmp = df.groupby(['service','series']).rolling(12, min_periods=12, on='date')['value'].mean().reset_index()
    tmp = tmp[~isnull(tmp.value) & (tmp.series.isin(['daily_usage','daily_cost']))]
    tmp.series='ttm_'+tmp.series
    
    return concat([df,tmp])


def get_assessment_history(pid, db_connection):

    query = """
    select 
        jsonb_array_elements((previous->>'Year')::jsonb)::int as year,
        jsonb_array_elements((previous->>'Building')::jsonb)::int as building,
        jsonb_array_elements((previous->>'Land Value')::jsonb)::int as land,
        jsonb_array_elements((previous->>'Total')::jsonb)::int as total
    from property.patriot
    where pid = '{pid}'
    UNION
    select year, 
    (assessments->>'buildingValue')::int as building, 
    (assessments->>'landValue')::int as land, 
    (assessments->>'totalValue')::int as total
    from property.patriot
    where pid = '{pid}'
    ORDER BY year
    ;
    """
    df = read_sql_query(query.format(pid=pid),db_connection)
    
    df = df[df.year!=0]  ##badness in patriot extract
    if len(df)==0:
        return None
    
    year = df.year.min()
    
    query = """
        select * from property.tax_rates
        where year>={year}
           ;
    """.format(year=year)
    rates = read_sql_query(query,db_connection)
    
    df = df.merge(rates,how='left',on='year')

    ##above all better with UNNEST sql
    
    for col in df.columns[1:]:
        for idx in [1]:#,3,5,10]:
            try:
                df[col+'_chg_'+str(idx)+'y']=df[col]/df[col].shift(-1*idx)-1
            except:
                df[col+'_chg_'+str(idx)+'y']=None
                
    df = df.melt(['year'],var_name='series')
        
        
            
    return df.sort_values(['series','year']).reset_index(drop=True)


### recent sales
def get_recent_sales(db_connection):
    query = """
    select p.pid,p.image,p.address,
	ivp.value as land_use,
	ivp2.value as style,
	a."area" as lot_size,
	a."living_area" as living_area,
	p.rooms->>'Rooms' as rooms,
    p.rooms->>'Bedrooms' as bedrooms,
    p.interior->>'Full Baths' as bathrooms,
    p.interior->>'1/2 Bath' as halfbath,
	d.date,d.consideration as price, d.name,d.grant_type
    from property.deeds_details d
    left join property.patriot p on p.pid = d.pid
    left join property.assessments a on a.pid = d.pid and a.year=date_part('year',d.date)
    left join common.int_value_pairs ivp on ivp.key=a.land_use  and ivp.item='land_use'
    left join common.int_value_pairs ivp2 on ivp2.key=a.style  and ivp2.item='style'
    where consideration>100
    and deed_type=96
    order by date desc, timestamp desc
    LIMIT 80
    """

    df  =  get_data_from_db (
        query,
        db_connection
    )

    return recent_sales_get_data(df)

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


import re

def parse_markdown_tree(md):
    # Pattern to match markdown headers.
    pattern = re.compile(r"(#+) (.+?)\n")
    
    headers = []
    stack = []
    prev_end = 0
    
    for match in pattern.finditer(md):
        level = len(match.group(1))
        title = match.group(2)
        start = match.start()
        end = match.end()
        
        # Before processing a new header, assign content from the last end to this start to the last header.
        if stack:
            stack[-1]['content'] = md[prev_end:start].strip()

        node = {
            'level': level,
            'title': title,
            'children': [],
        }

        # Pop headers from the stack that are of the same or higher level.
        while stack and stack[-1]['level'] >= level:
            stack.pop()

        if stack:
            stack[-1]['children'].append(node)
        else:
            headers.append(node)

        stack.append(node)
        prev_end = end

    # Handle the content after the last header.
    if stack:
        stack[-1]['content'] = md[prev_end:].strip()

    return headers

