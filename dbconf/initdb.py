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
		self.AREA = [i[0] for i in self.AREA]

	def load_subarea(self):
		c.execute('''
		SELECT DISTINCT *
		FROM SUBAREA
		''')
		self.SUBAREA = c.fetchall()
		self.SUBAREA = [i for i in self.SUBAREA]

	def load_dsu(self):
		c.execute('''
		SELECT DISTINCT *
		FROM DSU
		''')
		self.DSU = c.fetchall()
		self.DSU = [i for i in self.DSU]

	def load_ebl(self):
		c.execute('''
		SELECT DISTINCT *
		FROM ENG_BNG_LETTER
		''')
		self.EBL = c.fetchall()
		self.EBL = [i for i in self.EBL]


	def load_jbl(self):
		c.execute('''
		SELECT DISTINCT *
		FROM JUKTOBRONO_MAP
		''')
		self.JBL = c.fetchall()
		self.JBL = [i for i in self.JBL]

	def load_bl(self):
		c.execute('''
		SELECT DISTINCT *
		FROM BANGLA_KEYMAP
		''')
		self.BL = c.fetchall()
		self.BL = [i for i in self.BL]

	def load_bv(self):
		c.execute('''
		SELECT DISTINCT *
		FROM BANGLA_VOWEL
		''')
		self.BV = c.fetchall()
		self.BV = [i[0] for i in self.BV]

	def load_digit(self):
		c.execute('''
		SELECT DISTINCT *
		FROM DIGITS
		''')
		self.DIGITS = c.fetchall()
		self.DIGITS = [i for i in self.DIGITS]

	def load_keyword_map(self):
		c.execute('''
		SELECT DISTINCT *
		FROM KEYWORD_MAPLIST
		''')
		self.KEYWORD_MAP = c.fetchall()
		self.KEYWORD_MAP = [i for i in self.KEYWORD_MAP]


	def get_area(self):
		return self.AREA

	def get_subarea(self):
		return self.SUBAREA

	def get_dsu(self):
		return self.DSU

	def get_ebl(self):
		return self.EBL

	def get_jbl(self):
		return self.JBL

	def get_bl(self):
		return self.BL

	def get_bv(self):
		return self.BV

	def get_digit(self):
		return self.DIGITS

	def get_keyword_map(self):
		return self.KEYWORD_MAP

