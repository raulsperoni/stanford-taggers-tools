#!/usr/bin/python
# -*- coding: utf-8 -*-
import pymongo
from pymongo import MongoClient
import json
import os
from twitter import *
import re
import unicodedata

def twitterAPI():
    #-----------------------------------------------------------------------
    # load our API credentials 
    #-----------------------------------------------------------------------
    config = {}
    here = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(here, 'config.py')
    exec(open(filename).read(), config)

    #-----------------------------------------------------------------------
    # create twitter API object
    #-----------------------------------------------------------------------
    return Twitter(auth = OAuth(config["access_key"], config["access_secret"], config["consumer_key"], config["consumer_secret"]))



#Dado un conjunto de datos, luego de utilizar el tokenizador de nltk
#devuelve una lista de las n palabras mas frecuentes del conjunto ordenadas por
#frecuencia
def mostFrequentWords (n,data,searchList = None):
    here = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(here, 'stopwords.txt')
    #Elimino de los datos las stopwords
    stopwords = open(filename).read().splitlines()
    data = filterWords(data,stopwords, True)
    
    if searchList != None:
        data = filterWords(data,searchList,True)
    
    words = {}
    for tweet in data:
        for word in tweet.split():
            word = simplifyText(word)
            word = re.sub('[\-\.\,\$\%\^\&\*\s\:]+', '', word)
            if word and word not in searchList:
                if word.lower() in words: 
                    words[word.lower()] = words[word.lower()] + 1
                else:
                    words[word.lower()] = 1

    mostFrequent = [w for w in sorted(words, key=words.get, reverse=True) if words[w] > 10]
    return mostFrequent[:n]


#Dado un conjunto de datos, una lista de palabras, y un booleano
#filtra el conjunto de los datos segun las palabras de la lista.
#Si not_in = False: Se queda con las palabras de los datos que pertenecen a la lista
#Si not_in = True: Se queda con las palabras de los datos que NO pertencen a la lista
def filterWords(data,filter,not_in):
    #print filter
    filtered_data = []
    for d in data:
        if(not_in):
            filt = [w.lower() for w in d.split() if not simplifyText(w.lower()) in filter]
        else:
            filt = [w.lower() for w in d.split() if simplifyText(w.lower()) in filter]
        
        if len(filt) != 0:
            filtered_data.append(" ".join(filt))
    
    return filtered_data


def simplifyText(text):
    """
    Saca tildes, Saca espacios extras
    """
    from unidecode import unidecode
    import re
    text = re.sub(' +',' ',text)
    return unidecode(text)
    

def getTokens(text):
    """
    Saca tildes, Saca espacios extras
    """
    from unidecode import unidecode
    import re
    import string
    #Saco urls, dejo espacio
    text = re.sub('http(.)*',' ',text)
    #Saco todo lo que no sea palabra, dejo espacio
    text = re.sub('[^#@a-zA-Z0-9_]',' ',text)
    #Saco espacios de mas
    text = re.sub(' +',' ',text)
    text = unidecode(text)
    return text.split(' ')
    
    

