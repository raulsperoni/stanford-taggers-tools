#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket, os
from flask import Flask,jsonify,request,g
from bson import json_util
from bson.objectid import ObjectId
import json
from libs import TweetRepository
from libs.utils import simplifyText,getTokens
from flask_cors import CORS, cross_origin
from flask_httpauth import HTTPBasicAuth
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)
from functools import wraps
from pymongo import MongoClient

auth = HTTPBasicAuth()
app = Flask(__name__)
CORS(app,supports_credentials=False)

app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy dog'
dbdb = os.getenv('MONGO_DATABASE',None)
dbhost = os.getenv('MONGO_HOST',None)
dbport = os.getenv('MONGO_PORT',None)
dbuser = os.getenv('MONGO_USER',None)
dbpass = os.getenv('MONGO_PASS',None)

#Users
if dbuser:
    otherClient = MongoClient('mongodb://'+dbuser+':'+dbpass+'@'+dbhost+':'+dbport+'/'+dbdb)
else:
    otherClient = MongoClient('mongodb://'+dbhost+':'+dbport+'/'+dbdb)
krypton_db = otherClient[dbdb]
users = krypton_db["users"]

#Repository connections
dbcoll = os.getenv('MONGO_COLL',None)
tweetRepository = TweetRepository.TweetRepository(dbcoll,dbhost,dbuser,dbpass,dbport,dbdb)

def hash_password(password):
    return pwd_context.encrypt(password)

def verify_password(user, password):
    return pwd_context.verify(password, user['password'])

def generate_auth_token(user,expiration=600):	
    s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
    return s.dumps({'id': str(user['_id'])})

def verify_auth_token(token):
    s = Serializer(app.config['SECRET_KEY'])
    try:
        data = s.loads(token)
    except SignatureExpired:
        return None    # valid token, but expired
    except BadSignature:
        return None    # invalid token
    user = users.find_one({'_id':ObjectId(data['id'])})
    return user


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.headers.get('Authorization'):
            response = jsonify(message='Missing authorization header')
            response.status_code = 401
            return response
        g.user = verify_auth_token(request.headers.get('Authorization'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/ner/api/signup', methods=['POST'])
def signup():
    if not request.json.get('pin',None) or request.json['pin'] != os.getenv('SIGNUP_PIN',None):
        response = jsonify(message='Wrong signup PIN')
        response.status_code = 401
        return response
    if not request.json.get('email',None) or not request.json.get('password',None):
        response = jsonify(message='Wrong signup data')
        response.status_code = 401
        return response
    if users.find_one({'email':request.json.get('email',None)}):
       response = jsonify(message='User exists')
       response.status_code = 422
       return response
    user = {'email':request.json['email'].lower(), 'password': hash_password(request.json['password'])}
    users.insert_one(user)
    token = generate_auth_token(user)
    return jsonify({ 'token': token.decode('ascii') })

@app.route('/ner/api/tweet/unclassified', methods = ['GET'])
@login_required
def get_unclassified_tweet():
    try:
        data = tweetRepository.getRandomOne("ner_classified",False)
        #Envio info con clases candidatas
        data[u'ner_entities'] = tweetRepository.getEntities(data[u'text'])
        #Hay que serializar el obj id de mongo
        data[u'_id']=str(data[u'_id'])
        return jsonify(**data)
    except Exception, e:
        return jsonify(error=str(e))
        
@app.route('/ner/api/info', methods = ['GET'])
@login_required
def get_info():
    try:
        data = tweetRepository.getInfoNer()
        return jsonify(**data)
    except Exception, e:
        return jsonify(error=str(e))


@app.route('/ner/api/tweet/classify', methods = ['POST'])    
@login_required
def classify_tweet():
    try:
        data = request.get_json()
        print 'Clasificando',data
        if data != None:
            tweetRepository.saveEntities(data[u'ner_entities'])
            tweetRepository.updateOne(data[u'_id'],u'ner_entities',data[u'ner_entities'])
            tweetRepository.updateOne(data[u'_id'],u'ner_classified',True)
            print 'Clasificando ok'
            return jsonify(info='OK')
        else:
            return jsonify(error='Error',exeption='No llegó contenido')
    except Exception, e:
        return jsonify(error='Error',exeption=str(e))


@app.route('/ner/api/login', methods=['POST'])
def login():
    user = users.find_one({'email':request.json.get('email',None)})
    if not user or not verify_password(user,request.json['password']):
        response = jsonify(message='Wrong Email or Password',debug = hash_password(request.json['password']))
        response.status_code = 401
        return response
    token = generate_auth_token(user)
    return jsonify({ 'token': token.decode('ascii') })


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=6666,threaded=True)
    
