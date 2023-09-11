### [LA3 Sales](https://dlsgateway.dor.state.ma.us/gateway/DLSPublic/ParcelSearch)

* [DOR Land Use codes and Arms Length sales (NAL) codes](https://www.mass.gov/doc/property-type-classification-codes-non-arms-length-codes-and-sales-report-spreadsheet/download)


MA Department of Local Services (DLS) Gateway offers local officials
an immediate way to enter data and verify submission status across all
the regulatory review programs administered by Division of Local
Services. The LA3 parcel search details all real estate property sales
used in assessment valuations.

The data is for every city and town in Massachusetts from about 2001
through the current period and is generally updated each year in the
fall.  Fiscal year generally ends on June 30.  The same realestate
sales are sometimes used in different fiscal years; duplicates are
removed. Recreating assessment valuations using the LA3 Sales process
would require the possible inclusion of duplicate sales in different
fiscal years.

The data is incomplete for calendar years 2001 and 2007.  The
*Process*(I, C), *Prior Assessed Value*, *Current Assessed Value* and
*A/S Ratio* (Assessed to Sales) columns are dropped.  Columns *St
Name*, *St Alpha* and *Num* are combined into the address column.

The PID (asessor's property identifier) changes to standard full
format in 2005, the function *fix_pid_property_sales* is the attempt
to normalize all pids to current, long form standard; ~700/13000 fail
to match assessor records, mostly in 2002 and 2004.

The LA3 sales report is downloaded, transformed and loaded to postgres
using the [sales ETL notebook]().

#### Output

*  address TEXT
*  land_use INTEGER   [cross reference](https://www.mass.gov/doc/property-type-classification-codes-non-arms-length-codes-and-sales-report-spreadsheet/download) with description in common.int_value_pairs sql table
*  date TEXT
*  price INTEGER
*  buyer TEXT
*  seller TEXT
*  sale_type INTEGER [cross reference](https://www.mass.gov/doc/property-type-classification-codes-non-arms-length-codes-and-sales-report-spreadsheet/download) with description in common.int_value_pairs sql table
*  year INTEGER
*  loc_id TEXT
*  pid TEXT

#### Issues

* Multi-parcel deals have the aggregate price for each tax parcel in package.
* Missing 2003 and 2005 sales
* repeated sales across fiscal years
* lags by 18 months
* pid format changes
* loc_id in meter reference plane; in feet since 2018.
* loc_id change (centroid of parcel in feet F_LAT_LON) without (legal) documented changes
  