#!/usr/bin/python3
#----------------------------------------------------
# filename      : crimefeeder.py
# description   : inject into crimefeeds @ mapping.fbb
# note          : best used with Python3
#----------------------------------------------------
import randomUserAgent
import time
import datetime
from selenium import webdriver
import selenium
from bs4 import BeautifulSoup
import urllib.request
import json
import time
import datetime
import csv

#--------
# logging
#--------
flog=open('log','a+',encoding='utf-8')
flog.write(time.strftime("%d/%m/%Y %I:%M:%S")+': crimefeeder log started\n')

#------
# timer
#------
then=time.time()

#---------------------
# retrying url request
#---------------------
import time
from functools import wraps

def retry(ExceptionToCheck, tries=4, delay=3, backoff=2, logger=None):
    """Retry calling the decorated function using an exponential backoff.

    http://www.saltycrane.com/blog/2009/11/trying-out-retry-decorator-python/
    original from: http://wiki.python.org/moin/PythonDecoratorLibrary#Retry

    :param ExceptionToCheck: the exception to check. may be a tuple of
        exceptions to check
    :type ExceptionToCheck: Exception or tuple
    :param tries: number of times to try (not retry) before giving up
    :type tries: int
    :param delay: initial delay between retries in seconds
    :type delay: int
    :param backoff: backoff multiplier e.g. value of 2 will double the delay
        each retry
    :type backoff: int
    :param logger: logger to use. If None, print
    :type logger: logging.Logger instance
    """
    def deco_retry(f):

        @wraps(f)
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                except ExceptionToCheck:
                    msg = "%s, Retrying in %d seconds..." % (str(ExceptionToCheck), mdelay)
                    if logger:
                        logger.warning(msg)
                    else:
                        print(msg)
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return f(*args, **kwargs)

        return f_retry  # true decorator

    return deco_retry

@retry(urllib.error.URLError, tries=4, delay=3, backoff=2)
def urlopen_with_retry(URL):
    opener=urllib.request.build_opener()
    opener.addheaders=[('User-Agent', randomUserAgent.getUserAgent())]
    f=opener.open(URL)
    return f.read()

#--------------------------
# get info from google maps
#--------------------------
def google_maps(query):
    params={}
    params['sensor']="false"
    params['address']=query

    params=urllib.parse.urlencode(params)

    f=urlopen_with_retry("https://maps.googleapis.com/maps/api/geocode/json?%s" % params)
    return json.loads(f.decode())

#---------------------
# read from places.csv
#---------------------
data=[]
filename='pos_crime_category_places.csv'
with open(filename, 'r') as csvfile:
    csvreader = csv.reader(csvfile, delimiter='\t')
    for row in csvreader:
        if row[0]!='NO':
            data.append(row[1::])

#----------------
# reading aliases
#----------------
aliases={}
with open('aliases', 'r') as csvfile:
    csvreader = csv.reader(csvfile, delimiter='\t')
    for row in csvreader:
        aliases[row[0]]=row[1]
        
'''
#----------------
# geocoded output
#----------------
fout=open('geocoded.csv','w')
fout.write('TITLE\tSOURCE\tLINK\tFULL_TEXT\tDATE\tPLACE\tLAT\tLONG\tFULL_ADDRESS\n')

#-----
# Main
#-----
for i in data:
    places=i[5].split(';')
    places.append(i[6])
    places=list(filter(('NA').__ne__, places))
    for j in places:
        results=google_maps(j)
        result=results['results'][0]
        full_address=result['formatted_address']
        lat=result['geometry']['location']['lat']
        lng=result['geometry']['location']['lng']

        if j in full_address:
            fout.write('\t'.join(i[0:4]))
            fout.write('\t'.join([j,str(lat),str(lng),full_address]))
            fout.write('\n')
            break

fout.close()
'''

#-----
# Main
#-----
#category
# value 1: ACCIDENT
# value 2: VIOLENT
# value 3: PROPERTY
# value 4: TRUSTED
# value 5: ???
# value 6: SEXUAL
# value 7: OTHERS

category_dict={'ACCIDENT':'1','VIOLENT':'2','PROPERTY':'3','TRUSTED':'4',
               'SEXUAL':'6','OTHERS':'7'}

url='http://mapping.fbb.utm.my/crimefeeds/v2/reports/submit'
driver=webdriver.Firefox()

firstname='feeder'
lastname='crime'
email='crimefeeder7@gmail.com'

for i in data:
    driver.get(url)

    TITLE=i[0]
    LINK=i[2]
    DESC=i[3]
    DATE=i[4].split(';')[0]
    TIME=i[4].split(';')[1].split(':')
    CATEGORY=i[5]
    
    PLACES=i[6].split(';')
    PLACES.append(i[7])
    PLACES=list(filter(('NA').__ne__, PLACES))

    # title
    title=driver.find_element_by_id('incident_title')
    title.clear()
    title.send_keys(TITLE)

    # description
    description=driver.find_element_by_id('incident_description')
    description.clear()
    description.send_keys(DESC)

    modify_date=driver.find_element_by_id('date_toggle')
    modify_date.click()
    time.sleep(3)

    # dates
    incident_date=driver.find_element_by_id('incident_date')
    incident_date.clear()
    incident_date.send_keys(DATE)

    # Google chrome problem
    #datepicker=driver.find_element_by_class_name('ui-datepicker-trigger')
    #datepicker.click()
    
    # hours
    hour=driver.find_element_by_id('incident_hour')
    allOptions=hour.find_elements_by_tag_name('option')
    for option in allOptions:
        if option.get_attribute('value')==TIME[0]:
            option.click()
            break

    # minutes
    minute=driver.find_element_by_id('incident_minute')
    allOptions=minute.find_elements_by_tag_name('option')
    for option in allOptions:
        if option.get_attribute('value')==TIME[1]:
            option.click()
            break

    # am/pm
    ampm=driver.find_element_by_id('incident_ampm')
    allOptions=ampm.find_elements_by_tag_name('option')
    for option in allOptions:
        if option.get_attribute('value')==TIME[2]:
            option.click()
            break

    # firstname
    first=driver.find_element_by_id('person_first')
    first.clear()
    first.send_keys(firstname)

    # lastname
    last=driver.find_element_by_id('person_last')
    last.clear()
    last.send_keys(lastname)

    # email
    mail=driver.find_element_by_id('person_email')
    mail.clear()
    mail.send_keys(email)

    # link
    link=driver.find_element_by_name('incident_news[]')
    link.clear()
    link.send_keys(LINK)

    # button submit
    btn_submit=driver.find_element_by_class_name('btn_submit')

    # location
    location_find=driver.find_element_by_name('location_find')
    btn_find=driver.find_element_by_class_name('btn_find')
    
    category_elements=driver.find_elements_by_name('incident_category[]')
    for element in category_elements:
        if element.get_attribute('value')==category_dict[CATEGORY]:
            element.click()
        elif element.get_attribute('value')==category_dict['TRUSTED']:
            element.click()
    
    for j in PLACES:
        '''
        alias_trigger=False
        
        # dealing with aliases
        if j.lower() in aliases:
            alias=aliases[j.lower()]
            alias_trigger=True
        '''
        
        submitted=False
        location_find.clear()

        '''
        if alias_trigger:
            location_find.send_keys(alias)
        else:
        '''

        location_find.send_keys(j+' Malaysia')
        btn_find.click()
        loading=driver.find_element_by_id('find_loading')

        location_trigger=False
        wait_time=0
        
        while location_trigger==False:
            time.sleep(30)

            try:
                loading.find_element_by_tag_name('img')
                if loading.find_element_by_tag_name('img') and wait_time <= 30:
                    wait_time=wait_time+10
                    time.sleep(wait_time)
                    btn_find.click()
                else:
                    location_trigger=True
            except:
                location_trigger=True
                
        try:
            alert=driver.switch_to_alert()
            alert.accept()
            
        except:
            location_name=driver.find_element_by_name('location_name')
            address=location_name.get_attribute('value')
            
            if j.lower() in address.lower() and 'Malaysia' in address:
                btn_submit.click()
                time.sleep(30)
                try:
                    error_str=driver.find_element_by_class_name('red-box').text
                    if 'Error!' in error_str:
                        submitted=False
                        break
                except:
                    try:
                        submit_str=driver.find_element_by_tag_name('h3').text
                        if 'Your Report has been submitted' in submit_str:
                            submitted=True
                            break
                    except:
                        btn_submit.click()
                        time.sleep(30)

    if submitted==False:
        flog.write(time.strftime("%d/%m/%Y %I:%M:%S")+': news %s failed to submit\n' % TITLE)

driver.close()

#------
# timer
#------
now=time.time()

flog.write(time.strftime("%d/%m/%Y %I:%M:%S")+': %s (HH:MM:SS) elapsed...\n' % str(datetime.timedelta(seconds=now-then)))
flog.write(time.strftime("%d/%m/%Y %I:%M:%S")+': crimefeeder log ended\n')

flog.close()
