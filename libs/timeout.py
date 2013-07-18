class Event(object):
	def fire(self,*args,**kw): pass

class Countdown(object):
	def __init__(self): pass
	def schedule(self,ticks,event,*args,**kw): pass
	def tick(self): pass


if __name__ == '__main__':
	import unittest

	class TestCountdown(unittest.TestCase):
		def a_test_schedule(self):
			a = Countdown()
			class event_test(Event):
				def __init__(self):
					self.fired = False
				def fire(self):
					self.fired = not self.fired
					return False
			a.schedule(3,event_test())
