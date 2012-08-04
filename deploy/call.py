import sys, os
from fluidity import StateMachine, state, transition
from models import Call

import plivo
import plivohelper
from xml.dom import minidom


"""http://pypi.python.org/pypi/fluidity-sm/
State Machine representation of a Plivo call.

Inbound calls look like this:
{'Direction': 'inbound', 'From': '16176424223', 'CallerName': '+16176424223', 'BillRate': '0.00900', 'To': '12138141831', 'CallUUID': u'dc03af24-d46c-11e1-a698-efdbf167ae32', 'CallStatus': 'ringing'}

"""

class CallStateMachDaddy(StateMachine):
    def __init__(self,CallUUID):
		StateMachine.__init__(self)
		self.call = Call.query.filter(Call.callUUID == CallUUID).first() 
    initial_state = 'sm_ringing'
    state('sm_ringing', exit='_answer_call')
    state('sm_answer', enter='_setup_call')
    state('sm_intro',)
    state('sm_help')
    state('sm_choose_song')
    state('sm_vote')
    state('sm_record_intro')
    state('sm_recording')
    state('sm_reviewing')
    state('sm_ending')
    
    transition(from_='sm_ringing', event='e_answer', to='sm_answer')
    transition(from_='sm_answer', event='e_introduce', to='sm_recording')
    #transition(from_=['waiting', 'created'], event='cancel', to='canceled')
    
    def _answer_call(self):
        print >> sys.stderr, "about to _answer_call"
        s = "Answering call uuid = "+ str(self.call.callUUID)
        #print "print answering call " + self.call.CallUUID
        #call event has been written to mongo by answer callback
        
    def _setup_call(self):
        print >> sys.stderr, "about to _setup_call"
        s = "setting up call " + str(self.call.callUUID)
        print >> sys.stderr, s
        #perhaps play some music?
        #perhaps 
        

