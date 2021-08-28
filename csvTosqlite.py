import pandas as pd
import sqlite3
conn=sqlite3.connect('dbconf/outfile.db')
df = pd.read_csv('Barikoi Area Mapping - Final Mapping.csv')
df.to_sql('dsu_shopup_mapping', conn, if_exists='append', index=False)