import pandas as pd

def get_people_residents ( file ) :

    columns = [
        'Record Sequence Number',
        'Resident Id Number', 
        'Last Name',
        'First Name',
        'Middle Name',
        'Title',
        'Date of Birth',
        'Residential Address - Street Number',
        'Residential Address - Street Suffix',
        'Residential Address - Street Name',
        'Residential Address - Apartment Number',
        'Residential Address - Zip Code',
        'Mailing Address - Street Name and Number',
        'Mailing Address - Apartment Number',
        'Mailing Address - City or Town',
        'Mailing Address - State',
        'Mailing Address - Zip Code', 
        'Occupation',
        'Party Affiliation',
        'Nationality', 
        'Gender',
        'Ward Number',
        'Precinct Number',
        'Voter Status',
        'Mail to Code'
    ]

    residents =  pd . read_csv ( file , sep = '|' , low_memory = False , dtype = str )

    ##assumes RES files have column headers.  Gender dropped around 2020.
    lcols = len ( residents . columns )
    if   lcols  ==  25 :
        residents . columns = columns
    elif lcols  ==  24 :
        columns . remove ( 'Gender' )
        residents . columns = columns
    else:
        print ( 'Unsupported column size' , file )
        return pd . DataFrame ( )

    residents [ 'Date of Birth' ] = pd . to_datetime ( residents [ 'Date of Birth' ] , format = '%m/%d/%Y', errors = 'coerce' ) . dt . strftime ( '%Y-%m-%d' )

    ## handy for display
    residents  =  residents . replace ( { None : '' } )
    residents ['name'] = residents [ ['First Name', 'Middle Name', 'Last Name'] ] . apply ( lambda x : ' ' . join ( x ) , axis = 1 )

    residents['address']  = residents [ 'Residential Address - Street Number'   ] . map ( str , na_action = 'ignore' ) +\
                    ' ' + residents [ 'Residential Address - Street Name' ] . map ( str , na_action = 'ignore' ) +\
                    ' ' + residents [ 'Residential Address - Apartment Number'  ] . map ( str , na_action = 'ignore' ) .str.strip().replace(r'\s+',' ', regex=True)

    residents['name']  =     residents [ 'First Name'   ] . map ( str , na_action = 'ignore' ) +\
                ' ' + residents [ 'Middle Name'  ] . map ( str , na_action = 'ignore' ) +\
                ' ' + residents [ 'Last Name'    ] . map ( str , na_action = 'ignore' )

    residents[ 'party' ]  =  residents [ 'Party Affiliation' ]

    return residents


def get_people_registered ( file , Debug = False ) :

    import chardet
    import numpy as np

    columns = [
        'Record Sequence Number',
        'Voter Id Number',
        'Last Name',
        'First Name',
        'Middle Name',
        'Title',
        'Residential Address - Street Number',
        'Residential Address - Street Suffix',
        'Residential Address - Street Name',
        'Residential Address - Apartment Number',
        'Residential Address - Zip Code',
        'Mailing Address - Street Number and Name',
        'Mailing Address - Apartment Number',
        'Mailing Address - City or Town',
        'Mailing Address - State',
        'Mailing Address - Zip Code',
        'Party Affiliation',
        'Gender',
        'Date of Birth',
        'Date of Registration',
        'Ward Number',
        'Precinct Number',
        'Congressional District Number',
        'Senatorial District Number',
        'State Representative District',
        'Voter Status',
        'NA'
    ]


    with open ( file , 'rb' ) as f:
        enc  =  chardet . detect ( f . readline ( ) )  #readline since the file is large and generally entire directory read

    df  =  pd . read_csv ( file , sep = '|' , dtype = str , encoding = enc [ 'encoding' ] )

    lcols = len ( df . columns )
    if   lcols  ==  27 :
        df . columns = columns
    elif lcols  ==  26 :
        columns.remove('Gender')
        df . columns = columns
    else:
        print ( 'Unsupported column size', )


    for col in [ 'Date of Birth' , 'Date of Registration' ] :
        df [ col ] = pd . to_datetime ( df [ col ] , format = '%m/%d/%Y', errors = 'coerce' ) . dt . strftime ( '%Y-%m-%d' )

    ## handy for display
    df  =  df . replace ( { None : '' } )
    df['address']  = df [ 'Residential Address - Street Number'   ] . map ( str , na_action = 'ignore' ) +\
                    ' ' + df [ 'Residential Address - Street Name' ] . map ( str , na_action = 'ignore' ) +\
                    ' ' + df [ 'Residential Address - Apartment Number'  ] . map ( str , na_action = 'ignore' ) .str.strip().replace(r'\s+',' ', regex=True)

    df['name']  =     df [ 'First Name'   ] . map ( str , na_action = 'ignore' ) +\
                ' ' + df [ 'Middle Name'  ] . map ( str , na_action = 'ignore' ) +\
                ' ' + df [ 'Last Name'    ] . map ( str , na_action = 'ignore' )
#    df ['name'] = df [ ['First Name', 'Middle Name', 'Last Name'] ] . apply ( lambda x : ' ' . join ( x ) , axis = 1 )

    df [ 'party' ]  =  df [ 'Party Affiliation' ]

    df = df . drop ( 'NA' , axis = 1 ) . replace ( { np . nan : None } )
    
    return df 


def get_people_elections ( file ) :
    
    import os
    import numpy as np

    # columns :trimmed trailing blanks and renamed 'Voter Status r' to 'Voter Status'
    if 'ANP' in file:
        columns = [
            'Party Affiliation', 
            'Voter Id Number', 
            'Last Name', 
            'First Name',
            'Middle Name',
            'Residential Address - Street Number',
            'Residential Address - Street Suffix',
            'Residential Address - Street Name',
            'Residential Address - Apartment Number',
            'Residential Address - Zip Code',
            'Type of Election',
            'Election Date',
            'City/ Town Name',
            'City/ Town Indicator',
            'City/ Town Code Assigned Number',
            'Voter Title',
            'Ward Number',
            'Precinct Number',
            'Voter Status',
            'Mailing Address - Street Number/Name',
            'Mailing Address - Apartment Number',
            'Mailing Address - City/Town',
            'Mailing Address - State',
            'Mailing Address - Zip Code'
        ]
    elif 'ACP' in file :
        columns = [
            'Party Affiliation', 
            'Voter Id Number', 
            'Last Name', 
            'First Name',
            'Middle Name',
            'Residential Address - Street Number',
            'Residential Address - Street Suffix',
            'Residential Address - Street Name',
            'Residential Address - Apartment Number',
            'Residential Address - Zip Code',
            'Type of Election',
            'Election Date',
            'Party Voted',
            'City/ Town Name',
            'City/ Town Indicator',
            'City/ Town Code Assigned Number',
            'Voter Title',
            'Ward Number',
            'Precinct Number',
            'Voter Status',
            'Mailing Address - Street Number/Name',
            'Mailing Address - Apartment Number',
            'Mailing Address - City/Town',
            'Mailing Address - State',
            'Mailing Address - Zip Code'
        ]        
    else:
        print('Unknown file type',file)
        return

    ## historic files were stripped of header for ArlingtonMA only
    if os . path . getmtime(file) < 1648199999 :        
        df = pd.read_csv(file, sep='|', header = None, dtype=str)
    else:
        df = pd.read_csv(file, sep='|', dtype=str)


    ##last column all null, MA supplied header has extra field separator.
    if pd.isnull(df[df.columns[-1]]).all() :
        df.drop(df.columns[-1],axis=1,inplace=True)

    df.columns = columns
    
    mask = df['Residential Address - Zip Code'].str[0:5].isin(['02474','02476','02174'])
    if len(df[~mask])>0:
        print('non-Arlington voters in',file,len(df[~mask]))
        
    df = df[mask]

    df [ 'Election Date' ] = pd.to_datetime( df [ 'Election Date' ] )
    df [ 'party' ]  =  df [ 'Party Affiliation' ]

    if 'Party Voted' in df.columns:
        df [ 'partyVoted' ]  =  df [ 'Party Voted' ]

    mask = ~pd.isnull(df [ 'Residential Address - Apartment Number'  ])
#    df.loc[mask,'Residential Address - Apartment Number'] = '#'+df.loc[mask,'Residential Address - Apartment Number']
    df = df.replace({np.nan:''})
    df['address']  = df [ 'Residential Address - Street Number'   ] . map ( str , na_action = 'ignore' ) +\
                    ' ' + df [ 'Residential Address - Street Name' ] . map ( str , na_action = 'ignore' ) +\
                    ' ' + df [ 'Residential Address - Apartment Number'  ] . map ( str , na_action = 'ignore' ) .str.strip().replace(r'\s+',' ', regex=True)

    df['name']  =     df [ 'First Name'   ] . map ( str , na_action = 'ignore' ) +\
                ' ' + df [ 'Middle Name'  ] . map ( str , na_action = 'ignore' ) +\
                ' ' + df [ 'Last Name'    ] . map ( str , na_action = 'ignore' )

    df['Precinct Number']=df['Precinct Number'].astype(int).astype(str)
    
    return df



''' 
    10VOT*.txt has "Date of Registration".  
    10RES*.txt has ascension numbers close-by "Date of Registration".  
    Match VOT and RES by close-by ascension numbers
'''

def create_file_asof_date_xref ( registered, residents, elections ) :

    xref = {'registered':{},'residents':{},'elections':{}}

    for key in registered . keys ( ) :
        date = pd . to_datetime ( registered [ key ] [ 'Date of Registration' ] ) . max ( ) . strftime ( '%Y-%m-%d' )
        xref [ 'registered' ] [ key ] = date

    for key in elections . keys ( ) :
        if len ( elections [ key ] ) > 0:
            date = pd . to_datetime ( elections [ key ] [ 'Election Date' ] ) . max ( ) . strftime ( '%Y-%m-%d' )
            xref [ 'elections' ] [ key ] = date
            
    ##compared file names (numbers) between voters to residents; usually off by "1", automate via merge.asof(), also use file ctime stamps
    
    xref [ 'residents' ] = {
        '10RES_26391.txt':'2004-11-18',
        '10RES_31188.txt':'2005-04-27',
        '10RES_35526.txt':'2005-12-02',
        '10RES_53376.txt':'2007-11-20',
        '10RES_54643.txt':'2008-01-23',
        '10RES_72247.txt':'2009-12-30',
        '10RES_80049.txt':'2010-08-25',
        '10RES_83484.txt':'2010-12-09',
        '10RES_87627.txt':'2011-05-18',
        '10RES_96845.txt':'2012-05-07',
        '10RES_92961.txt':'2012-01-17',
        '10RES_104016.txt':'2012-12-04',
        '10RES_108782.txt':'2013-04-18',
        '10RES_112368.txt':'2014-04-04',
        '10RES_114472.txt':'2014-02-24',
        '10RES_119073.txt':'2014-08-27',
        '10RES_121269.txt':'2014-12-01',
        '10RES_126110.txt':'2015-06-19',
        '10RES_129402.txt':'2015-11-25',
        '10RES_135055.txt':'2016-06-30',
        '10RES_140090.txt':'2016-12-05',
        '10RES_147065.txt':'2017-07-04',
        '10RES_152836.txt':'2018-01-08',
        '10RES_157881.txt':'2018-06-28',
        '10RES_164376.txt':'2019-01-07',
        '10RES_169655.txt':'2019-07-09',
        '10RES_204218.txt':'2019-12-26',
        '10RES_211001.txt':'2020-06-29',
        '10RES_226805.txt':'2020-12-23',
        '10RES_234478.txt':'2021-06-30',
        '10RES_240871.txt':'2021-12-30',
        '10RES_242017.txt':'2022-02-01',
        '10RES_242314.txt':'2022-03-01',
        '10RES_244961.txt':'2022-04-25',
        '10RES_250706.txt':'2022-08-11',
        '10RES_260000.txt':'2022-10-20',
        '10RES_272671.txt':'2023-02-27',
        '10RES_272815.txt':'2023-03-16',
    }

    for key in xref . keys ( ) :
        xref[key] = {k: v for k, v in sorted(xref[key].items(), key=lambda item: item[1])}
        
    return xref

## combine_residents_into_households belongs in transform for dash modules
def combine_residents_into_households ( file ) :

    ##combine all residents within a parcel; including condos, apartments, etc.  For merge with parcel level data
   
    df = file . groupby ( [ 'Residential Address - Street Name', 'Residential Address - Street Number'] ) \
                      . agg ( {
                                'name':list,
                                'Occupation':pd.unique,
                                'Party Affiliation':pd.unique, 
                                'Nationality':pd.unique, 
                                'Precinct':max,
                                'Voter Status':pd.unique
                            } ) \
                        . reset_index ( )
    
    df . columns = [ 'street','streetNumber','name','occupation','party','nationality','precinct','voterStatus' ]

    mask  =  df . name . apply ( len ) > 5
    df . loc [ mask , 'name' ] = df . name . apply ( len ) [ mask ] . astype ( str ) + ' adults'

    return df
