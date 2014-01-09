#!/usr/bin/python3
#----------------------------------------------------
# filename      : crimextrator.py
# description   : scrapping news from NST and TheStar
# note          : best used with Python3
#----------------------------------------------------

import randomUserAgent
import time
import datetime
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import urllib.request
import csv
import re

#--------
# logging
#--------
flog=open('log','a+',encoding='utf-8')
flog.write(time.strftime("%d/%m/%Y %I:%M:%S")+': crimextractor log started\n')

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

#---------------------------
# Get the previous last news
#---------------------------
f=open('last_star.csv','r',encoding='utf-8')
last_star=f.readline().strip().split('\t')
f.close()

f=open('last_nst.csv','r',encoding='utf-8')
last_nst=f.readline().strip().split('\t')
f.close()

f=open('last_sarawak.csv','r',encoding='utf-8')
last_sarawak=f.readline().strip().split('\t')
f.close()

f=open('last_sabah.csv','r',encoding='utf-8')
last_sabah=f.readline().strip().split('\t')
f.close()

if last_star==['']:
    last_star=['','','','','','']
if last_nst==['']:
    last_nst=['','','','','','']
if last_sarawak==['']:
    last_sarawak=['','','','','','']
if last_sabah==['']:
    last_sabah=['','','','','','']

#----------------
# The Star Online
#----------------
flog.write(time.strftime("%d/%m/%Y %I:%M:%S")+': mining from TheStar...\n')

# function for page detection in thestar
def detect_page(x):
    return "content_0_newslandingpage_main_1_twocolumnleftfocus_a_left_0_pagination_rptPagination_ctl0"+str(x)+"_lbpage"

url='http://www.thestar.com.my/News/Latest.aspx'
nation='content_0_newslandingpage_main_1_twocolumnleftfocus_a_left_0_ListViewCategory_ctrl1_lbShowLatest'

titles={}
texts={}
links={}
dates={}

driver=webdriver.Firefox()
driver.get(url)

# Check latest nation news
nation_trigger=False
wait_time=0

while nation_trigger==False:
    element=driver.find_element_by_id(nation)
    if element.get_attribute('class')!='active' and wait_time <= 30:
        action=ActionChains(driver).move_to_element(element)
        action.click()
        action.perform()
        
        wait_time=wait_time+10
        time.sleep(wait_time)
    else:
        page_nation=element.get_attribute('class')
        nation_trigger=True

flog.write(time.strftime("%d/%m/%Y %I:%M:%S")+': wait time for page_nation %s\n' % wait_time)

if page_nation=='active':
    count=0
    proceed=True
    
    for i in range(1,6):

        if proceed==True:
            page_trigger=False
            wait_time=0

            while page_trigger==False:
                elements=driver.find_elements_by_tag_name('a')

                for element in elements:
                    if element.get_attribute('id')==detect_page(i):
                        break
                
                if element.get_attribute('class')!='current' and wait_time <= 30:
                    action=ActionChains(driver).move_to_element(element)
                    action.click()
                    action.perform()
                    
                    wait_time=wait_time+10
                    time.sleep(wait_time)
                else:
                    page_current=element.get_attribute('class')
                    page_trigger=True

            if page_current=='current':

                # Get da news!
                elements=driver.find_elements_by_tag_name('a')

                for element in elements:
                    attribute=element.get_attribute('id')
                    start='content_0_newslandingpage_main_1_twocolumnleftfocus_a_left_0_ListView'
                    end='hpHeadline'

                    if attribute[0:len(start)]==start and attribute[-(len(end)):]==end and element.text!='':
                        text=element.text
                        link=element.get_attribute('href')
                        
                        if text[0:len('ONLINE EXECUTIVE')]=='ONLINE EXECUTIVE':
                            text=text[len('ONLINE EXECUTIVE')::].strip()

                        if text!=last_star[1] and link!=last_star[3]:
                            count+=1
                            titles[count]=text
                            links[count]=link

                        else:
                            proceed=False
                            break

                flog.write(time.strftime("%d/%m/%Y %I:%M:%S")+': wait time for page %s %s\n' % (i,wait_time))
                    
            else:
                flog.write(time.strftime("%d/%m/%Y %I:%M:%S")+': page %s not active after 3 trials\n' % i)

    flog.write(time.strftime("%d/%m/%Y %I:%M:%S")+': %s news extracted...\n' % (count))

elif page_nation!='active':
    flog.write(time.strftime("%d/%m/%Y %I:%M:%S")+': page_nation not active after 3 trials\n')

# Close webdriver
driver.close()

# Get the full stories
if page_nation=='active':
    for i in links:
        f=urlopen_with_retry(links[i])
        soup=BeautifulSoup(f)
        story=soup.find('div',{'class':'story'})
        
        text=story.get_text()
        text=''.join(text.split('\r'))
        text='\n'.join(text.split('\n\n'))
        text=' '.join(text.split('\n'))
        text=text.replace('\xa0',' ')
        text=text.strip()

        if not ('other news & views is compiled from the vernacular newspapers' in text.lower() or \
                'found in translation is compiled from the vernacular newspapers' in text.lower()):
            texts[i]=text

        else:
            texts[i]=''

        date=soup.find('p',{'class':'date'})
        date=date.get_text()
        date=date.split('\r\n                ')
        date=date[2]

        timestamp=date.split(' MYT ')[1]
        date=date.split(' MYT ')[0]
        
        date=date.split()
        date=date[1:]
        date[1]=date[1][:-1]
        date='-'.join(date)

        date=datetime.datetime.strptime(date, '%B-%d-%Y')
        date=date.strftime('%m/%d/%Y')
        
        timestamp=timestamp.split(':')
        tmp=timestamp[2].split()
        timestamp=timestamp[0:2]
        timestamp.extend(tmp)
        timestamp=':'.join(timestamp)

        dates[i]=date+';'+timestamp

    flog.write(time.strftime("%d/%m/%Y %I:%M:%S")+': %s full texts retrieved...\n' % (len(texts)))

    fstar=open('output_star.csv','w',encoding='utf-8')
    fstar.write('NO\tTITLE\tSOURCE\tLINK\tFULL_TEXT\tDATE\n')

    for i in titles:
        if texts[i]!='':
            fstar.write('%s\t%s\t%s\t%s\t%s\t%s\n' % (i,titles[i],'TheStar',links[i],texts[i],dates[i]))
    fstar.close()

    fstar=open('last_star.csv','w',encoding='utf-8')
    for i in titles:
        if texts[i]!='':
            fstar.write('%s\t%s\t%s\t%s\t%s\t%s\n' % (i,titles[i],'TheStar',links[i],texts[i],dates[i]))
            break
    fstar.close()

#elif page_nation!='active':
#    fstar=open('output_star.csv','w',encoding='utf-8')
#    fstar.close()
    
#------------------
# New Straits Times
#------------------
flog.write(time.strftime("%d/%m/%Y %I:%M:%S")+': mining from NST...\n')

url='http://www.nst.com.my/nation'

titles={}
texts={}
links={}
dates={}

driver=webdriver.Firefox()
driver.get(url)

# Check latest nation news page by page
count=0
proceed=True

for i in range(1,11):
    if proceed==True:
        element=driver.find_element_by_xpath("//div[@class='page_navigation']")

        page_trigger=False
        wait_time=0    

        while page_trigger==False:
            elements=driver.find_elements_by_tag_name('a')

            for element in elements:
                if element.text==str(i):
                    break
        
            if element.get_attribute('class')!='page_link first active_page' and wait_time <= 30:
                action=ActionChains(driver).move_to_element(element)
                action.click()
                action.perform()

                wait_time=wait_time+10
                time.sleep(wait_time)
            else:
                page_trigger=True

        if element.get_attribute('class')=='page_link first active_page' and element.text==str(i):

            flog.write(time.strftime("%d/%m/%Y %I:%M:%S")+': wait time for page %s %s\n' % (i,wait_time))
            
            elements=driver.find_elements_by_xpath("//div[@class='news-content']")
            for element in elements:
                sub_element=element.find_element_by_tag_name('a')

                text=sub_element.text
                link=sub_element.get_attribute('href')

                if text!=last_nst[1] and link!=last_nst[3]:
                    count+=1
                    titles[count]=text
                    links[count]=link
                else:
                    proceed=False
                    break

        else:
            flog.write(time.strftime("%d/%m/%Y %I:%M:%S")+': page %s not active after 3 trials\n' % i)

# Close webdriver
driver.close()
     
flog.write(time.strftime("%d/%m/%Y %I:%M:%S")+': %s news extracted...\n' % (count))

# Get the full stories
for i in links:
    text_soup=None

    while text_soup==None:
        f=urlopen_with_retry(links[i])
        soup=BeautifulSoup(f)
        text_soup=soup.find('div',{'class':'news-article'})

    text=''

    if text_soup.find('h2'):
        story=text_soup.find('h2')
        text=story.get_text()+':'
    
    story=text_soup.findAll('p')
    for a in story:
        if not a.find('class'):
            text=text+a.get_text()
    
    text=''.join(text.split('\r'))
    text='\n'.join(text.split('\n\n'))
    text=' '.join(text.split('\n'))
    text=text.replace('\xa0',' ')
    text=text.replace('\t','')
    text=text.strip()

    texts[i]=text

    date=soup.find('div',{'class':'article-date'})
    date=date.get_text()
    date=date.split('\n\n')
    date=date[1]
    timestamp=date.split('| last updated at ')[1]
    date=date.split('| last updated at ')[0]

    timestamp=timestamp.strip()
    timestamp=timestamp.split(':')
    timestamp=':'.join([timestamp[0],timestamp[1][:-2],timestamp[1][2:]])

    date=datetime.datetime.strptime(date, '%d %B %Y')
    date=date.strftime('%m/%d/%Y')

    dates[i]=date+';'+timestamp

flog.write(time.strftime("%d/%m/%Y %I:%M:%S")+': %s full texts retrieved...\n' % (len(texts)))
fnst=open('output_nst.csv','w',encoding='utf-8')
fnst.write('NO\tTITLE\tSOURCE\tLINK\tFULL_TEXT\tDATE\n')

for i in titles:
    fnst.write('%s\t%s\t%s\t%s\t%s\t%s\n' % (i,titles[i],'NST',links[i],texts[i],dates[i]))
fnst.close()

if count>0:
    fnst=open('last_nst.csv','w',encoding='utf-8')
    for i in titles:
        fnst.write('%s\t%s\t%s\t%s\t%s\t%s\n' % (i,titles[i],'NST',links[i],texts[i],dates[i]))
        break
    fnst.close()

#--------------------
# Sarawak Borneo Post
#--------------------
flog.write(time.strftime("%d/%m/%Y %I:%M:%S")+': mining from BP (Sarawak)...\n')

titles={}
texts={}
links={}
dates={}

def page_generator(word):
    tmp=[]
    string='http://www.theborneopost.com/news/'+word+'/'
    tmp.append(string)
    for i in range(2,11):
        tmp.append(string+'page/'+str(i))
    return tmp

proceed=True
count=0

pages=page_generator('sarawak')
for i in pages:
    if proceed:
        catList=None

        while catList==None:
            f=urlopen_with_retry(i)
            soup=BeautifulSoup(f)
            catList=soup.find('div',{'class':'catList'})

        List=catList.find_all('h3')

        for j in List:
            try:
                tmp=j.find('a')
                TITLE=tmp.get_text()
                LINK=tmp.get('href')

                if TITLE!=last_sarawak[1] and LINK!=last_sarawak[3]:
                    count+=1
                    titles[count]=TITLE
                    links[count]=LINK
                else:
                    proceed=False
                    break

            except:
                pass
            
for i in links:

    div=None

    while div==None:
        f=urlopen_with_retry(links[i])
        soup=BeautifulSoup(f)
        div=soup.find('div',attrs={'class':'newsBody floatLeft'})
    
    text=div.findAll('p')
    fulltext=''
    for j in text:
        if j.findChild('em'):
            pass
        elif j.has_attr('class'):
            if j.attrs['class']==['newsInfo']:
                timestamp=''.join(j.get_text()[j.get_text().index('Posted on ')+len('Posted on '):].split(',')[0:-1])
                timestamp=datetime.datetime.strptime(timestamp,'%B %d %Y')
                date=timestamp.strftime('%m/%d/%Y')
                dates[i]=date+';'+':'.join(['12','00','AM'])
            pass
        elif j.has_attr('style'):
            pass
        else:
            fulltext=fulltext+j.get_text()

    texts[i]=fulltext

flog.write(time.strftime("%d/%m/%Y %I:%M:%S")+': %s full texts retrieved...\n' % (len(texts)))
fsrw=open('output_sarawak.csv','w',encoding='utf-8')
fsrw.write('NO\tTITLE\tSOURCE\tLINK\tFULL_TEXT\tDATE\n')

for i in titles:
    fsrw.write('%s\t%s\t%s\t%s\t%s\t%s\n' % (i,titles[i],'BP',links[i],texts[i],dates[i]))
fsrw.close()

if count>0:
    fsrw=open('last_sarawak.csv','w',encoding='utf-8')
    for i in titles:
        fsrw.write('%s\t%s\t%s\t%s\t%s\t%s\n' % (i,titles[i],'BP',links[i],texts[i],dates[i]))
        fsrw.close()
        break

#------------------
# Sabah Borneo Post
#------------------
flog.write(time.strftime("%d/%m/%Y %I:%M:%S")+': mining from BP (Sabah)...\n')

titles={}
texts={}
links={}
dates={}
count=0

proceed=True

pages=page_generator('sabah')
for i in pages:
    if proceed:
        catList=None

        while catList==None:
            f=urlopen_with_retry(i)
            soup=BeautifulSoup(f)
            catList=soup.find('div',{'class':'catList'})

        List=catList.find_all('h3')

        for j in List:
            try:
                tmp=j.find('a')
                TITLE=tmp.get_text()
                LINK=tmp.get('href')

                if TITLE!=last_sabah[1] and LINK!=last_sabah[3]:
                    count+=1
                    titles[count]=TITLE
                    links[count]=LINK
                else:
                    proceed=False
                    break

            except:
                pass

for i in links:

    div=None

    while div==None:
        f=urlopen_with_retry(links[i])
        soup=BeautifulSoup(f)
        div=soup.find('div',attrs={'class':'newsBody floatLeft'})

    text=div.findAll('p')
    fulltext=''
    for j in text:
        if j.findChild('em'):
            pass
        elif j.has_attr('class'):
            if j.attrs['class']==['newsInfo']:
                timestamp=''.join(j.get_text()[j.get_text().index('Posted on ')+len('Posted on '):].split(',')[0:-1])
                timestamp=datetime.datetime.strptime(timestamp,'%B %d %Y')
                date=timestamp.strftime('%m/%d/%Y')
                dates[i]=date+';'+':'.join(['12','00','AM'])
            pass
        elif j.has_attr('style'):
            pass
        else:
            fulltext=fulltext+j.get_text()

    texts[i]=fulltext

flog.write(time.strftime("%d/%m/%Y %I:%M:%S")+': %s full texts retrieved...\n' % (len(texts)))
fsbh=open('output_sabah.csv','w',encoding='utf-8')
fsbh.write('NO\tTITLE\tSOURCE\tLINK\tFULL_TEXT\tDATE\n')

for i in titles:
    fsbh.write('%s\t%s\t%s\t%s\t%s\t%s\n' % (i,titles[i],'BP',links[i],texts[i],dates[i]))
fsbh.close()

if count>0:
    fsbh=open('last_sabah.csv','w',encoding='utf-8')
    for i in titles:
        fsbh.write('%s\t%s\t%s\t%s\t%s\t%s\n' % (i,titles[i],'BP',links[i],texts[i],dates[i]))
        fsbh.close()
        break

#------
# timer
#------
now=time.time()

flog.write(time.strftime("%d/%m/%Y %I:%M:%S")+': %s (HH:MM:SS) elapsed...\n' % str(datetime.timedelta(seconds=now-then)))
flog.write(time.strftime("%d/%m/%Y %I:%M:%S")+': crimextractor log ended\n')

flog.close()

