import pandas as pd
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def start_up(county = 'MiddlesexSouth', headless=True):
    from datetime import datetime
    from selenium.webdriver.chrome.options import Options

    url = 'http://www.masslandrecords.com/' + county +'/Default.aspx'

    options = Options()
    options.add_argument("start-maximized")

    from seleniumbase import Driver

    driver = Driver(browser="chrome", headless=False)
    driver.maximize_window()

    driver.get(url)

    addedCookies = [{u'domain': u'www.masslandrecords.com',
      u'expiry': int(datetime.now().strftime("%s"))+3600*24*7,# 1 week in the future...
      u'name': u'AllowPopupTips',
      u'path': u'/',
      u'secure': False,
      u'value': u'False'}]

    for cookie in addedCookies:
        driver.add_cookie(cookie)

    return driver


def Btn ( driver, button ) :
    try:
        element = WebDriverWait(driver,10)\
                    .until(EC.presence_of_element_located((By.ID, button)))
        driver.find_element(By.ID,button).click()

    except :
        print ("Waited 10s for button.")
        
def fill_in_form(driver,data):
    idx = 0
    for id in [
        "SearchFormEx1_ACSTextBox_Document",
        "SearchFormEx1_ACSTextBox_Document2",
        "SearchFormEx1_ACSTextBox_DateFrom",
        "SearchFormEx1_ACSTextBox_DateTo"
    ]:
        try:
            element = WebDriverWait(driver,100)\
                        .until(EC.presence_of_element_located((By.ID, id)))
            input_field = driver.find_element(By.ID,id)
            input_field.clear()
            input_field.send_keys(data[idx])
            idx += 1

        except :
            print ("Waited 10s for Input Field.")
            
def deeds_load_summary_page ( func, **kwargs ):
    def perform(f):
        f()
    
    driver=start_up(headless=kwargs['headless'])
    time.sleep(5)

    Btn(driver,"Navigator1_SearchCriteria1_menuLabel")
    if kwargs['recorded']:
        Btn(driver,'Navigator1_SearchCriteria1_LinkButton02') #recorded land
    else:
        Btn(driver,'Navigator1_SearchCriteria1_LinkButton13')#registered land
        select_town(driver,town='ARLINGTON')
        
    Btn(driver,'SearchFormEx1_BtnAdvanced')
    
    data = [kwargs['docno_from'], kwargs['docno_to'], 
            kwargs['date_from'], kwargs['date_to']]
    print(data)
    fill_in_form(driver,data)

    Btn(driver,'SearchFormEx1_btnSearch')
    Btn(driver,'DocList1_PageView100Btn')
    
    df = perform(lambda: func(driver, **kwargs))
    
    return df

def get_table_contents(driver):
    from pandas import read_html
    df=read_html(driver.page_source)

    for idx in range(len(df)):
        if 'Book/Page' in df[idx].columns:
            return df[idx].iloc[2:-2,1:]
        
    return None

from selenium.common.exceptions import NoSuchElementException
def check_exists_by_id(driver,id):
    try:
        driver.find_element(By.ID,id)
    except NoSuchElementException:
        return False
    return True


def update_docno_range(driver,docno_range):
    idx = 0
    for id in [
        "SearchFormEx1_ACSTextBox_Document",
        "SearchFormEx1_ACSTextBox_Document2"
    ]:
        element = WebDriverWait(driver,10)\
                    .until(EC.presence_of_element_located((By.ID, id)))
        input_field = driver.find_element(By.ID,id)
        input_field.clear()
        input_field.send_keys(str(docno_range[idx]))
        idx += 1


    time.sleep(2)
    button = 'SearchFormEx1_btnSearch'
    Btn(driver,button)
    return True


def update_book_page(driver,book, page):
    idx = 0
    for id in [
        "SearchFormEx1_ACSTextBox_Book",
        "SearchFormEx1_ACSTextBox_PageNumber"
    ]:
        element = WebDriverWait(driver,10)\
                    .until(EC.presence_of_element_located((By.ID, id)))
        input_field = driver.find_element(By.ID,id)
        input_field.clear()
        input_field.send_keys(str(book if idx == 0 else page))
        idx += 1


    time.sleep(2)
    button = 'SearchFormEx1_btnSearch'
    Btn(driver,button)
    return True


def select_town(driver,
                town='ARLINGTON',
                id='SearchFormEx1_ACSDropDownList_Towns'):
    from selenium.webdriver.support.ui import Select
    try:
        element = WebDriverWait(driver,10)\
                    .until(EC.presence_of_element_located((By.ID, id)))
        select = Select(driver.find_element(By.ID,id))
        select.select_by_visible_text(town)

    except :
        print ("Town dropdown select failed.")
        

def combine_pages(driver):
    id = "DocList1_LinkButtonNext"
    all_df=pd.DataFrame()
    while True:
        df = get_table_contents(driver)
        time.sleep(4)
        all_df = pd.concat([all_df,df])
        if check_exists_by_id(driver,id)==True:
            Btn(driver,id)
            time.sleep(2)
        else:
            break

    return all_df
        
def combine_pages2(driver):
    id = "DocList1_LinkButtonNext"
    all_df=pd.DataFrame()
    df = get_table_contents(driver)
    time.sleep(4)
    all_df = pd.concat([all_df,df])
    if check_exists_by_id(driver,id)==True:
        Btn(driver,id)
    return all_df


def find_gaps(df):
    from itertools import groupby
    from operator import itemgetter
    
    ranges = []
    for key, group in groupby(enumerate(df), lambda i: i[0] - i[1]):
        group = list(map(itemgetter(1), group))
        ranges.append((group[0], group[-1]))
        
    return ranges

def deeds_summary_norm(df, cnx):

    deeds_summary   =  df[~df.duplicated()].copy()
    deeds_summary.columns = ['date','book/page','deed_type','town','docno']
    deeds_summary.docno = deeds_summary.docno.astype(int)

    deeds_summary['date'] = pd.to_datetime(deeds_summary['date']).dt.date

    query = "select key,upper(value) as value from common.int_value_pairs where item='deed_type'"
    int_value_pairs = pd.read_sql_query(query,cnx)
    xref = dict(
        zip(int_value_pairs.to_dict()['value'].values(),
            int_value_pairs.to_dict()['key'].values()
           )
    )
    
    query = "select key,upper(value) as value from common.int_value_pairs where item='dor'"
    int_value_pairs = pd.read_sql_query(query,cnx)
    town_2_dor = dict(
        zip(
            int_value_pairs.to_dict()['value'].values(),
            int_value_pairs.to_dict()['key'].values()
        )
    )
    
    town_2_dor['NONE']=999
    town_2_dor['MULTIPLE']=998
    town_2_dor['OUT COUNTY']=997
    town_2_dor['MARLBORO']=996
    town_2_dor['SEE RECORD']=995
    town_2_dor['OUT OF DISTRICT']=994

    deeds_summary.deed_type=deeds_summary.deed_type.replace(xref)
    deeds_summary.town=deeds_summary.town.replace(town_2_dor)

    deeds_summary['book'] = deeds_summary['book/page'].str.split('/').str[0]
    deeds_summary['page'] = deeds_summary['book/page'].str.split('/').str[1]
    deeds_summary=deeds_summary.drop(['book/page'],axis=1)
    deeds_summary.loc[deeds_summary.page=='','page']='0'
    deeds_summary.loc[deeds_summary.book=='','book']='0'
    

    deeds_summary=deeds_summary[['date','book','page','deed_type','town','docno']]
    
    return deeds_summary.sort_values(['docno']).reset_index(drop=True)

def get_detail(driver):
    df=pd.read_html(driver.page_source)
    address = pd.DataFrame()
    for idx in range(len(df)):
        if 'Street #' in df[idx].columns:
            address= df[idx]
            break
        
    details=pd.DataFrame()
    for idx in range(len(df)):
        if 'Consideration' in df[idx].columns:
            details= df[idx]
            break
    df = pd.concat([address,details],axis=1)
            
    try:
        id="DocDetails1_GridView_GrantorGrantee"
        people = pd.read_html(driver.page_source,attrs = {'id':id})[0]
        people.columns = ['name','grant_type']
        # people = people.to_dict('records')
        for col in people.columns:
            df.at[0,col]=''
            df.at[0,col]=[ x for x in people[col].replace({'^Grantee$':0,'^Grantor$':1},regex=True).to_list()]
    except:
        print('No people')
    
    try:
        id="DocDetails1_GridView_Document_Refs"
        refs = pd.read_html(driver.page_source,attrs = {'id':id})[0]
        refs.columns = ['refs_book_page','refs_deed_type','refs_year']
        for col in refs.columns:
            df.at[0,col]=''
            df.at[0,col]=[ x for x in refs[col].replace({'^Grantee$':0,'^Grantor$':1},regex=True).to_list()]
        # refs = refs.to_dict('list')
        # df.at[0,'refs']=refs
    except:
        pass
        #print('No refs')
        
    return df
