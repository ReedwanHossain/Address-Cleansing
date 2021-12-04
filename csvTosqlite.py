import pandas as pd
import sqlite3
conn=sqlite3.connect('dbconf/outfile.db')
# df = pd.read_csv('Barikoi Area Mapping - Final Mapping.csv')
# df.to_sql('dsu_shopup_mapping', conn, if_exists='replace', index=False)

#Metro Area Mapping
df = pd.read_csv('Uttara_Modified.csv')
df.to_sql('Uttara_Modified', conn, if_exists='replace', index=False)