crimefeeder
===========
Collections of Python 2 &amp; 3 script to mine crime news and inject into mapping.fbb.utm.my/crimefeeds/v2

Acknowledgements
===============
- InvisibleMan in Python, http://pastebin.com/zYPWHnc6
- Eliot (SaltyCrane), http://www.saltycrane.com/blog/2009/11/trying-out-retry-decorator-python/
- onyfish, https://gist.github.com/322906/90dea659c04570757cccf0ce1e6d26c9d06f9283
- Tim McNamara, http://timmcnamara.co.nz/post/2650550090/extracting-names-with-6-lines-of-python-code
- Jim Plush, http://jimplush.com/blog/article/172
- Jacob Perkins, http://streamhacker.com/
- Anyone who I might have forgotten

Requirements
============
- Python 2 with NLTK, BeautifulSoup4, unicodecsv
- Python 3 with selenium, BeautifulSoup4
- Optional, an Ushahidi instance setup for displaying news

crimextractor.py
================
- Python 3
- extract news from 4 local (Malaysian) news site, saving into csv files

crimeclassifier_v2.py
=====================
- Python 2
- train the classifier (NLTK) to recognize crime vs non-crime news and if crime, which type (accident, violent, property, sexual and others)?
- save to another csv

crimeplacer.py
==============
- Python 2
- using NLTK, detect the named entity for all the categorized crime news, and extract the places
- extract the place at the beginning of each news as fallback
- save to yet another csv

crimefeeder.py
==============
- Python 3
- for each news, go to mapping.fbb.utm.my/crimefeeds/v2 and "fill in" the reports and use the places extracted in crimeplacer, try to geo-locate with built-in Google Maps, if everything ok, submit


Notes
=====
- It's messy, very messy with some unused functions, non-pythonic approach to do some stuff and non-dynamic (you will have to change the code if you wish to mine from other sites, for example)
- I includes lots of codes from other people and I am sorry if I forget to acknowledge you in the code. I will try to do so in future commits. Thanks to all of you.
