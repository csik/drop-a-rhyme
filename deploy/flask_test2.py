
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

from models import Call

app = Flask(__name__)

BASEURL='http://50.116.10.109'

song_urls=['http://50.116.10.109/~csik/plivo_sounds/old_skool.mp3',
          'http://50.116.10.109/~csik/plivo_sounds/reggae_1.mp3',
          'http://50.116.10.109/~csik/plivo_sounds/swing.mp3',
          'http://50.116.10.109/~csik/plivo_sounds/vibrant_thing.mp3',
          'http://50.116.10.109/~csik/plivo_sounds/afro_classic.mp3',]

@app.route("/")
def hello():
    return "A very serious Hello World."
    
    
@app.route("/plivo/voice/answer/", methods=['GET', 'POST'])
def answer():
    if request.method == 'POST':
        try:
            print >> sys.stderr, "Received POST request to /answer/."

            c= Call(    timeAnswered = datetime.datetime.now(),
                        direction = request.form['Direction'],
                        callFrom = request.form['From'],
                        billRate = request.form['BillRate'],
                        cn = request.form['CallerName'],
                        callTo = request.form['To'],
                        callUUID = request.form['CallUUID'], 
                        callStatus = request.form['CallStatus'],
                        callState = request.form['ringing'] ) #make a new sCall object
                        
            call_uuid = request.form['CallUUID']
            
            s = "call uuid = "+ str(call_uuid)
            print >> sys.stderr, s
            
            r = plivohelper.Response()
            r.addSpeak("""Please rap your best rap.  Press star to finish recording.""")
            
            #r.addPlay(song_urls[4])
            auth_id = 'MAYTUZMDRKMJI0ZJQ3YJ'                        # Our secret keys, please don't put up on github!
            auth_token = 'MDhhYzRlMGViYjgwMDExYTY0Y2NmYjlhMWIwZDIw' # Our secret keys, please don't put up on github!
            p = plivo.RestAPI(auth_id, auth_token)                  # Create a Plivo API object, used when you want to write to their service
            params = {  'call_uuid':call_uuid,
                        'urls':song_urls[3],
                        'length':60,
                     }    
            p.play(params)                                  # A method in the object for sending sms
            
            r.addRecord(action=BASEURL+url_for('get_recording'), 
                        method='POST',
                        playBeep='true',
                        maxLength="60",
                        finishOnKey="*",
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
            except:
                 print >> sys.stderr, str(sys.exc_info()[0]) # These write the nature of the error
                 print >> sys.stderr, str(sys.exc_info()[1])
        else:
            print >> sys.stderr, "Received GET request to /answer."
        return "Received request to /answer."

    
#@app.route("/plivo/voice/digit_print/", methods=['GET', 'POST'])
#def answer():
#    if request.method == 'POST':
#        print >> sys.stderr, "this is the /digit_print routine: " + str(request.form)

@app.route("/plivo/sms/", methods=['GET', 'POST'])
def sms():
    if request.method == 'POST':
        print >> sys.stderr, "Received POST request to /plivo/sms/" # this is how you write messages to yourself in the Apache /var/log/apache2/error.log
        try:
            message = request.form['Text']
            caller = request.form['From']
            send_txt(caller,message.upper())
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

