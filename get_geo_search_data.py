import requests
import mysql.connector
import json

def getdb(host, username, password, db):
    mydb = mysql.connector.connect(
        host=host,
        user=username,
        passwd=password,
        database=db,
        raise_on_warnings=True
    )
    return mydb
def polygon_search(q, polygon):
    url = "https://rupantor.barikoi.com/autosearch/autocomplete/polygon"
    myobj = {'q': q, 'polygon': polygon}
    try:
        x = requests.post(url, data=myobj)
        return x.json()
    except Exception as e:
        print(e)
        print('from polygon_search')
        return []
def get_db_data(item, tablename, field, field_val):
    mydb=getdb('db.barikoi.com', 'barikoiadmin','Amitayef5.7', 'ethikana')
    data = []
    #tablename = 'districts'
    # try:
    #     mydb = getdb('db.barikoi.com', 'barikoiadmin',
    #                  'Amitayef5.7', 'ethikana')
    #     print("Sucessfully connected with ethikana !")
    #     print('Fetching data from '+tablename+' Please wait..')
    # except Exception as e:
    #     print(e)
    #     print('from get_db_data')
    insertcursor = mydb.cursor()
    iteratorcursor = mydb.cursor(buffered=True)
    querycursor = mydb.cursor()
    querycursor.execute(
        "SELECT "+item+" from " + tablename + " where "+tablename+"."+field+"="+repr(field_val) + ";")
    count = 0
    gotAddress = querycursor.fetchall()
    return gotAddress
def get_data_by_polygon_search(q, district):
    data = []
    try:
        polygon = get_db_data('bounds', 'districts', 'adm2_en', district)[0][0]
        polygon = polygon.replace('MULTI', '')
        polygon = polygon.replace('(', '')
        polygon = polygon.replace(')', '')
        # print(str(polygon.split()))
        data = polygon_search(q, str(polygon.split()))
        # print(data)

        return data
    except Exception as e:
        print(e)
        print('from get_db_data_by_polygon_search')
        return []
        pass
    return []
def get_dsu_comp(addr):
    url = 'http://3.1.115.160/zone/dsu'
    r = requests.post(url, data={'addr': addr})
    return r.json()

def get_geo_data(raw_input_addr,q):
    data=[]
    try:
        comp=get_dsu_comp(raw_input_addr)[0]
        print(q)
        print(comp)
        district=comp['district']
        print(district)
        if district!=None:
            data=get_data_by_polygon_search(q,district)
        #print(len(data))
        if len(data)>0:
            return data
    except Exception as e:
        print(e.with_traceback)
        pass


    url = 'https://admin.barikoi.xyz:8090/v2/search/autocomplete/web?q=' + q
    try:
        data= requests.get(url).json()['places']
    except Exception as e:
        print(e)
    print(data)
    return data


if __name__ == "__main__":
    print(get_geo_data('mirpur'))
