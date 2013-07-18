class ItemRegister(object):
	items = {}
	ingredients = {}
	@classmethod
	def register_item(cls,itm):
		cls.items[itm.__name__.lower()] = itm
		cls.add_ingredients(itm.ingredients)
	@classmethod
	def add_ingredients(cls,ingr):
		cls.ingredients[ingr.__name__.lower()] = ingr

class Ingredient(object):
	def __init__(self, name):
		self.name = name
		self.combos = 

class Items(object):
	def __init__(self, name, ingredients):
		self.name = name
		self.ingredients = ingredients[:]

