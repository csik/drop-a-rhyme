from fluidity import StateMachine, state, transition

"""http://pypi.python.org/pypi/fluidity-sm/
State Machine representation of a Plivo call.

Inbound calls look like this:
{'Direction': 'inbound', 'From': '16176424223', 'CallerName': '+16176424223', 'BillRate': '0.00900', 'To': '12138141831', 'CallUUID': u'dc03af24-d46c-11e1-a698-efdbf167ae32', 'CallStatus': 'ringing'}

"""

class CallStateMachDaddy(StateMachine):
    def __init__(self,CallUUID,Direction,From,CallerName,BillRate,To,CallStatus):
		StateMachine.__init__(self)
		self.CallUUID = CallUUID
		self.Direction = Direction
		self.From = From
		self.CallerName = CallerName
		self.BillRate = BillRate
		self.To = To
		self.CallStatus = CallStatus
    initial_state = 'ringing'
    state('ringing', exit='_answer_call')
    state('answer', enter='_setup_call')
    state('intro',)
    state('help')
    state('choose_song')
    state('vote')
    state('record_intro')
    state('recording')
    state('reviewing')
    state('ending')
    
    transition(from_='ringing', event='answer', to='answer')
    transition(from_='answer', event='introduce', to='recording')
    #transition(from_=['waiting', 'created'], event='cancel', to='canceled')
    
    def _answer_call(self):
        print "print answering call " + self.CallUUID
        #write call event to mongo
    def _setup_call(self):
        print "setting up call " + self.CallUUID
        #perhaps play some music?
        #perhaps 
        

c = CallStateMachDaddy(  Direction= 'inbound',
                         From= '16176424223',
                         CallerName= '+16176424223', 
                         BillRate= '0.00900', 
                         To= '12138141831', 
                         CallUUID= u'dc03af24-d46c-11e1-a698-efdbf167ae32', 
                         CallStatus= 'ringing')