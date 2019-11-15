import sqlite3

conn = sqlite3.connect('dbconf/TestDB.db')  
c = conn.cursor()

class DBINIT(object):

	def __init__(self):
		self.AREA = None
		self.SUBAREA = None
		self.DSU = None
		self.EBL = None
		self.JBL = None
		self.BL = None
		self.BV = None
		self.DIGIT = None
		self.KEYWORD_MAP = None

	def load_area(self):
		c.execute('''
		SELECT DISTINCT *
		FROM AREA
		''')
		self.AREA = c.fetchall()

	def load_subarea(self):
		c.execute('''
		SELECT DISTINCT *
		FROM SUBAREA
		''')
		self.SUBAREA = c.fetchall()

	def load_dsu(self):
		c.execute('''
		SELECT DISTINCT *
		FROM DSU
		''')
		self.DSU = c.fetchall()

	def load_ebl(self):
		c.execute('''
		SELECT DISTINCT *
		FROM ENG_BNG_LETTER
		''')
		self.EBL = c.fetchall()

	def load_jbl(self):
		c.execute('''
		SELECT DISTINCT *
		FROM JUKTOBRONO_MAP
		''')
		self.JBL = c.fetchall()

	def load_bl(self):
		c.execute('''
		SELECT DISTINCT *
		FROM BANGLA_KEYMAP
		''')
		self.BL = c.fetchall()

	def load_bv(self):
		c.execute('''
		SELECT DISTINCT *
		FROM BANGLA_VOWEL
		''')
		self.BV = c.fetchall()

	def load_digit(self):
		c.execute('''
		SELECT DISTINCT *
		FROM DIGITS
		''')
		self.DIGITS = c.fetchall()

	def load_keyword_map(self):
		c.execute('''
		SELECT DISTINCT *
		FROM KEYWORD_MAPLIST
		''')
		self.KEYWORD_MAP = c.fetchall()


	def get_area(self):
		return [i[0] for i in self.AREA]

	def get_subarea(self):
		return [i for i in self.SUBAREA]

	def get_dsu(self):
		return [i for i in self.DSU]

	def get_ebl(self):
		return [i for i in self.EBL]

	def get_jbl(self):
		return [i for i in self.JBL]

	def get_bl(self):
		return [i for i in self.BL]

	def get_bv(self):
		return [i[0] for i in self.BV]

	def get_digit(self):
		return [i for i in self.DIGITS]

	def get_keyword_map(self):
		return [i for i in self.KEYWORD_MAP]

