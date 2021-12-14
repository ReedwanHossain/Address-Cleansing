import requests
import json
from string import capwords
import time
execute_time={}

def dsu_geo_shape_search(q,filter_query):
    url="http://elastic.barikoi.com/test/within/geoshape?q="+q+filter_query
    try:
        x = requests.get(url)
        print('from dsu_geo_shape_search')
        return x.json()['places']
    except Exception as e:
        print(e)
        return []

def filter_search_by_area_subarea(q,filter_obj):
    print('trying to search by filtering parsed area')
    #print(filter_obj)
    data=[]
    url1="http://elastic.barikoi.com/test/autocomplete/type?q="+q+"&area="+capwords(filter_obj['area'])
    if 'subarea' in filter_obj:
        url2="http://elastic.barikoi.com/test/autocomplete/type?q="+q+"&area="+capwords(filter_obj['area'])+"&subarea="+capwords(filter_obj['subarea'])
    else:
        url2=url1
    try:
        #print(url1)

        x = requests.get(url2)
        data=x.json()['places']
        if len(data)==0:
            x = requests.get(url1)
            data=x.json()['places']
        print('from area subarea filter search')
        return data
    except Exception as e:
        print(e)
        print('error from area subarea filter search')
        return []
def filter_search(q,filter_obj):
    base_url = "http://elastic.barikoi.com/test/autocomplete/type?q="+q+"&area="+filter_obj['area'][0]

    url=base_url
    if 'city' in filter_obj:
        url=base_url+"&city="+filter_obj['city'][0]
    try:
        x = requests.get(url)
        print('from filter search')
        return x.json()['places']
    except Exception as e:
        print(e)
        print('error from filter search')
        return []

    
    return []
def get_dsu_comp(addr):
    url2='http://localhost:8012/dsu'
    url = 'http://3.1.115.160/zone/dsu'
    try:
        print('trying test server')
        r = requests.post(url2, data={'addr': addr},timeout=4)
        #print(r.json())
        return r.json()
    except requests.Timeout:
        print('worked from out')
        r = requests.post(url, data={'addr': addr})
        #print(r.json())
        return r.json()

def modify_search_addr(q):
    q='REDX Logistics HQ'
    return q

def get_geo_data(raw_input_addr,q,filter_obj):

    data=[]
    print(filter_obj)
    start = time.time()
    try:
        if len(filter_obj)>=1:
            if 'parsed' in filter_obj:
                data=filter_search_by_area_subarea(q,filter_obj['parsed'])
            if 'area' in filter_obj and len(data)==0:
                data=filter_search(q,filter_obj)
    except:
        pass
    end=time.time()
    execute_time['filter_search_area_subarea']=end-start
    try:
        q=' '+q+' '
        if ' redx ' in q and ' tejgaon ' in q:
            q=modify_search_addr(q)
            raw_input_addr=raw_input_addr.lower().replace('tejgaon','tejgaon industrial area')
    except:
        pass
    #dsu find and search
    start=time.time()
    comp={'district':None,'sub_district':None,'union':None}
    try:
        comp=get_dsu_comp(raw_input_addr)[0]
    except:
        pass
    end=time.time()
    execute_time['find_dsu']=end-start

    start=time.time()
    try:
        if comp['union']!=None and len(data)==0:
            query_filter='&district='+comp['district']+'&subdistrict='+comp['sub_district']+'&union='+comp['union']
            data=dsu_geo_shape_search(q,query_filter)
            print('data from union boundary')
    except:
        pass
  

    try:
        if comp['sub_district']!=None and len(data)==0:
            query_filter='&district='+comp['district']+'&subdistrict='+comp['sub_district']
            data=dsu_geo_shape_search(q,query_filter)
            print('data from subdistrict boundary')
    except:
        pass
    #print(comp)
    
    try:
        if comp['district']!=None and len(data)==0:
            query_filter='&district='+comp['district']
            data=dsu_geo_shape_search(q,query_filter)
            print('data from district boundary')
    except:
        pass
    end=time.time()
    execute_time['filter_search_dsu']=end-start

    start=time.time()
    if len(data)==0:
        #print(q)
        url = 'http://elastic.barikoi.com/bkoi/autocomplete/search?q=' + q

        #url = 'https://admin.barikoi.xyz:8090/v2/search/autocomplete/web?q=' + q
        try:
            data= requests.get(url).json()['places']
            print('data from raw search')
        except Exception as e:
            print(e)
    #print(data)
    end=time.time()
    execute_time['raw_search']=end-start
    print(execute_time)
    return data


def get_db_data_union(district, union):
    start=time.time()
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
    end=time.time()
    execute_time['union_polygon_from_db']=end-start
    return polygon

def get_db_data_subdis(district, subdistrict):
    start=time.time()
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
    end=time.time()
    execute_time['subdistrict_polygon_from_db']=end-start
    return gotAddress

# if __name__ == "__main__":
#     print(get_geo_data('mirpur'))
