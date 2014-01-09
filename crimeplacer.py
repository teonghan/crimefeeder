#!/usr/bin/python
#----------------------------------------------
# filename      : crimeplacer.py
# description   : extracting place from article
# note          : for Python version 2.7
#----------------------------------------------

import nltk
import collections
import csv
import urllib, urllib2
import randomUserAgent
from bs4 import BeautifulSoup
import json
import datetime
import time
import codecs
import unicodecsv

#--------
# logging
#--------
flog=codecs.open('log','a+',encoding='utf-8')
flog.write(time.strftime("%d/%m/%Y %I:%M:%S")+': crimeplacer log started\n')

#------
# timer
#------
then=time.time()

#---------------------
# dealing with unicode
#---------------------
def to_unicode_or_bust(obj, encoding='utf-8'):
    if isinstance(obj, basestring):
        if not isinstance(obj, unicode):
            obj = unicode(obj, encoding)
    return obj

#----------------------
# function for method 1
#----------------------
def extract_entity_names(t):
    entity_names = []
    if hasattr(t, 'node') and t.node:
        if t.node == 'NE':
            entity_names.append(' '.join([child[0] for child in t]))
        else:
            for child in t:
                entity_names.extend(extract_entity_names(child))
    return entity_names

#----------------------
# function for method 2
#----------------------
def extract_entities(text):
    places=[]
    for sent in nltk.sent_tokenize(text):
        for chunk in nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(sent))):
            if hasattr(chunk,'node'):
                if chunk.node=='GPE':
                    places.append(' '.join(c[0] for c in chunk.leaves()))

    return places

#----------------------------------------------
# function to convert nltk tree to unicoded str
#----------------------------------------------
def tree_to_unicode(tree):
    obj=u''
    for i in tree:
        if hasattr(i,'node'):
            k=['/'.join(j) for j in i.leaves()]
            if obj==u'':
                obj=obj+i.node+' '+' '.join(k)
            else:
                obj=obj+'\n'+i.node+' '+' '.join(k)
        else:
            if obj==u'':
                obj=obj+i[0]+' '+i[1]
            else:
                obj=obj+'\n'+i[0]+' '+i[1]

    return obj

#------------------------------------------
# function to get chunks -> list of word(s)
#------------------------------------------
def dechunk(chunked_sentence):
    terms=[]
    for chunk in chunked_sentence:
        if hasattr(chunk,'node'):
            terms.append(' '.join(c[0] for c in chunk.leaves()))
        else:
            terms.append(chunk[0])

    return terms

'''
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
                except ExceptionToCheck, e:
                    msg = "%s, Retrying in %d seconds..." % (str(e), mdelay)
                    if logger:
                        logger.warning(msg)
                    else:
                        print msg
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return f(*args, **kwargs)

        return f_retry  # true decorator

    return deco_retry

@retry(urllib2.URLError, tries=4, delay=3, backoff=2)
def urlopen_with_retry(URL):
    opener=urllib2.build_opener()
    opener.addheaders=[('User-Agent', randomUserAgent.getUserAgent())]
    f=opener.open(URL)
    return f.read()
    
#--------------------------
# correlating with geonames
#--------------------------
def link_generator(term):
    term='+'.join(term.split())
    return 'http://api.geonames.org/searchJSON?q='+term+'&maxRows=999&country=MY&username=teonghan'

def link_generator_details(ID):
    return 'http://api.geonames.org/getJSON?geonameId='+str(ID)+'&username=teonghan'
    
def geonames(detected):
    
    places=[]

    bbox=0
    largest_bbox=0
    largest='Malaysia'

    for i in detected:
        url=link_generator(i)
        data=urlopen_with_retry(url)
        data=json.loads(data)

        if 'totalResultsCount' in data and data['totalResultsCount']>0:
            
            for j in data['geonames']:
                if j['name']==i.title():
                    url=link_generator_details(str(j['geonameId']))
                    data=urlopen_with_retry(url)
                    data=json.loads(data)
                    if 'bbox' in data.keys():
                        bbox=(data['bbox']['north']-data['bbox']['south'])*(data['bbox']['east']-data['bbox']['west'])
                        coor=[data['bbox']['north'],data['bbox']['south'],data['bbox']['east'],data['bbox']['west']]
                    else:
                        bbox=0
                        coor=[0,0,0,0]
                    if bbox < 0:
                        bbox=-bbox
                        
                    places.append([i,j['lat'],j['lng'],bbox,coor])

    return places                    

#--------------------------
# get info from google maps
#--------------------------
def google_maps(query):
    params={}
    params['sensor']="false"
    params['address']=query

    params=urllib.urlencode(params)

    f=urlopen_with_retry("https://maps.googleapis.com/maps/api/geocode/json?%s" % params)
    return json.loads(f)
'''
#-------------------------------
# reading csv (using unicodecsv)
#-------------------------------
filename='pos_crime_category.csv'
data=[]
with open(filename, 'r') as csvfile:
    csvreader = unicodecsv.reader(csvfile, delimiter='\t', encoding='utf-8')
    for row in csvreader:
        if row[0]!='NO':
            data.append(row)

#---------
# output
#---------
#fout=codecs.open('pos_crime_category_places.txt','w',encoding='utf-8')
fcsv=codecs.open('pos_crime_category_places.csv','w',encoding='utf-8')

fcsv.write(to_unicode_or_bust('NO\tTITLE\tSOURCE\tLINK\tFULL_TEXT\tDATE\tTYPE\tPLACES\tFALLBACK\n'))

#-----------------
# reading keywords
#-----------------
f=open('keys','r')
keywords=f.readlines()
f.close
keywords=[i.strip() for i in keywords]

#-------------------------------
# reading wrongly detected place
#-------------------------------
f=open('wrong','r')
wrong=f.readlines()
f.close
wrong=[i.strip() for i in wrong]

#-----------------
# detecting places
#-----------------
finalized={}

count=0
for i in data:
    number=i[0]
    title=i[1]
    source=i[2]
    link=i[3]
    text=i[4]
    date=i[5]
    category=i[6]
    
    sentences = nltk.sent_tokenize(text)

    tokenized_sentences = [nltk.word_tokenize(sentence) for sentence in sentences]
    tagged_sentences = [nltk.pos_tag(sentence) for sentence in tokenized_sentences]
    chunked_sentences = nltk.batch_ne_chunk(tagged_sentences, binary=True)
     
    entity_names = []

    #-----------------------------------
    # simple place extraction (fallback)
    #-----------------------------------
    fallback=[]
    
    textlist=text.split(':')

    #fout.write(title+'\n')

    if len(textlist)==1:
        pass

    elif len(textlist)==2 and textlist[0].strip().isupper():
        fallback.append(textlist[0].strip())

    elif len(textlist)>=4 and textlist[2].strip().isupper():
        fallback.append(textlist[2].strip())

    else:
        for split in textlist:
            if split.strip().isupper():
                fallback.append(split)
    
    #-------------------------------
    # more accurate place extraction
    #-------------------------------
    accurate=[]
    
    for i in range(0,len(chunked_sentences)):
        tree=chunked_sentences[i]
        sentence=sentences[i]
        entities=extract_entity_names(tree)
        termlist=dechunk(tree)

        if any(keyword in sentence for keyword in keywords):
                
            if len(entities)!=0:

                if 'at' in termlist and 'in' in termlist:
                    for entity in entities:
                        if not any(item.lower() in entity.lower() for item in wrong):
                            index_entity=termlist.index(entity)
                            if termlist[index_entity-1] == 'at' or \
                               termlist[index_entity-2] == 'at' or \
                               termlist[index_entity-1] == 'in' or \
                               termlist[index_entity-2] == 'in':

                                for i in range(index_entity+1,len(tree)):

                                    if type(tree[i])==tuple and tree[i][1]=='NNP':
                                        entity=entity+' '+tree[i][0]
                                    else:
                                        break
                               
                                accurate.append(entity)

                                #new_tree=tree_to_unicode(tree)
                                #fout.write(new_tree)

                elif 'in' in termlist and 'at' not in termlist:
                    for entity in entities:
                        if not any(item.lower() in entity.lower() for item in wrong):
                            index_entity=termlist.index(entity)
                            if termlist[index_entity-1] == 'in' or \
                               termlist[index_entity-2] == 'in':

                                for i in range(index_entity+1,len(tree)):

                                    if type(tree[i])==tuple and tree[i][1]=='NNP':
                                        entity=entity+' '+tree[i][0]
                                    else:
                                        break

                                accurate.append(entity)

                                #new_tree=tree_to_unicode(tree)
                                #fout.write(new_tree)

                elif 'at' in termlist and 'in' not in termlist:
                    for entity in entities:
                        if not any(item.lower() in entity.lower() for item in wrong):
                            index_entity=termlist.index(entity)
                            if termlist[index_entity-1] == 'at' or \
                               termlist[index_entity-2] == 'at':
                                
                                for i in range(index_entity+1,len(tree)):

                                    if type(tree[i])==tuple and tree[i][1]=='NNP':
                                        entity=entity+' '+tree[i][0]
                                    else:
                                        break
                                    
                                accurate.append(entity)

                                #new_tree=tree_to_unicode(tree)
                                #fout.write(new_tree)

                elif 'in' not in termlist and 'at' not in termlist:

                    if 'near' in termlist:

                        for entity in entities:

                            if not any(item.lower() in entity.lower() for item in wrong):
                                index_entity=termlist.index(entity)
                                if termlist[index_entity-1] == 'near' or \
                                   termlist[index_entity-2] == 'near':
                                    
                                    for i in range(index_entity+1,len(tree)):

                                        if type(tree[i])==tuple and tree[i][1]=='NNP':
                                            entity=entity+' '+tree[i][0]
                                        else:
                                            break
                                        
                                    accurate.append(entity)

                                    #new_tree=tree_to_unicode(tree)
                                    #fout.write(new_tree)

                    elif 'into' in termlist:

                        for entity in entities:

                            if not any(item.lower() in entity.lower() for item in wrong):
                                index_entity=termlist.index(entity)
                                if termlist[index_entity-1] == 'into' or \
                                   termlist[index_entity-2] == 'into':
                                    
                                    for i in range(index_entity+1,len(tree)):

                                        if type(tree[i])==tuple and tree[i][1]=='NNP':
                                            entity=entity+' '+tree[i][0]
                                        else:
                                            break
                                        
                                    accurate.append(entity)

                                    #new_tree=tree_to_unicode(tree)
                                    #fout.write(new_tree)

        #entity_names.extend(extract_entity_names(tree))

    ''' 
    detected=[]
    for i in entity_names:
        if i not in detected:
            detected.append(i)
    
    for i in extract_entities(text):
        if i not in detected:
            detected.append(i)
    '''

    if len(accurate)==0:
        accurate=['NA','NA']

        '''
        fout.write(title+'\n')
        for i in range(0,len(chunked_sentences)):
            tree=chunked_sentences[i]
            sentence=sentences[i]
            entities=extract_entity_names(tree)
            termlist=dechunk(tree)

            fout.write(str(tree)+'\n')
            fout.write(str(entities)+'\n')
        '''
        
    elif len(accurate)==1:
        accurate.append('NA')

    if len(fallback)==0:
        fallback=['NA']

    places=';'.join(accurate)

    fcsv.write(number+'\t'+title+'\t'+source+'\t'+link+'\t'+text+'\t'+date+'\t'+category+'\t'+places+'\t'+fallback[0]+'\n')
    #fout.write('\n')

    count+=1

#fout.close()
fcsv.close()

flog.write(time.strftime("%d/%m/%Y %I:%M:%S")+': total news: %s\n' % len(data))
flog.write(time.strftime("%d/%m/%Y %I:%M:%S")+': Total detected: %s\n' % count)
#------
# timer
#------
now=time.time()

flog.write(time.strftime("%d/%m/%Y %I:%M:%S")+': %s (HH:MM:SS) elapsed...\n' % str(datetime.timedelta(seconds=now-then)))
flog.write(time.strftime("%d/%m/%Y %I:%M:%S")+': crimeplacer log ended\n')

flog.close()
