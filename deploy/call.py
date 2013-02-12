import sys, os
from fluidity import StateMachine, state, transition
from models import Call

from flask import Flask

import plivo
import plivohelper
from xml.dom import minidom



app = Flask(__name__)
app.config.from_object('config')
auth_id = app.config['AUTH_ID']                        # Our secret keys, please don't put up on github!
auth_token = app.config['AUTH_TOKEN'] # Our secret keys, please don't put up on github!

"""http://pypi.python.org/pypi/fluidity-sm/
State Machine representation of a Plivo call.
Inbound calls look like this:
{'Direction': 'inbound', 'From': '16176424223', 'CallerName': '+16176424223', 'BillRate': '0.00900', 'To': '12138141831', 'CallUUID': u'dc03af24-d46c-11e1-a698-efdbf167ae32', 'CallStatus': 'ringing'}

"""


song_urls=['http://50.116.10.109/~csik/plivo_sounds/old_skool.mp3',
          'http://50.116.10.109/~csik/plivo_sounds/reggae_1.mp3',
          'http://50.116.10.109/~csik/plivo_sounds/swing.mp3',
          'http://50.116.10.109/~csik/plivo_sounds/vibrant_thing.mp3',
          'http://50.116.10.109/~csik/plivo_sounds/afro_classic.mp3',]

class CallStateMachDaddy(StateMachine):
    def __init__(self,CallUUID):
		StateMachine.__init__(self)
		self.callUUID = unicode(CallUUID) 
		self.callXMLBuffer = u''
    initial_state = 'sm_ringing'
    state('sm_ringing')
    state('sm_answer', enter='_answer_call')
    state('sm_intro',)
    state('sm_help')
    state('sm_choose_song')
    state('sm_vote')
    state('sm_record_intro')
    state('sm_recording', enter ='_setup_call')
    state('sm_reviewing')
    state('sm_ending')
    
    transition(from_='sm_ringing', event='e_answer', to='sm_answer')
    transition(from_='sm_answer', event='e_introduce', to='sm_recording')
    #transition(from_=['waiting', 'created'], event='cancel', to='canceled')
    
#    def _answer_call(self):
#        print >> sys.stderr, "about to _answer_call"
#        s = "Answering call uuid = "+ str(self.call.callUUID)
#        
#        p = plivo.RestAPI(auth_id, auth_token)                  # Create a Plivo API object, used when you want to write to their service
#        params = {  'call_uuid':self.call.callUUID,
#                    'urls':song_urls[4],
#                    'length':60,
#                 }    
#        p.play(params)                                  # A method in RestAPI

    def _answer_call(self):
        print >> sys.stderr, "about to _answer_call"
        s = "Answering call uuid = "+ str(self.callUUID)
        print >> sys.stderr, s
        r = plivohelper.Response()
        r.addSpeak("Welcome.  Redirecting you to the next state.")
        r.addRedirect(url = app.config['BASEURL']+'/plivo/voice/testing_redirect/'+str(self.callUUID))
        self.callXMLBuffer = r
        s = "g xml = "+ str(r)
        print >> sys.stderr, s
 	print "leaving _answer_call"
        
    def _setup_call(self):
        print >> sys.stderr, "about to _setup_call"
        s = "setting up call " + str(self.callUUID)
        print >> sys.stderr, s
        play_music(self.callUUID,song_urls[4],60)
        r = plivohelper.Response()
        r.addSpeak("""Please rap your best rap.  You have one minute.  Press star to finish recording.""")
        r.addRecord(action=app.config['BASEURL']+'/plivo/voice/get_recording/', 
                    method='POST',
                    playBeep='true',
                    maxLength="80",
                    )
        s = "Ready to record call uuid = "+ str(self.callUUID)
        print >> sys.stderr, s
        s = "returning xml response = "+ str(r)
        print >> sys.stderr, s
        self.callXMLBuffer = r #don't forget to purge later!
        
def play_music(uuid,url,duration):
    s = "Entering play_music with url: " + str(url) + "   uuid: " + str(uuid) + "   dur: " +str(duration)
    print >> sys.stderr, s
    p = plivo.RestAPI(auth_id, auth_token)                  # Create a Plivo API object, used when you want to write to their service
    params = {  'call_uuid':uuid,
                'urls':url,
                'length':duration,
                'method':'GET',
             }    
    p.play(params)                                  # A method in RestAPI
    
