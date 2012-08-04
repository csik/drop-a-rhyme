
"""
A more complex example of plivo working.  Here there is a combination of messaging, voice, music, and user recordings. 
"""

from flask import Flask
from flask import request, render_template, url_for

import sys
import datetime
import shelve
import plivo
import plivohelper
from xml.dom import minidom

from flaskext.mongoalchemy import MongoAlchemy
from models import Call, SMS, Trax
from call import CallStateMachDaddy


app = Flask(__name__)
app.config.from_object('config')
app.config['MONGOALCHEMY_DATABASE'] = 'calli'
db = MongoAlchemy(app)

current_calls = {}

BASEURL='http://50.116.10.109'

song_urls=['http://50.116.10.109/~csik/plivo_sounds/old_skool.mp3',
          'http://50.116.10.109/~csik/plivo_sounds/reggae_1.mp3',
          'http://50.116.10.109/~csik/plivo_sounds/swing.mp3',
          'http://50.116.10.109/~csik/plivo_sounds/vibrant_thing.mp3',
          'http://50.116.10.109/~csik/plivo_sounds/afro_classic.mp3',]

@app.route("/")
def hello():
    return "A very serious Hello World."
    
#New inbound call {'Direction': 'inbound', 'From': '16176424223', 'CallerName': '+16176424223', 'BillRate': '0.00900', 'To': '12132601816', 'CallUUID': u'6a551ecc-dd0d-11e1-b24d-efdbf167ae32', 'CallStatus': 'ringing'}
@app.route("/plivo/voice/answer/", methods=['GET', 'POST'])
def answer():
    if request.method == 'POST':
        try:
            print >> sys.stderr, "Received POST request to /answer/."
            print >> sys.stderr, str(request.form['Direction'])
            print >> sys.stderr, str(request.form['From'])
            print >> sys.stderr, str(request.form['BillRate'])
            print >> sys.stderr, str(request.form['CallerName'])
            print >> sys.stderr, str(request.form['To'])
            print >> sys.stderr, str(request.form['CallUUID'])
            #print >> sys.stderr, str(request.form['CallStatus'])
            c= Call(    timeAnswered = datetime.datetime.now(),
                        direction = request.form['Direction'],
                        callFrom = request.form['From'],
                        billRate = float(request.form['BillRate']),
                        cn = request.form['CallerName'],
                        callTo = request.form['To'],
                        callUUID = request.form['CallUUID'], 
                        #callStatus = request.form['CallStatus'],
                        callState = 'ringing',) #make a new sCall object
                        
            c.save()
            s = "Written call object = "+ str(c.callUUID)
            print >> sys.stderr, s
            daddy = CallStateMachDaddy(c.callUUID)
            print >> sys.stderr, "Made daddy"
            current_calls[c.callUUID] = daddy
            print >> sys.stderr, "put daddy into current_calls"
            
            s = "call uuid = "+ str(c.callUUID)
            print >> sys.stderr, s
            daddy.e_answer()
            print >> sys.stderr, "daddy in answer state"
            daddy.e_introduce()
            print >> sys.stderr, "daddy in recording state"
            r = plivohelper.Response()
            r.addSpeak("""Please rap your best rap.  You have one minute.  Press star to finish recording.""")
            
            #r.addPlay(song_urls[4])
            auth_id = app.config['AUTH_ID']                        # Our secret keys, please don't put up on github!
            auth_token = app.config['AUTH_TOKEN'] # Our secret keys, please don't put up on github!
            p = plivo.RestAPI(auth_id, auth_token)                  # Create a Plivo API object, used when you want to write to their service
            params = {  'call_uuid':c.callUUID,
                        'urls':song_urls[4],
                        'length':60,
                     }    
            p.play(params)                                  # A method in RestAPI
            
            r.addRecord(action=BASEURL+url_for('get_recording'), 
                        method='POST',
                        playBeep='true',
                        maxLength="80",
                        )
            r.addSpeak("""No message recorded.""")
            #r.addGetDigits(numDigits = 6,action = BASEURL+'/plivo/voice/digit_print/')
            output = "Plivo Call RESTXML Response => %s" % r
            print >> sys.stderr, output
            return render_template('response_template.xml', response=r)
        except:
            print >> sys.stderr, str(sys.exc_info()[0]) # These write the nature of the error
            print >> sys.stderr, str(sys.exc_info()[1])
    else:
        print >> sys.stderr, "Received GET request to /answer."
    return "Received GET request to /answer."
    




@app.route("/plivo/get_recording/", methods=['GET', 'POST'])
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

@app.route('/calls')
def list_calls():
    all_calls = Call.query.all()
    return render_template('list_calls.html', all_calls = all_calls)
        
@app.route('/calls/<uuid>')
def detail_calls(uuid):
    print >> sys.stderr, "Received GET request to /calls/detail/."
    call = Call.query.filter(Call.callUUID == uuid).first()
    attr_list = get_attributes(call)
    return render_template('detail_call.html', attr_list = attr_list)
    
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

