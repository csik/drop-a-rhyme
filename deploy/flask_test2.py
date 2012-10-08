
"""
A more complex example of plivo working.  Here there is a combination of messaging, voice, music, and user recordings. 
"""

from flask import Flask
from flask import request, render_template, url_for

import sys
import datetime

import plivo
import plivohelper
from xml.dom import minidom

import pickle

from flaskext.mongoalchemy import MongoAlchemy

from models import Call, SMS, Trax
from call import CallStateMachDaddy

from functools import wraps
#import pymongo.objectid


app = Flask(__name__)
app.config.from_object('config')
app.config['MONGOALCHEMY_DATABASE'] = 'callz'
db = MongoAlchemy(app)

song_urls=['http://50.116.10.109/~csik/plivo_sounds/old_skool.mp3',
          'http://50.116.10.109/~csik/plivo_sounds/reggae_1.mp3',
          'http://50.116.10.109/~csik/plivo_sounds/swing.mp3',
          'http://50.116.10.109/~csik/plivo_sounds/vibrant_thing.mp3',
          'http://50.116.10.109/~csik/plivo_sounds/afro_classic.mp3',]

@app.route("/")
def hello():
    return "A very serious Hello World."
    
#wrapper to get call and daddy    
def get_objects(function):
    @wraps(function)
    def get_objects_wrapper(*args,**kwargs):
        try:
            #c = Call.query.filter(Call.callUUID == uuid).first()
            #daddy =  pickle.loads(c.callDaddyPickle)
            #function(uuid, daddy = daddy, c = c)
            print >> sys.stderr, 'args '+str(args)
            print >> sys.stderr, 'kwargs '+str(kwargs)
            uuid = str(kwargs['uuid'])
            print >> sys.stderr, uuid
            c = Call.query.filter(Call.callUUID == uuid).first()
            print >> sys.stderr, 'got c'
            kwargs['c'] = c
            daddy =  pickle.loads(c.callDaddyPickle)
            kwargs['daddy'] =  daddy
            print >> sys.stderr, 'kwargs '+str(kwargs)
            #return function(*args, **kwargs)
            return function(uuid=uuid, c=c, daddy=daddy)
        except:
            print >> sys.stderr, str(sys.exc_info()[0]) # These write the nature of the error
            print >> sys.stderr, str(sys.exc_info()[1])
    return get_objects_wrapper
        

@app.route('/dec_test/<uuid>')
@get_objects
def dec_test(uuid, c, daddy):
#def dec_test(*args,**kwargs):
    print >> sys.stderr, 'in dec_test!'
    try:
        print >> sys.stderr, 'in dec_test TRY!'
        print >> sys.stderr, str(uuid)
        print >> sys.stderr, str(c)
        print >> sys.stderr, str(daddy)
    except:
        print >> sys.stderr, str(sys.exc_info()[0]) # These write the nature of the error
        print >> sys.stderr, str(sys.exc_info()[1])
    return "Hmmmmmmm"
    
#New inbound call {'Direction': 'inbound', 'From': '16176424223', 'CallerName': '+16176424223', 'BillRate': '0.00900', 'To': '12132601816', 'CallUUID': u'6a551ecc-dd0d-11e1-b24d-efdbf167ae32', 'CallStatus': 'ringing'}
@app.route("/plivo/voice/answer/", methods=['GET', 'POST'])
def answer():
    if request.method == 'POST':
        try:
            #print >> sys.stderr, str(request.form['CallStatus'])
            
            #create call object
            c= Call(    timeAnswered = datetime.datetime.now(),
                        direction = request.form['Direction'],
                        callFrom = request.form['From'],
                        billRate = float(request.form['BillRate']),
                        cn = request.form['CallerName'],
                        callTo = request.form['To'],
                        callUUID = str(request.form['CallUUID']), 
                        #callStatus = request.form['CallStatus'],
                        callState = 'ringing',
                    ) #make a new sCall object
                        
            c.save()
            
            #create state machine
            daddy = CallStateMachDaddy(c.callUUID)
            daddy.e_answer()
            if daddy.callXMLBuffer:
                r = daddy.callXMLBuffer
                daddy.callXMLBuffer = ''
          
            c.callDaddyPickle = pickle.dumps(daddy)
            c.save()
            
            
                        #send response to Plivo cloud.
            output = "Plivo Call RESTXML Response => %s" % r
            print >> sys.stderr, output
            return render_template('response_template.xml', response=r)
        except:
            print >> sys.stderr, str(sys.exc_info()[0]) # These write the nature of the error
            print >> sys.stderr, str(sys.exc_info()[1])
    else:
        print >> sys.stderr, "Received GET request to /answer."
    return "Received GET request to /answer."

@app.route("/plivo/voice/get_recording/", methods=['GET', 'POST'])
def get_recording():
        if request.method == 'POST':
            try:
                thiscall = Call.query.filter(Call.callUUID == request.form['CallUUID']).first() 
                thiscall.recordingURL = request.form['RecordFile']
                print >> sys.stderr, "Received POST request to /get_recording/."
                s = "received url = " + thiscall.recordingURL
                print >> sys.stderr, s
                thiscall.save()
            except:
                 print >> sys.stderr, str(sys.exc_info()[0]) # These write the nature of the error
                 print >> sys.stderr, str(sys.exc_info()[1])
        else:
            print >> sys.stderr, "Received GET request to /answer."
        return "Received request to /answer."
        
@app.route("/plivo/voice/hangup/", methods=['GET', 'POST'])
def hang_up():
    if request.method == 'POST':
        print >> sys.stderr, "Received POST request to /hangup/." 
        try:
            thiscall = Call.query.filter(Call.callUUID == request.form['CallUUID']).first()
            s = "call UUID = " + thiscall.callUUID
            thiscall.callStatus = request.form['CallStatus']
            thiscall.timeEnded = datetime.datetime.now()
            thiscall.callState = "hung"
            thiscall.hangupCause = request.form['HangupCause']
            thiscall.callPlivoDuration = request.form['Duration']
            s = "Call Status = " + thiscall.callStatus +"    Hung up at: " + str(thiscall.timeEnded)
            print >> sys.stderr, s
            thiscall.save()
        except:
             print >> sys.stderr, str(sys.exc_info()[0]) # These write the nature of the error
             print >> sys.stderr, str(sys.exc_info()[1])
    else:
        print >> sys.stderr, "Received GET request to /plivo/voice/hangup."
    return "Received request to /hangup."

@app.route('/plivo/voice/testing_redirect/<uuid>', methods=['GET', 'POST'])
@get_objects
def testing_redirect(uuid, c, daddy):
    if request.method == 'POST':
        print >> sys.stderr, "Successfully Redirected  to testing_redirect"
        try:
            #c = Call.query.filter(Call.callUUID == uuid).first()
            #daddy =  pickle.loads(c.callDaddyPickle)
            s = 'type of daddy = '+str(type(daddy))
            print >> sys.stderr, s
        except:
            print >> sys.stderr, str(sys.exc_info()[0]) # These write the nature of the error
            print >> sys.stderr, str(sys.exc_info()[1])
        print >> sys.stderr, "Retreived daddy from call object"
        s = 'daddy is '+str(daddy)
        print >> sys.stderr, s
        daddy.e_introduce()
        if daddy.callXMLBuffer:
            r = daddy.callXMLBuffer
            daddy.callXMLBuffer = ''
        return render_template('response_template.xml', response=r)
        
    
@app.route('/calls')
def list_calls():
    try:
        all_calls = Call.query.descending(Call.timeAnswered).all()
    except:
        print >> sys.stderr, str(sys.exc_info()[0]) # These write the nature of the error
        print >> sys.stderr, str(sys.exc_info()[1])
    print >> sys.stderr, "loading /calls page"
    return render_template('/calls/list_calls.html', all_calls = all_calls)

@app.route('/calls/<int:page>')
def paginate_calls(page=1):
    print >> sys.stderr, "going to calls page"
    try:
        print >> sys.stderr, "about to get pagination"
        pagination = Call.query.descending(Call.timeAnswered).paginate(page=page, per_page=5)
        print >> sys.stderr, "got pagination, about to print type"
        print >> sys.stderr, str(type(pagination))
        print >> sys.stderr, "printed type, about to render"
        return render_template('/calls/paginate_calls.html', pagination = pagination, title = u"Calls")
    except:
        print >> sys.stderr, str(sys.exc_info()[0]) # These write the nature of the error
        print >> sys.stderr, str(sys.exc_info()[1])
        
        
@app.route('/calls/<string:uuid>')
def detail_calls(uuid):
    print >> sys.stderr, "Received GET request to /calls/detail/."
    try:
        call = Call.query.filter(Call.callUUID == uuid).first()
        attr_list = get_attributes(call)
        return render_template('/calls/detail_call.html', attr_list = attr_list)
    except:
        print >> sys.stderr, str(sys.exc_info()[0]) # These write the nature of the error
        print >> sys.stderr, str(sys.exc_info()[1])
        
        
@app.route('/sms')
def list_sms():
    all_sms = SMS.query.all()
    return render_template('list_sms.html', all_sms = all_sms)
    
@app.route('/sms/<uuid>')
def detail_sms(uuid):
    print >> sys.stderr, "Received GET request to /sms/detail/"
    sms = SMS.query.filter(SMS.smsMessageUUID == uuid).first()
    attr_list = get_attributes(sms)
    return render_template('detail_sms.html', attr_list = attr_list)
    
#helper function to return key/value pairs for all object attributes, only tested on mongoalchemy objects
def get_attributes(mongoobject):
    fields = list(mongoobject.get_fields())
    attr_list = []
    for field in fields:
        try:
            attr_list.append([field, mongoobject.__getattribute__(field)])
        except:
             print >> sys.stderr, str(sys.exc_info()[0]) # These write the nature of the error
             print >> sys.stderr, str(sys.exc_info()[1])
    return attr_list
    
#@app.route("/plivo/voice/digit_print/", methods=['GET', 'POST'])
#def answer():
#    if request.method == 'POST':
#        print >> sys.stderr, "this is the /digit_print routine: " + str(request.form)

@app.route("/plivo/sms/", methods=['GET', 'POST'])
def sms():
    if request.method == 'POST':
        print >> sys.stderr, "Received POST request to /plivo/sms/" # this is how you write messages to yourself in the Apache /var/log/apache2/error.log
        try:
            s = SMS(timeAnswered = datetime.datetime.now(),
                    direction = 'incoming',
                    smsTo = request.form['To'],
                    smsType = request.form['Type'],
                    smsMessageUUID = request.form['MessageUUID'],
                    smsFrom = request.form['From'],
                    smsText = request.form['Text'],
                    )
            s.save()
            send_txt(s.smsFrom,s.smsText.upper())
        except:
            print >> sys.stderr, str(sys.exc_info()[0]) # These write the nature of the error
            print >> sys.stderr, str(sys.exc_info()[1]) 
    else:
        return "These aren't the droids you're looking for.  Move along, move along."

"""Message Receive Format from Plivo: 
    ImmutableMultiDict([('To', u'12132601816'), 
                        ('Type', u'sms'), 
                        ('MessageUUID', u'e3120158-c805-11e1-86e9-002590735821'), 
                        ('From', u'75973'), 
                        ('Text', u'"Here\'s my supervisor, he\'ll help you"\n"Yo man, where\'s the supervisor at?')])}
    This is basically a dict passed to the Flask 'request' object, so to access individual data nuggets you can simply call the element:                request.form['Text'].
"""
def send_txt(destination, text, src='12132601816'):
    auth_id = 'MAYTUZMDRKMJI0ZJQ3YJ'                        # Our secret keys, please don't put up on github!
    auth_token = 'MDhhYzRlMGViYjgwMDExYTY0Y2NmYjlhMWIwZDIw' # Our secret keys, please don't put up on github!
    
    p = plivo.RestAPI(auth_id, auth_token)                  # Create a Plivo API object, used when you want to write to their service 
    params = {  'text':text,
                'src':src,
                'dst':destination,
             }    
    p.send_message(params)                                  # A method in the object for sending sms

if __name__ == "__main__":
    app.run()

