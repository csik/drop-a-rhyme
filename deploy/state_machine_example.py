from fluidity import StateMachine, state, transition

class SimpleMachine(StateMachine):
        def __init__(self, name):
            super( SimpleMachine, self ).__init__()
            self.name = name
        initial_state = 'created'
        state('created')
        state('waiting', enter = 'queued_now', exit = 'put_in_processing')
        state('processed', enter = 'processing', exit = 'now_processed')
        state('canceled', enter = 'canceling',)
        
        transition(from_='created', event='queue', to='waiting')
        transition(from_='waiting', event='process', to='processed')
        transition(from_=['waiting', 'created'], event='cancel', to='canceled')
        
        def creation(self):
        	print "created " + self.name
        def put_on_queue(self):
        	print "put on queue " + self.name
        def queued_now(self):
        	print "queued " + self.name
        def put_in_processing(self):
        	print "putting in processing " + self.name
        def processing(self):
        	print "now in processing " + self.name
        def now_processed(self):
        	print "done processing " + self.name
        def canceling(self):
        	print "canceling " + self.name