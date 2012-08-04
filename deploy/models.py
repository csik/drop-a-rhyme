#!/usr/bin/env python
"""
models.py

Created by Christopher Csikszentmihalyi on 2012-07-26.
Copyright (c) 2012 __MyCompanyName__. All rights reserved.
Licensed under the Affero 3 GPL License
http://www.gnu.org/licenses/agpl.txt
"""

import sys
import os
import datetime

from flask import Flask
from flaskext.mongoalchemy import MongoAlchemy

app = Flask(__name__)
app.config['MONGOALCHEMY_DATABASE'] = 'calli'
db = MongoAlchemy(app)

#{'Direction': 'inbound', 'From': '16176424223', 'CallerName': '+16176424223', 'BillRate': '0.00900', 'To': '12138141831', 'CallUUID': u'dc03af24-d46c-11e1-a698-efdbf167ae32', 'CallStatus': 'ringing'}

import datetime

#!!!!!!!!!!!!!!!!!!!
#!!!!!!!!!!!!!!!!!!! 
class Call(db.Document):
    timeAnswered = db.DateTimeField()
    direction = db.StringField() #inbound, outbound
    callFrom = db.StringField() #from number
    cn = db.StringField() #from number
    billRate = db.FloatField() 
    callTo = db.StringField() 
    callUUID = db.StringField() #unique id assigned by Plivo (we aren't checking this!)
    callStatus = db.StringField(required=False) #the plivo status
    callState = db.StringField() #our state machine state
    #everything above this mark should be part of the __init__()
    #everything below can be updated later
    timeEnded = db.DateTimeField(required=False) #allows for call length
    recordingURL = db.StringField(required=False) #passed with successful record
    hangupCause = db.StringField(required=False)
    callNumberOfListens = db.IntField(required=False)
    callLength = db.IntField(required=False) #seconds
    callUpVotes = db.IntField(required=False)
    callDownVotes = db.IntField(required=False)
    callListens = db.IntField(required=False)
    callListenLengths = db.ListField(db.IntField(),required=False)
    callPlivoDuration = db.StringField(required=False)

class SMS(db.Document):
    timeAnswered = db.DateTimeField()
    direction = db.StringField()
    smsTo = db.StringField() 
    smsType = db.StringField() 
    smsMessageUUID = db.StringField()
    smsFrom = db.StringField()
    smsText = db.StringField()
    
class Trax(db.Document):
    traxAdded = db.DateTimeField()
    traxURL = db.StringField()


#c= Call(    timeAnswered = datetime.datetime.now(),
#            direction='left', 
#            callFrom = 'me', 
#            billRate = 3.333, 
#            cn = 'theFonz',
#            callTo = 'you', 
#            callUUID = 'opiasdflkjsafhskjfh', 
#            callStatus = 'ringing',
#            callState = "ringing" ) #make a new sCall object
#            
#d= Call(    timeAnswered = datetime.datetime.now(),
#            direction='right', 
#            callFrom = 'yo mama', 
#            billRate = 3.333, 
#            cn = 'yo mama number',
#            callTo = 'me', 
#            callUUID = 'xxxxxxxxxxxxxxxxxxx', 
#            callStatus = 'ringing',
#            callState = "ringing" ) #make a new sCall object
#            
#e = Call(   timeAnswered = datetime.datetime.now(),
#            direction='center', 
#            callFrom = 'the fonz', 
#            billRate = 400.23, 
#            cn = 'theFonz',
#            callTo = 'you', 
#            callUUID = 'yyy23487298347298743', 
#            callStatus = 'hungup',
#            callState = "hanging up" ) #make a new sCall object
    
#c.save()
#thiscall = Call.query.filter(Call.callUUID == 'opiasdflkjsafhskjfh').first()
#print thiscall.callUUID

#fonz = Call.query.filter(Call.cn == 'theFonz')
#print str(fonz.all())
#d.save()
#e.save()
#print str(fonz.all())

#for i in fonz.all():
#    print i.timeAnswered

        





    
