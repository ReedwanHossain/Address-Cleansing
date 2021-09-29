import pandas as pd
import sqlite3
conn=sqlite3.connect('dbconf/outfile.db')
# df = pd.read_csv('Barikoi Area Mapping - Final Mapping.csv')
# df.to_sql('dsu_shopup_mapping', conn, if_exists='replace', index=False)

#Metro Area Mapping
df = pd.read_csv('Metro Area Mapping - Mapping.csv')
df.to_sql('Mapping', conn, if_exists='replace', index=False)