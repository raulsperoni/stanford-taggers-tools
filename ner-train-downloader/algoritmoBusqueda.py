#!/bin/python
# -*- coding: utf-8 -*-

from libs import TweetRepository,utils
from pymongo import MongoClient
from twitter import *
import time
import sys
import datetime
import os

script = os.path.basename(__file__)

#DB NER
dbdb = os.getenv('MONGO_DATABASE',None)
dbhost = os.getenv('MONGO_HOST',None)
dbport = os.getenv('MONGO_PORT',None)
dbuser = os.getenv('MONGO_USER',None)
dbpass = os.getenv('MONGO_PASS',None)
dbcoll = os.getenv('MONGO_COLL',None)
tweetRepository = TweetRepository.TweetRepository(dbcoll,dbhost,dbuser,dbpass,dbport,dbdb)

#Info corridas
if dbuser:
    otherClient = MongoClient('mongodb://'+dbuser+':'+dbpass+'@'+dbhost+':'+dbport+'/'+dbdb)
else:
    otherClient = MongoClient('mongodb://'+dbhost+':'+dbport+'/'+dbdb)
krypton_db = otherClient[dbdb]
runs = krypton_db["runs"]

initial_search= os.getenv('SEARCH_CRITERIA',None)
geo_search= os.getenv('GEO_CRITERIA',None)

delay = 10

last_id = 0

while True:
    #Inicialización criterio de búsqueda
    search = initial_search
    
    prev_last_id = last_id

    #Con el criterio de búsqueda actual, se obtienen tweets nuevamente
    twitter = utils.twitterAPI()
    if initial_search:
        print 'El criterio de búsqueda actual es: ' + search
        print 'La cantidad de caracteres del criterio de búsqueda es: ' + str(len(search))
        #Siempre se filtran los retweets
        search += ' -filter:retweets'
        if not geo_search:
            query = twitter.search.tweets(q = search, count = 500, lang = "es", result_type = "mixed", since_id = last_id)
        else:
            latitude = float(geo_search.split(',')[0])
            longitude = float(geo_search.split(',')[1])
            max_range = int(geo_search.split(',')[2])
            query = twitter.search.tweets(q = search, geocode = "%f,%f,%dkm" % (latitude, longitude, max_range), count = 500, lang = "es", result_type = "mixed", since_id = last_id)
    elif geo_search:
        print 'El criterio de búsqueda actual es GEO'
        latitude = float(geo_search.split(',')[0])
        longitude = float(geo_search.split(',')[1])
        max_range = int(geo_search.split(',')[2])
        query = twitter.search.tweets(geocode = "%f,%f,%dkm" % (latitude, longitude, max_range), count = 500, lang = "es", result_type = "mixed", since_id = last_id)
    
    #Luego de obtenerlos, se guardan en la base
    insertInfo = tweetRepository.addTweets(query["statuses"],search)
    insertsCount = insertInfo['count']
    
    last_id = insertInfo['lastId']
    
    if insertsCount < 1:
        delay = delay*2
    else:
        delay = 10
        info_run = {
        'from_id':prev_last_id,
        'to_id':last_id,
        'inserts':insertsCount,
        'delay':delay,
        'now':datetime.datetime.now()
        }
        if initial_search:
            info_run['search'] = search
        if geo_search:
            info_run['geo_search'] = geo_search
        runs.insert_one(info_run)
        print 'Saved: ',info_run
    
    print script,datetime.datetime.now()," # Delay ",delay," segundos"
    time.sleep(delay)  # Delay
    

