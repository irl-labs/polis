from dash import Dash, dcc, html
from dash_bootstrap_components import themes
from pandas import isnull, unique

##add assets/styles.css here
app = Dash(
    __name__,
    external_stylesheets = [ themes . BOOTSTRAP ],
    suppress_callback_exceptions = True
)

server = app.server

from utils import get_db_connection, get_params, get_data_from_db, get_solar_data, get_dor_scatter_series, get_recent_sales

## get UI parameters
db_connection  =  get_db_connection( dbname = "ArlingtonMA" )
params         =  get_params ( db_connection )

## get key, value pairs for client side cross reference
int_value_pairs  =  get_data_from_db (
    "select * from common.int_value_pairs;",
    db_connection
)

attributes  =  get_data_from_db (
    "select * from people.attributes;",
    db_connection
)

addresses  =  get_data_from_db (
    "select * from people.addresses;",
    db_connection
)

street_search = addresses[~isnull(addresses.streetNum)]\
    .groupby('streetName').agg({
        'streetNum':unique
    }).reset_index()


loc_polygons = get_data_from_db (
    "select loc_id,lat,lon,geometry from common.loc_polygons;",
    db_connection
)

loc_pid = get_data_from_db (
    "select * from common.loc_pid order by pid,year;",
    db_connection
)
## move to query OR use slider-date for loc_id at that time
loc_pid=loc_pid[~loc_pid.duplicated('pid',keep='last')][['pid','loc_id']]


solar = get_solar_data(db_connection)

dor_series = get_dor_scatter_series(params, int_value_pairs, db_connection)

## initialize data store for parameters, key/value cross reference
data_store  =  dcc . Store (
    id           = "polis-data-store",
    storage_type = "local",
    data = {}
)

recent_sales = get_recent_sales ( db_connection )

## poor place for app decorator callbacks
from callbacks import get_callbacks
get_callbacks ( app , params ,
                int_value_pairs , attributes, addresses,street_search,
                loc_pid, loc_polygons,solar,dor_series,recent_sales,
                db_connection )


## SPA layout
from layouts import app_layout
app.layout = app_layout ( params, data_store )


if __name__ == '__main__':
    from os import environ
    app.run_server(host="0.0.0.0", port=int(environ.get("PORT", 5000)))#,debug=True)
