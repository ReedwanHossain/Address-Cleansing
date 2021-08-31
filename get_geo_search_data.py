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
    #url = "https://rupantor.barikoi.com/autosearch/autocomplete/polygon"
    url="http://elastic.barikoi.com/bkoi/autocomplete/polygon"
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
    querycursor.execute("SELECT "+item+" from " + tablename + " where "+tablename+"."+field+"="+repr(field_val) + ";")
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
    #print(raw_input_addr)
    data=[]
    comp={'district':None,'sub_district':None,'union':None}
    try:
        comp=get_dsu_comp(raw_input_addr)[0]
    except:
        pass
    try:
        if comp['union']!=None:
            polygon = get_db_data_union(comp['district'], comp['union'])
            # print(str(polygon.split()))
            data = polygon_search(q, str(polygon))
            print('data from union boundary')
    except:
        pass

    try:
        if comp['sub_district']!=None and len(data)==0:
            polygon = get_db_data_subdis(comp['district'], comp['sub_district'])[0][0]
            # print(str(polygon.split()))
            data = polygon_search(q, str(polygon.replace('(','').split()))
            print('data from subdistrict boundary')
    except:
        pass
    #print(comp)
    
    try:
        if comp['district']!=None and len(data)==0:
            data=get_data_by_polygon_search(q,comp['district'])
            print('data from district boundary')
    except:
        pass
    
    if len(data)==0:
        #print(q)
        url = 'http://elastic.barikoi.com/bkoi/autocomplete/search?q=' + q

        #url = 'https://admin.barikoi.xyz:8090/v2/search/autocomplete/web?q=' + q
        try:
            data= requests.get(url).json()['places']
            print('data from raw search')
        except Exception as e:
            print(e)
    
    return data


def get_db_data_union(district, union):
    data = []
    mydb=getdb('db.barikoi.com', 'barikoiadmin','Amitayef5.7', 'ethikana')
    item = 'bounds'
    tablename = 'unions'
    tablename2 = 'areas_fixed'
    # try:
    #     mydb = getdb('db.barikoi.com', 'barikoiadmin',
    #                  'Amitayef5.7', 'ethikana')
    #     print("Sucessfully connected with ethikana !")
    #     print('Fetching data from '+tablename+' Please wait..')
    # except Exception as e:
    #     print(e)
    #     print('from get_db_data_union')
    insertcursor = mydb.cursor()
    iteratorcursor = mydb.cursor(buffered=True)
    querycursor = mydb.cursor()
    querycursor.execute("SELECT unions.bounds from unions inner join subdistricts ON unions.subdistrict_id=subdistricts.id where subdistricts.adm2_en="+repr(district)+" and unions.adm4_en="+repr(union)+";")
    count = 0
    polygon = []
    gotAddress = querycursor.fetchall()
    #print(gotAddress[0][0])
    try:
        pol_str=gotAddress[0][0].replace('[[[','[')
        pol_str=pol_str.replace(']]]',']')
        data = eval(pol_str)
        #print(data)
        for i in data:
            polygon.append(str(i[1]) + ',' + str(i[0]))
    except Exception as e:
        print('from get_db_data_union')
        print(e)
        pass
    # print(polygon)
    return polygon

def get_db_data_subdis(district, subdistrict):
    data = []
    item = 'bounds'
    tablename = 'subdistricts'
    mydb=getdb('db.barikoi.com', 'barikoiadmin','Amitayef5.7', 'ethikana')
    # try:
    #     mydb = getdb('db.barikoi.com', 'barikoiadmin',
    #                  'Amitayef5.7', 'ethikana')
    #     print("Sucessfully connected with ethikana !")
    #     print('Fetching data from '+tablename+' Please wait..')
    # except Exception as e:
    #     print(e)
    #     print('from get_db_data_subdis')
    insertcursor = mydb.cursor()
    iteratorcursor = mydb.cursor(buffered=True)
    querycursor = mydb.cursor()
    querycursor.execute(
        "SELECT "+item+" from " + tablename + " where "+tablename+".adm2_en="+repr(district)+" and "+tablename+".adm3_en="+repr(subdistrict)+";")
    count = 0
    gotAddress = querycursor.fetchall()
    return gotAddress

# if __name__ == "__main__":
#     print(get_geo_data('mirpur'))
