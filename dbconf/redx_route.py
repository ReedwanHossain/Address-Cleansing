from geojson import Polygon
import json
from shapely import wkt
import pandas as pd
import sqlite3
conn = sqlite3.connect('outfile.db')
def wkt_loads(x):
    try:
        return wkt.loads(x)
    except Exception:
        return None
def insert():
    f= open('redx_route.wkt')
    d=f.readlines()
    prefix='Mirpur12'
    route_names=['A','B','C','D']
    idx=0
    for i in d:
        hub_id='3'
        hub_name='Mirpur Hub'
        area_id='315'
        area_name='Mirpur(Dhaka)'
        poly=wkt_loads(i)
        c=conn.cursor()
        c.execute(" INSERT INTO redx_route(`route_name`,`area_id`,`hub_id`,`area_name`,`hub_name`,`bounds`) VALUES ('"+prefix+route_names[idx]+"','"+area_id+"','"+hub_id+"','"+area_name+"','"+hub_name+"','"+str(poly)+"' ) ")
        idx+=1
        conn.commit()
if __name__ == "__main__":
    insert()