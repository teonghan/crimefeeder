crimefeeder
===========
Collections of Python 2 &amp; 3 script to mine crime news and inject into mapping.fbb.utm.my/crimefeeds/v2

Requirements
============
- Python 2 with NLTK, BeautifulSoup4, unicodecsv
- Python 3 with selenium, BeautifulSoup4
- Optional, an Ushahidi instance setup for displaying news

crimextractor.py
================
- Python 3
- extract news from 4 local (Malaysian) news site, saving into csv files

crimeclassifier.py
==================
- Python 2
- train the classifier (NLTK) to recognize crime vs non-crime news and if crime, which type (accident, violent, property, sexual and others)?
