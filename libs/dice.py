import random

class Die(object):
	def __init__(self, sides, min=1, step=1):
		self.sides = sides
		self.min = min
		self.step = 1
		self.sides = range(min, (min+sides)*step, step)
		self._value = None
		self.combine_func = lambda a,b: a+b

	def roll(object):
		self._value = random.choice(self.sides)
		return self._value

	@property
	def value(object):
		if self._value is None: self.roll()
		return self._value

	def combine(self, other):
		if hasattr(other, 'value'): other = other.value
		return self.combine_func(self.value, other.value)

def DiceRoll(object):
	def __init__(self, dice):
		self.dice = dice
