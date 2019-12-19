import sqlite3
import pandas as pd
from pandas import DataFrame

conn = sqlite3.connect('TestDB.db')  
c = conn.cursor()

# read_clients = pd.read_csv (r'../custom_banglish_transformer/keyword_maplist.csv')
# read_clients.to_sql('KEYWORD_MAPLIST', conn, if_exists='replace', index = False) 

read_clients = pd.read_csv (r'../subarea-list.csv')
read_clients.to_sql('SUBAREA', conn, if_exists='replace', index = False) 

# c.execute('''
# SELECT DISTINCT *
# FROM AREA
# ''')

# c.execute('''
# SELECT DISTINCT *
# FROM SUBAREA WHERE `subarea` = 'Gulshan'
# ''')

# c.execute('''
# SELECT DISTINCT *
# FROM ENG_BNG_LETTER
# ''')


# c.execute('''
# SELECT DISTINCT *
# FROM JUKTOBRONO_MAP 
# ''')

# c.execute('''
# SELECT DISTINCT *
# FROM BANGLA_KEYMAP 
# ''')

# c.execute('''
# SELECT DISTINCT *
# FROM BANGLA_VOWEL 
# ''')

# c.execute('''
# SELECT DISTINCT *
# FROM DIGITS 
# ''')

# c.execute('''
# SELECT DISTINCT *
# FROM KEYWORD_MAPLIST
# ''')

# c.execute('SELECT name from sqlite_master where type= "table"')   
# print(c.fetchall())
