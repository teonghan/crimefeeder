#!/usr/bin/python
#----------------------------------------------------
# filename      : crimeclassifier.py
# description   : classify crime into 5 categories
# note          : best used with Python
# credits       : Jacob Perkins & Jim Plush
#----------------------------------------------------

import collections, itertools
import nltk.classify.util, nltk.metrics
from nltk.classify import NaiveBayesClassifier
from nltk.corpus import movie_reviews, stopwords
from nltk.collocations import BigramCollocationFinder
from nltk.metrics import BigramAssocMeasures
from nltk.probability import FreqDist, ConditionalFreqDist
from nltk.stem import PorterStemmer
from nltk.tokenize import WordPunctTokenizer
import unicodecsv
import codecs
import glob
import datetime
import time

#--------
# logging
#--------
flog=codecs.open('log','a+',encoding='utf-8')
flog.write(time.strftime("%d/%m/%Y %I:%M:%S")+': crimeclassifier log started\n')

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

def get_feature(word):
    return dict([(word, True)])

def bag_of_words(words):
    return dict([(word, True) for word in words])

def extract_words(text):
    stemmer = PorterStemmer()

    tokenizer = WordPunctTokenizer()
    tokens = tokenizer.tokenize(text)

    result =  [stemmer.stem(x.lower()) for x in tokens if x not in stopwords.words('english') and len(x) > 1]
    return result

def extract_words_bigram(text,chi_score):
    '''
    here we are extracting features to use in our classifier. We want to pull all the words in our input
    porterstem them and grab the most significant bigrams to add to the mix as well.
    '''

    stemmer = PorterStemmer()

    tokenizer = WordPunctTokenizer()
    tokens = tokenizer.tokenize(text)

    bigram_finder = BigramCollocationFinder.from_words(tokens)
    bigrams = bigram_finder.nbest(BigramAssocMeasures.chi_sq, chi_score)

    for bigram_tuple in bigrams:
        x = "%s %s" % bigram_tuple
        tokens.append(x)

    result =  [stemmer.stem(x.lower()) for x in tokens if x not in stopwords.words('english') and len(x) > 1]
    return result
#-------------------------------
# Main loop (crime vs non-crime)
#-------------------------------
texts = {}
texts['crime'] = ''
texts['non-crime'] = ''

#-------------------------------
# reading csv (using unicodecsv)
#-------------------------------
filename='./classification/train_pos.csv'
with open(filename, 'r') as csvfile:
    csvreader = unicodecsv.reader(csvfile, delimiter=',', encoding='utf-8')
    for row in csvreader:
        if row[0]!='NO':
            texts['crime']=texts['crime']+'\n'+row[4]

filename='./classification/train_neg.csv'
with open(filename, 'r') as csvfile:
    csvreader = unicodecsv.reader(csvfile, delimiter=',', encoding='utf-8')
    for row in csvreader:
        if row[0]!='NO':
            texts['non-crime']=texts['non-crime']+'\n'+row[4]

train_set = []

for sense, text in texts.iteritems():
    features = extract_words_bigram(text,500)
    train_set = train_set + [(get_feature(word), sense) for word in features]

classifier = NaiveBayesClassifier.train(train_set)

#-------------------
# categorize loop #1
#-------------------
files=['output_nst.csv','output_star.csv','output_sabah.csv','output_sarawak.csv']
POS=[]
for f in files:
    with open(f, 'r') as csvfile:
        csvreader = unicodecsv.reader(csvfile, delimiter='\t', encoding='utf-8')
        for row in csvreader:
            if row[0]!='NO':
                tokens = bag_of_words(extract_words_bigram(row[4],500))
                decision = classifier.prob_classify(tokens)
                
                if decision.max()=='crime':
                    POS.append(row)
            else:
                row.extend([u'TYPE'])
                HEADER='\t'.join(row)

flog.write(time.strftime("%d/%m/%Y %I:%M:%S")+': %s crime news detected\n' % (len(POS)))
'''                
#---------
# test set
#---------
POS=[]
with open('train_category_test.csv', 'r') as csvfile:
    csvreader = unicodecsv.reader(csvfile, delimiter=',', encoding='utf-8')
    for row in csvreader:
        if row[0]!='NO':
            POS.append(row)
        else:
            row.extend([u'TYPE'])
            HEADER='\t'.join(row)
'''
#---------
# training
#---------
texts = {}
texts['ACCIDENT'] = ''
texts['VIOLENT'] = ''
texts['PROPERTY'] = ''
texts['SEXUAL'] = ''
texts['OTHERS'] = ''
'''
#----------------------------
# option #1 curated sentences
#----------------------------
for f in glob.glob('./classification/curated/*.txt'):
    reader=open(f,'r')
    texts[f[len('./classification/curated/'):f.index('.txt')].upper()]=to_unicode_or_bust(''.join(reader.readlines()))
    reader.close()

#-------------------------------
# option #2 manual keywords only
#-------------------------------
for f in glob.glob('./classification/manual/*.txt'):
    reader=open(f,'r')
    texts[f[len('./classification/manual/'):f.index('.txt')].upper()]=to_unicode_or_bust(''.join(reader.readlines()))
    reader.close()
'''
#-----------------------
# option #3 full stories
#-----------------------
files=['./classification/star/pos_star_category.csv','./classification/nst/pos_nst_category.csv','./classification/sarawak/pos_sarawak_category.csv']
for f in files:
    with open(f, 'r') as csvfile:
        csvreader = unicodecsv.reader(csvfile, delimiter='\t', encoding='utf-8')
        for row in csvreader:
            if row[0]!='NO':
                if row[6]=='ACCIDENT':
                    texts[row[6]]=texts[row[6]]+'\n'+row[4]
                elif row[6]=='VIOLENT':
                    texts[row[6]]=texts[row[6]]+'\n'+row[4]
                elif row[6]=='PROPERTY':
                    texts[row[6]]=texts[row[6]]+'\n'+row[4]
                elif row[6]=='SEXUAL':
                    texts[row[6]]=texts[row[6]]+'\n'+row[4]
                elif row[6]=='OTHERS':
                    texts[row[6]]=texts[row[6]]+'\n'+row[4]

word_fd = FreqDist()
label_word_fd = ConditionalFreqDist()

for sense, text in texts.iteritems():
    features = extract_words(text)
    for word in features:
        word_fd.inc(word.lower())
        label_word_fd[sense].inc(word.lower())

accident_word_count = label_word_fd['ACCIDENT'].N()
violent_word_count = label_word_fd['VIOLENT'].N()
property_word_count = label_word_fd['PROPERTY'].N()
sexual_word_count = label_word_fd['SEXUAL'].N()
others_word_count = label_word_fd['OTHERS'].N()

total_word_count = accident_word_count + violent_word_count + property_word_count + sexual_word_count + others_word_count

word_scores = {}
 
for word, freq in word_fd.iteritems():
    accident_score = BigramAssocMeasures.chi_sq(label_word_fd['ACCIDENT'][word],(freq, accident_word_count), total_word_count)
    violent_score = BigramAssocMeasures.chi_sq(label_word_fd['VIOLENT'][word],(freq, violent_word_count), total_word_count)
    property_score = BigramAssocMeasures.chi_sq(label_word_fd['PROPERTY'][word],(freq, property_word_count), total_word_count)
    sexual_score = BigramAssocMeasures.chi_sq(label_word_fd['SEXUAL'][word],(freq, sexual_word_count), total_word_count)
    others_score = BigramAssocMeasures.chi_sq(label_word_fd['OTHERS'][word],(freq, others_word_count), total_word_count)

    word_scores[word] = accident_score + violent_score + property_score + sexual_score + others_score

best = sorted(word_scores.iteritems(), key=lambda (w,s): s, reverse=True)[:100]
bestwords = set([w for w, s in best])

train_set = []                    
for sense, text in texts.iteritems():
    features = extract_words(text)
    train_set = train_set + [(get_feature(word), sense) for word in features if word in bestwords]

    features = extract_words_bigram(text,50)
    train_set = train_set + [(get_feature(word), sense) for word in features]

classifier = NaiveBayesClassifier.train(train_set)
#print 'accuracy:', nltk.classify.util.accuracy(classifier, train_set)

#-------------------
# categorize loop #2
#-------------------
for i in range(0,len(POS)):
    tokens = bag_of_words(extract_words(POS[i][4]))
    decision = classifier.prob_classify(tokens)
    POS[i].extend([to_unicode_or_bust(str(decision.max()))])

#-------
# output
#-------
fout=codecs.open('pos_crime_category.csv','w',encoding='utf-8')
fout.write(HEADER+'\n')
for i in POS:
    fout.write('\t'.join(i)+'\n')
fout.close()

#------
# timer
#------
now=time.time()

flog.write(time.strftime("%d/%m/%Y %I:%M:%S")+': %s (HH:MM:SS) elapsed...\n' % str(datetime.timedelta(seconds=now-then)))
flog.write(time.strftime("%d/%m/%Y %I:%M:%S")+': crimeclassifier log ended\n')

flog.close()
