#import scraping library and dataframe
from bs4 import BeautifulSoup 
import requests 
import pandas as pd 
from collections import OrderedDict

#selenium library
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


page = requests.get('http://www.envirostor.dtsc.ca.gov/public/deed_restrictions.asp')

soup = BeautifulSoup(page.content,'lxml')
driver = webdriver.Chrome()

global_df_1 = 0
global_df_2 = 0
global_df_3 = 0
#global_df_4 = 0
#sub link extraction

base_url = "http://www.envirostor.dtsc.ca.gov/public/"

count = 0
#tr = soup.find_all('tr')[20]
for tr in soup.find_all('tr')[4:]:
    #for testing purpose, can remove it for production.
    if count > 20: 
        break
    try:
        #Page 1 Scraping
        temp_dict = OrderedDict()
        tds = tr.find_all('td')
        
        temp_dict['SITENAME']   = tds[2].text
        temp_dict['AREA']       = tds[3].text
        temp_dict['SUB-AREA']   = tds[4].text
        temp_dict['SITE-TYPE']  = tds[5].text
        temp_dict['STATUS']     = tds[6].text
        temp_dict['ADDRESS']    = tds[7].text
        temp_dict['CITY']       = tds[8].text
        temp_dict['ZIP']        = tds[9].text
        temp_dict['CALENVIROSCREEN-SCORE']      = tds[10].text
        temp_dict['COUNTY']                     = tds[11].text
        temp_dict['DATE-RECORDED']              = tds[12].text
        
        #page2 Tab 1 ( Land Use Restriction)
        list_dict_page1 = list()
        
        page2 = base_url+str(tds[2].a['href'])
        
        #finding the Envirostor ID from the url
        find_me = 'global_id='
        start = str(page2).find(find_me)
        endofstart = len(find_me) + start
        find_me_e = '&'
        end = str(page2).find(find_me_e)
        envirostor_id = str(page2)[endofstart:end]
        
        temp_page = requests.get(page2)
        ssoup = BeautifulSoup(temp_page.content,'lxml') 
        table = ssoup.find_all('table',class_= 'display-v4-default')
        
        if len(table) < 1:
            table = ssoup.find_all('table',class_='panel-table')
            del table[0]
             
        for ninja in table: 
            second_dict = OrderedDict()        
            tr = ninja.find_all('tr')
            tds_ = tr[1].find_all('td')
            if len(tds_) == 3:
                second_dict['Envirostor ID']                = envirostor_id
                second_dict['AREA']                         = ' '
                second_dict['SUB_AREA']                     = ' '
                second_dict['Covenant']                     = base_url + str(tds[0].a['href'])
                second_dict['DATE RECORDED']                = tds_[1].text
                second_dict['SITE MANAGEMENT REQUIREMENTS'] = tds_[2].text   
            if len(tds_) == 5: 
                second_dict['Envirostor ID']                = envirostor_id
                second_dict['AREA']                         = tds_[0].text
                second_dict['SUB_AREA']                     = tds_[1].text
                second_dict['Covenant']                     = base_url + str(tds[2].a['href'])
                second_dict['DATE RECORDED']                = tds_[3].text
                second_dict['SITE MANAGEMENT REQUIREMENTS'] = tds_[4].text   
            
            list_dict_page1.append(second_dict)
        land_use_restriction_frame = pd.DataFrame.from_records(list_dict_page1)            
        
        #page2 Tab 2 & 3 (Future Activities, Completed)
        
        #selenium driver call for Chrome
        driver.get(page2)

        driver.find_element_by_id('activitiesTab').click()
        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="activities"]/div[1]/div')))

        html = driver.find_element_by_id('activities').get_attribute('innerHTML')
        sssoup = BeautifulSoup(html, 'lxml')
        div = sssoup.find_all('div', class_='panel-heading')
        table = sssoup.find_all('table', class_='display-v4-default')
        #if you table class display-v4_default is not available
        
        if (len(table) > 3) or (len(table) == 0): 
            table = soup.find_all('table',attrs = {'border':"0",'bordercolor':"#AAAAAA",'cellpadding':"2",'cellspacing':"0",'width':"100%"})
        
        list_of_dict_page2 = list()
        list_of_dict_page3 = list()
        list_of_dict_page4 = list()
        
        for tableindex in range(len(table)):
            if len(div) > 0 and str(div[tableindex].h5.text).strip('\n') == 'Future Activities': 
                
                tr = table[tableindex].find_all('tr')
                for trindex in range(len(tr)):
                    if trindex > 0:
                        try:
                            second_dict = OrderedDict()        
                            tds_ = tr[trindex].find_all('td')
                            if len(tds_) == 2:
                                second_dict['Envirostor ID']                = envirostor_id
                                second_dict['AREA']                         = temp_dict['AREA']
                                second_dict['SUB_AREA']                     = temp_dict['SUB-AREA']
                                second_dict['DOCUMENT_TYPE']                = tds_[0].text
                                second_dict['DUE DATE']                     = tds_[1].text
                                second_dict['ACTIVITY_TYPE']                = div[tableindex].h5.text
                                list_of_dict_page2.append(second_dict)
                            elif len(tds_) == 4: 
                                second_dict['Envirostor ID']                = envirostor_id
                                second_dict['AREA']                         = tds_[0].text
                                second_dict['SUB_AREA']                     = tds[1].text
                                second_dict['DOCUMENT_TYPE']                = tds_[2].text
                                second_dict['DUE DATE']                     = tds_[3].text
                                second_dict['ACTIVITY_TYPE']                = div[tableindex].h5.text
                                list_of_dict_page2.append(second_dict)
                        except Exception as e: 
                            print("Error in Future:"+str(e)+':'+len(tds_))
            if len(div) > 0 and div[tableindex].h5.text == 'Completed Activities': 
                
                tr = table[tableindex].find_all('tr')
                for trindex in range(len(tr)):
                    if trindex > 1:
                        try:
                            second_dict = OrderedDict()        
                            tds_ = tr[trindex].find_all('td')
                            if len(tds_) == 4:    
                                second_dict['Envirostor ID']                = envirostor_id
                                second_dict['DOC_LINK']                     = base_url+str(tds_[0].a['href'])
                                second_dict['DOCUMENT_TYPE']                = tds_[1].text
                                second_dict['DATE_COMPLETED']               = tds_[2].text 
                                second_dict['COMMENTS']                     = tds_[3].text
                                second_dict['ACTIVITY_TYPE']                = div[tableindex].h5.text
                                list_of_dict_page3.append(second_dict)
                            if len(tds_) == 6: 
                                second_dict['Envirostor ID']                = envirostor_id
                                second_dict['DOC_LINK']                     = base_url+str(tds_[2].a['href'])
                                second_dict['DOCUMENT_TYPE']                = tds_[3].text
                                second_dict['DATE_COMPLETED']               = tds_[4].text 
                                second_dict['COMMENTS']                     = tds_[5].text
                                second_dict['ACTIVITY_TYPE']                = div[tableindex].h5.text
                                list_of_dict_page3.append(second_dict)
                        except Exception as e:
                            print(str(e) +':Skipped the Row')
                            pass
                        
            if len(div) > 0 and "Currently Scheduled Activities"in str(div[tableindex].h5.text).strip('\n'):                        
                tr = table[tableindex].find_all('tr')
                for trindex in range(len(tr)):
                    if trindex > 0:
                        try:
                            second_dict = OrderedDict()
                            tds_ = tr[trindex].find_all('td')
                            
                            second_dict['Envirostor ID']                = envirostor_id
                            second_dict['DOCUMENT_TYPE']                = tds_[0].text
                            second_dict['DUE DATE']                     = tds_[1].text 
                            second_dict['REVISED DATE']                 = tds_[2].text
                            second_dict['ACTIVITY_TYPE']                = "Currently Scheduled Activities"
                            list_of_dict_page4.append(second_dict)
                        except Exception as e:
                            print(str(e) +':Skipped the Row')
                            pass
        
        secondTable = sssoup.find_all('table', class_='panel-table')
        list_of_dict_page5 = list()
        list_of_dict_page6 = list()
        list_of_dict_page7 = list()
       
        for table2index in range(len(secondTable)):    
            #overrid table variable
            #permitted units
            if len(div) > 0 and "Permitted Units" in str(div[table2index].h5.text).strip('\n'):
                tr = secondTable[table2index].find_all('tr')
                for trindex in range(len(tr)):
                    if trindex > 1:
                        try:
                            second_dict = OrderedDict()  
                            tds_ = tr[trindex].find_all('td')
                            
                            second_dict['Envirostor ID']                = envirostor_id
                            second_dict['UNIT']                         = tds_[0].text
                            second_dict['EVENT DESCRIPTION']            = tds_[1].text 
                            second_dict['DATE']                         = tds_[2].text 
                            second_dict['ACTIVITY_TYPE']                = "Permitted Units - Completed Activities"
                            list_of_dict_page5.append(second_dict)
                        except Exception as e:
                            print(str(e) +':Skipped the Row')
                            pass
            #units undergoing Closure
            if len(div) > 0 and "Units Undergoing Closure" in div[table2index].h5.text:
                
                tr = secondTable[table2index].find_all('tr')
                for trindex in range(len(tr)):
                    if trindex >= 0:
                        try:
                            second_dict = OrderedDict()        
                            tds_ = tr[trindex].find_all('td')
                            if(len(tds_) < 2):
                                second_dict['Envirostor ID']                = envirostor_id
                                second_dict['UNIT']                         = tds_[0].text
                                second_dict['EVENT DESCRIPTION']            = ' ' 
                                second_dict['DATE']                         = ' ' 
                                second_dict['ACTIVITY_TYPE']                = "Units Undergoing Closure - Completed Activities"
                                list_of_dict_page6.append(second_dict)
                            else: 
                                second_dict['Envirostor ID']                = envirostor_id
                                second_dict['UNIT']                         = tds_[0].text
                                second_dict['EVENT DESCRIPTION']            = tds_[1].text 
                                second_dict['DATE']                         = tds_[2].text 
                                second_dict['ACTIVITY_TYPE']                = "Units Undergoing Closure - Completed Activities"
                                list_of_dict_page6.append(second_dict)
                        except Exception as e:
                            print(str(e) +':Skipped the Row')
                            pass
            if len(div) > 0 and "Permit Maintenance" in div[table2index].h5.text:
                tr = secondTable[table2index].find_all('tr')
                for trindex in range(len(tr)):
                    if trindex > 1:
                        try:
                            second_dict = OrderedDict()       
                            tds_ = tr[trindex].find_all('td')           
                            second_dict['Envirostor ID']                = envirostor_id
                            second_dict['DOC_TYPE']                     = str(tds_[1].text).strip('\n').strip('\t')
                            second_dict['DOC_LINK']                     = base_url+str(tds_[0].a['href'])
                            second_dict['DATE COMPLETED']               = str(tds_[2].text).strip('\n').strip('\t') 
                            second_dict['ACTIVITY_TYPE']                = "Permit Maintenance - Completed Activities"
                            list_of_dict_page7.append(second_dict)
                    
                        except Exception as e:
                            print(str(e) +':Skipped the Row')
                            pass
                            
        future_frame = pd.DataFrame.from_records(list_of_dict_page2)
        completed_frame = pd.DataFrame.from_records(list_of_dict_page3)
        current_frame = pd.DataFrame.from_records(list_of_dict_page4)
        permitted_units = pd.DataFrame.from_records(list_of_dict_page5)
        units_undergoing = pd.DataFrame.from_records(list_of_dict_page6)
        permit_main = pd.DataFrame.from_records(list_of_dict_page7)
        
        if (count == 0): 
            global_df_1 = land_use_restriction_frame.copy(deep = True)
            global_df_2 = future_frame.copy(deep = True)
            global_df_3 = completed_frame.copy(deep = True)
            global_df_4 = current_frame.copy(deep = True)
            global_df_5 = permitted_units.copy(deep = True)
            global_df_6 = units_undergoing.copy(deep = True)
            global_df_7 = permit_main.copy(deep = True)
        if count > 0:
            global_df_1 = pd.concat([global_df_1,land_use_restriction_frame])
            global_df_2 = pd.concat([global_df_2,future_frame])
            global_df_3 = pd.concat([global_df_3,completed_frame])
            global_df_4 = pd.concat([global_df_4,current_frame])
            global_df_5 = pd.concat([global_df_5,permitted_units])
            global_df_6 = pd.concat([global_df_6,units_undergoing])
            global_df_7 = pd.concat([global_df_7,permit_main])    
        
    except Exception as e: 
        print("Some-Exception in the link:{}:Skipped Entirely".format(str(e)))
        pass
    finally:
        print("Row Number:{}".format(count))
        count += 1
   
#final_output -> to the execel sheet
try:    
    writer = pd.ExcelWriter('output.xlsx',engine='xlsxwriter')
    global_df_1.to_excel(writer,'Land_Use_Restrictions')
    global_df_2.to_excel(writer,'Future_Activities')
    global_df_3.to_excel(writer,'Completed_Activities')
    global_df_4.to_excel(writer,'Currently Scheduled Activities')
    global_df_5.to_excel(writer,'Permitted Units')
    global_df_6.to_excel(writer,'Units Undergoing Closure')
    global_df_7.to_excel(writer,'Permit Maintenance')
    writer.save() 
except Exception as e: 
    print(e)


