import pandas as pd
import numpy as np
import time
import shutil

"""
Schools postgres tables, drop/create

"""
table_create_schools_enrollment = \
    """
        DROP TABLE IF EXISTS infrastructure.schools_enrollment;
        CREATE TABLE infrastructure.schools_enrollment (
            "school_id" INTEGER,
            "year" SMALLINT,
            "grade" VARCHAR(5),
            "value" INT,
            PRIMARY KEY ("school_id","year","grade")
        );
        CREATE INDEX schools_enrollment_idx 
            ON infrastructure.schools_enrollment("school_id");
        CREATE INDEX schools_enrollment_year_idx 
            ON infrastructure.schools_enrollment("year");
            
    """


table_create_mcas = \
    """
        DROP TABLE IF EXISTS infrastructure.schools_mcas;
        CREATE TABLE infrastructure.schools_mcas (
            "school_id" INTEGER,
            "year" SMALLINT,
            "mcas_subject" SMALLINT,
            "mcas_grade" SMALLINT,
            "mcas" SMALLINT,
            "value" INT,
            PRIMARY KEY ("school_id","year","mcas_subject","mcas_grade","mcas")
        );
        CREATE INDEX schools_mcas_idx 
            ON infrastructure.schools_mcas("school_id");
        CREATE INDEX schools_mcas_year_idx 
            ON infrastructure.schools_mcas("year");
        COMMIT;    
    """

table_create_schools = \
    """
        DROP TABLE IF EXISTS infrastructure.schools_{category};
        CREATE TABLE infrastructure.schools_{category} (
            "school_id" INTEGER,
            "year" SMALLINT,
            "{category}" SMALLINT,
            "value" INT,
            PRIMARY KEY ("school_id","year","{category}")
        );
        CREATE INDEX schools_{category}_idx 
            ON infrastructure.schools_{category}("school_id");
        CREATE INDEX schools_{category}_year_idx 
            ON infrastructure.schools_{category}("year");
        COMMIT;    
    """

table_create_teachers = \
    """
        DROP TABLE IF EXISTS infrastructure.schools_{category};
        CREATE TABLE infrastructure.schools_{category} (
            "school_id" INTEGER,
            "year" SMALLINT,
            "{category}" SMALLINT,
            "value" INT,
            PRIMARY KEY ("school_id","year","{category}")
        );
        CREATE INDEX schools_{category}_idx 
            ON infrastructure.schools_{category}("school_id");
        CREATE INDEX schools_{category}_year_idx 
            ON infrastructure.schools_{category}("year");
        COMMIT;    
    """

table_create_schools_types = \
    """
        DROP TABLE IF EXISTS infrastructure.schools_types;
        CREATE TABLE infrastructure.schools_types (
            "dor" SMALLINT,
            "year" SMALLINT,
            "schools_type" SMALLINT,
            "value" SMALLINT,
            PRIMARY KEY ("dor","schools_type","year")
        );
        CREATE INDEX schools_type_idx 
            ON infrastructure.schools_types("schools_type");
            
    """

table_create_school_id_location = \
    """
        DROP TABLE IF EXISTS common.school_id_location;
        CREATE TABLE common.school_id_location (
            "school_id" INTEGER,
            "year" SMALLINT,
            "location" VARCHAR(25),
            "dor" SMALLINT,
            PRIMARY KEY ("school_id","year")
        );
        CREATE INDEX school_id_location_idx 
            ON common.school_id_location("school_id");
            
    """


from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException


def start_up(url, data_dir='./', headless=False):
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from webdriver_manager.chrome import ChromeDriverManager

    options = Options()
    options.add_argument("start-maximized")

    prefs = {
        "download.default_directory"   :  data_dir,
        "download.prompt_for_download" :  False,
        "download.directory_upgrade"   :  True
    }

    options.add_experimental_option('prefs', prefs)

    if headless==True:
        options.add_argument("--headless")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    driver.get(url)

    return driver

def get_schools_enrollments(driver):

    id = "ctl00_ContentPlaceHolder1_ddReportType"
    report_types=[]
    for elem in Select(driver.find_element(By.ID,id)).options:
        report_types.append(elem.get_attribute("value"))

    id = "ctl00_ContentPlaceHolder1_ddYear"
    years=[]
    for elem in Select(driver.find_element(By.ID,id)).options:
        years.append(elem.get_attribute("value"))

    data = {}
    for report_type in [x.title() for x in report_types]:
        data[report_type]=pd.DataFrame()
        select = Select(driver.find_element(By.ID,'ctl00_ContentPlaceHolder1_ddReportType'))
        select.select_by_visible_text(report_type)
        for year in years:
            select = Select(driver.find_element(By.ID,'ctl00_ContentPlaceHolder1_ddYear'))
            select.select_by_value(year)
            #time.sleep(1)

            driver.find_element(By.ID,'btnViewReport').click()
            time.sleep(1)
            tmp_df = pd.read_html(driver.page_source)[0]
            tmp_df['year']=year
            data[report_type] = pd.concat([data[report_type],tmp_df])
            
    return data

def transform_enrollments(data):
    enrollments = pd.DataFrame()
    int_value_pairs = pd.DataFrame()
    for key in data.keys():

        data[key][key+' Name']=data[key][key+' Name'].str.upper()

        mask = (data[key][key+' Name']!="NO DATA AVAILABLE IN TABLE") &\
            (data[key][key+' Code']!="No data available in table") &\
            (data[key][key+' Name']!="STATE TOTALS") &\
            (data[key][key+' Name']!="STATE TOTALS - STATE TOTALS") &\
            (data[key][key+' Name']!="STATE TOTAL - STATE TOTAL") &\
            (data[key][key+' Name']!="STATE TOTAL")
        df = data[key][mask].sort_values([key+' Code','year']).rename(columns={key+' Code':'school_id'})

        cols = ['school_id',key+' Name']
        xref = df[cols][~df[cols].duplicated(cols)].sort_values('school_id')
        xref.columns = ['key','value']
        xref['item']=key.lower()
        int_value_pairs = pd.concat([int_value_pairs,xref])

        df = df.drop(key+' Name',axis=1)
        df[df==0.0]=np.nan
        enrollments=pd.concat([enrollments,df])

    df = pd.melt(enrollments, id_vars=['school_id','year'], 
            value_vars=['PK','K','1','2','3','4','5','6',
                        '7','8','9','10','11','12','SP','Total'],
           var_name='grade')
    
    df=df[df.value==df.value]  ##dump nan
    
    return df, int_value_pairs    

def get_private_schools_enrollments(driver):

    id = "ctl00_ContentPlaceHolder1_ddYear"
    years=[]
    for elem in Select(driver.find_element(By.ID,id)).options:
        years.append(elem.get_attribute("value"))

    data = pd.DataFrame()
    #schools = {}
    for year in years:
        orgcodes = []
        print('Working',year)
        select = Select(driver.find_element(By.ID,'ctl00_ContentPlaceHolder1_ddYear'))
        select.select_by_value(year)
        #time.sleep(1)

        driver.find_element(By.ID,'ctl00_ContentPlaceHolder1_btnViewReport').click()
        time.sleep(1)
        tmp_df = pd.read_html(driver.page_source)[0]
        tmp_df['year']=year

        table = driver.find_elements(By.XPATH,'//*[@id="tblStateReport"]/tbody/tr')
        for row in table:
            link = row.find_element(By.TAG_NAME,"a")
            orgcode = link.get_attribute("href").split('orgcode=')[1].split('&')[0]
            orgcodes.append(orgcode)

        tmp_df['school_id']=orgcodes

        data = pd.concat([data,tmp_df])
        
    return data

def transform_private_schools_enrollments(data):

    data['Location']=data['Location'].str.upper()
    data['Location']=data['Location'].str.replace(' (NON-OP)','')
    data=data[~data['Location'].isin(['STATE TOTAL','STATE TOTALS'])]
    data.loc[:,'School Name']=data.loc[:,'School Name'].str.upper()

    schools = data[['school_id','School Name','Location','year']].sort_values(['school_id','year'])

    #schools = schools[~schools.duplicated()].sort_values(['school_id']).reset_index(drop=True)
    schools = schools[~schools.duplicated('school_id',keep='last')].sort_values(['school_id']).reset_index(drop=True)
    schools

    dor = pd.read_sql_query("select * from common.int_value_pairs where item='dor'",cnx)
    dor['value']=dor['value'].str.upper()
    df = schools.merge(dor,
                    right_on='value',
                    left_on='Location',
                    how='left',
                    indicator='matched')#\
    xref = df[['school_id','School Name']]\
        .rename(columns={'school_id':'key','School Name':'value'})
    xref['item'] = 'private school'
    xref.key=xref.key.astype(int)

    assert(xref.key.duplicated().any()==False)

    school_id_2_dor = df[['school_id','Location','year','key']]\
        .rename(columns={'Location':'location','key':'value'})
    school_id_2_dor.school_id=school_id_2_dor.school_id.astype(int)


    data.columns=data.columns.str.replace('TOTAL','Total')

    data=data.drop(['Location','School Name'],axis=1)

    df = pd.melt(data, id_vars=['school_id','year'], 
            value_vars=['PK','K','1','2','3','4','5','6',
                        '7','8','9','10','11','12','SP','Total'],
           var_name='grade')
    df = df[df['value']!=0].sort_values(['school_id','year']).reset_index(drop=True)
    df.school_id=df.school_id.astype(int)

    return df, xref, school_id_2_dor

def get_schools_types(driver):
    id = "ctl00_ContentPlaceHolder1_ddYear"
    years=[]
    for elem in Select(driver.find_element(By.ID,id)).options:
        years.append(elem.get_attribute("value"))

    data = pd.DataFrame()

    for year in years:
        print('Working',year)
        select = Select(driver.find_element(By.ID,'ctl00_ContentPlaceHolder1_ddYear'))
        select.select_by_value(year)
        #time.sleep(1)

        # element = WebDriverWait(driver,10)\
        #              .until(EC.presence_of_element_located((By.ID, id)))
        driver.find_element(By.ID,'ctl00_ContentPlaceHolder1_btnViewReport').click()
        time.sleep(1)
        tmp_df = pd.read_html(driver.page_source)[0]
        tmp_df['year']=year

        data = pd.concat([data,tmp_df])
    
    return data


def transform_schools_types(data):

    for string in [' (non-op)',' (Non-Op)',' (non-op',' (Non-op)','*']:
        data.Town=data.Town.str.replace(string,'')

    data.Town=data.Town.str.replace('Manchester','Manchester By The Sea')
    data.Town=data.Town.str.replace('Gay Head','Aquinnah')
    data = data[~data.Town.isin(['STATE TOTALS','State','State Total'])]
   
    dor = pd.read_sql_query("select * from common.int_value_pairs where item='dor';",cnx)
    dor = pd.concat([dor,pd.DataFrame({'key':[999],'item':['dor'],'value':['Devens']})])
    
    combo = data\
            .merge(dor,
                   right_on='value',
                   left_on='Town',
                   how='left',
                   indicator='matched')\
            .drop(['Town','item', 'value', 'matched'],axis=1)\
            .rename(columns={'key':'dor'})   
    
    df = pd.melt(combo, id_vars=['dor','year'], 
       var_name='schools_type')
    df = df[(df['value']!=0.0)&(df['value']==df['value'])&(df.schools_type!='% Public')]
    df = df[~df.duplicated(['dor','schools_type','year'])]
    
    schools_types = list(df.schools_type.unique())
    xref = dict(zip(schools_types,range(len(schools_types))))
    df.schools_type=df.schools_type.replace(xref)

    int_value_pairs = pd.DataFrame.from_dict(
        dict(zip(range(len(schools_types)),schools_types)),
        orient='index').reset_index().rename(columns={'index':'key',0:'value'})
    int_value_pairs['item']='schools_type'
    int_value_pairs
    
    return df, int_value_pairs
    

def get_teacher_details(
    driver,
    ids = {
        'year':'ctl00_ContentPlaceHolder1_ddYear',
        'button':'btnViewReport',
    }
):

    id = ids['year']
    years=[]
    for elem in Select(driver.find_element(By.ID,id)).options:
        years.append(elem.get_attribute("value"))

    data = pd.DataFrame()
    for year in years:
        select = Select(driver.find_element(By.ID,ids['year']))
        select.select_by_value(year)

        driver.find_element(By.ID,ids['button']).click()
        time.sleep(1)
        tmp_df = pd.read_html(driver.page_source)[0]
        tmp_df['year']=year

        data = pd.concat([data,tmp_df])
        
    return data


def transform_teacher_details(df, category = 'salaries_type',
                                 id_vars = ['school_id','year']
):

    if 'Salary Totals' in df.columns:
        for col in ['Salary Totals','Average Salary']:
            df[col]=df[col].str.replace('\$|\,','',regex=True).astype(int)

    ##for melt + db purposes, I'm rounding FTE Count to an int
    if 'FTE Count' in df.columns:
        df['FTE Count']=round(df['FTE Count'],0).astype(int)

    ## drop redundant District Name, 
    ## should check District Code is in int_value_pairs for new...
    df = df\
            . rename(columns={'District Code':'school_id'})\
            . drop(['District Name'],axis=1)\
            . sort_values(['school_id','year'])\
            . reset_index(drop=True)

    df = pd.melt(df, id_vars=id_vars, 
                 var_name=category)
    df = df[(df['value']!=0.0)&(df['value']==df['value'])]

    types = list(df[category].unique())
    xref = dict(zip(types,range(len(types))))
    df[category]=df[category].replace(xref)

    int_value_pairs = pd.DataFrame.from_dict(
        dict(zip(range(len(types)),types)),
        orient='index').reset_index().rename(columns={'index':'key',0:'value'})
    int_value_pairs['item']=category
    
    return df, int_value_pairs


def transform_mcas(data):
    
    mask = data['District Code']!=data['District Code']
    data.loc[mask,'District Code']=data.loc[mask,'School Code']

    mask = data['District Name']!=data['District Name']
    data.loc[mask,'District Name']=data.loc[mask,'School Name']

    data=data.drop(['School Code','School Name'],axis=1)

    df, xref = transform_teacher_details(data.copy(), 
                              category = 'mcas',
                              id_vars = ['school_id','year','Subject','grade']
                             )

    mask = (df['school_id']!="No data available in table")&\
            (df.school_id!=0)
    df=df[mask]

    a = list(df.Subject.sort_values().unique())
    str_2_int = dict(zip(a,range(len(a))))
    int_2_str = pd.DataFrame.from_dict(dict(zip(range(len(a)),a)),orient='index').reset_index().rename(columns={'index':'key',0:'value'})
    int_2_str['item']= 'mcas_subject'
    ivp1 = pd.concat([xref,int_2_str])
    df.Subject=df.Subject.replace(str_2_int)
    df.columns = df.columns.str.replace('Subject','mcas_subject')
    
    a = list(df.grade.sort_values().unique())
    str_2_int = dict(zip(a,range(len(a))))
    int_2_str = pd.DataFrame.from_dict(dict(zip(range(len(a)),a)),orient='index').reset_index().rename(columns={'index':'key',0:'value'})
    int_2_str['item']= 'mcas_grade'
    int_value_pairs = pd.concat([ivp1,int_2_str])
    df.grade=df.grade.replace(str_2_int)
    df.columns = df.columns.str.replace('grade','mcas_grade')
    
    return df, int_value_pairs

def get_mcas(driver):

    ids = {}
    ids['report_type'] = "ctl00_ContentPlaceHolder1_ddReportType"
    ids['year']    =  "ctl00_ContentPlaceHolder1_ddYear"
    ids['grade']   =  "ctl00_ContentPlaceHolder1_ddGrade"
    ids['button']  =  "btnViewReport"

    grades=[]
    for elem in Select(driver.find_element(By.ID,ids['grade'])).options:
        grades.append(elem.get_attribute("value"))

    report_types=[]
    for elem in Select(driver.find_element(By.ID,ids['report_type'])).options:
        report_types.append(elem.get_attribute("value"))

    years=[]
    for elem in Select(driver.find_element(By.ID,ids['year'])).options:
        years.append(elem.get_attribute("value"))

    print(
        'report_types',report_types,
        'grades',grades,
        'years',years
    )

    data = pd.DataFrame()
    for report_type in report_types:
        select = Select(driver.find_element(By.ID,ids['report_type']))
        select.select_by_value(report_type)

        for year in years:
            if year=='2020':
                continue

            select = Select(driver.find_element(By.ID,ids['year']))
            select.select_by_value(year)

            for grade in grades:
                try:
                    select = Select(driver.find_element(By.ID,ids['grade']))
                    select.select_by_value(grade)

                    driver.find_element(By.ID,ids['button']).click()
                    time.sleep(1)
                    tmp_df = pd.read_html(driver.page_source)[0]

                    tmp_df['year']=year
                    tmp_df['grade']=grade

                    data = pd.concat([data,tmp_df])
                    
                except:
                    print('Failed',report_type,year,grade)
                    continue
        
    return data
