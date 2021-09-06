import sqlite3
import requests
from miniparser import MiniParser
import fill_up_null_data
def getcon():
    try:
        conn = sqlite3.connect('dbconf/outfile.db')
        print("connected")
        return conn
    except Exception as e:
        print(e)
        return None
def gethub():
    conn=getcon()
    c = conn.cursor()
    c.execute("SELECT * from Unions where district='Dhaka'")
    check_result = c.fetchall()
    return check_result
def get_subarea(lat,lon):
    resp=None
    try:
        url="http://elastic.barikoi.com/bk/polygon/component?lat="+lat+"&lon="+lon+"&comp=subarea"
        data=requests.get(url).json()['places']
        if len(data)>0:
            resp=data[0]['subarea']
    except Exception as e:
        print(e)
        resp=None
        pass
    return resp
def get_subarea_by_parsing(geocoded):
    subarea=None
    try:
        obj=MiniParser()
        subarea=obj.parse(geocoded['address_short'],geocoded['pType'])['subarea']
        subarea=subarea
    except Exception as e:
        print(e)
        pass
    return subarea

def gethub_area_from_parsed(parsed):
    #print(parsed)
    parsed['city']='Dhaka'
    area_info={'redx_area':None,'redx_area_id':None}
    metro_cities=['Dhaka','Sylhet','Chittagong']
    conn=getcon()
    if parsed['city'] in metro_cities and parsed['parsed_subarea']!=None and parsed['area']!=None:
        #subarea=get_subarea(geo_address['latitude'],geo_address['longitude'])
        #subarea=get_subarea_by_parsing(geo_address)
        #print(parsed['parsed_subarea'])
        check_result=[]
        try:
            c = conn.cursor()
            c.execute("SELECT `RedX Area`, `RedX Area ID` from Mapping where `city` like '%"+parsed['city']+"%' and `area` like '%"+parsed['area']+"%' and  `subarea` like '%"+parsed['parsed_subarea']+"%' ")
            check_result = c.fetchall() 
            #print(check_result)
        except Exception as e:
            print(e)
            pass
        
        if parsed['area']!=None and len(check_result)==0:
            try:
                conn=getcon()
                c = conn.cursor()
                c.execute("SELECT `RedX Area`, `RedX Area ID` from Mapping where `city` like '%"+parsed['city']+"%' and `area` like '%"+parsed['area']+"%' ")
                check_result = c.fetchall()
            except Exception as e:
                print(e)
                pass
        #print(check_result)
        try:
            area_info['redx_area']=check_result[0][0]
            area_info['redx_area_id']=check_result[0][1]
        except Exception as e:
            print(e)
            pass
    return area_info
    
def gethub_area(geo_address):
    #print(geo_address)
    area_info={'redx_area':None,'redx_area_id':None}
    metro_cities=['Dhaka','Sylhet','Chittagong']
    conn=getcon()
    if geo_address['city'] in metro_cities:
        #subarea=get_subarea(geo_address['latitude'],geo_address['longitude'])
        subarea=get_subarea_by_parsing(geo_address)
        #print(subarea)
        check_result=[]
        try:
            c = conn.cursor()
            c.execute("SELECT `RedX Area`, `RedX Area ID` from Mapping where `city` like '%"+geo_address['city']+"%' and `area` like '%"+geo_address['area']+"%' and  `subarea` like '%"+subarea+"%' ")
            check_result = c.fetchall() 
            #print(check_result)
        except Exception as e:
            print(e)
            pass
        
        # if geo_address['thana']!=None and len(check_result)==0:
        #     try:
        #         conn=getcon()
        #         c = conn.cursor()
        #         c.execute("SELECT `RedX Area Name`, `RedX Area ID` from Unions where district='"+geo_address['district']+"' and subdistrict='"+geo_address['thana']+"' ")
        #         check_result = c.fetchall()
        #     except Exception as e:
        #         print(e)
        #         pass
        #print(check_result)
        try:
            area_info['redx_area']=check_result[0][0]
            area_info['redx_area_id']=check_result[0][1]
        except Exception as e:
            print(e)
            pass

    if area_info['redx_area']==None:
        try:
            geo_address= fill_up_null_data.fillUp(geo_address,'MTQ4MToxS1U5UlBQM043')
            #print(geo_address)
        except Exception as e:
            pass


        check_result=[]
        try:
            if geo_address['unions']!=None:
                c = conn.cursor()
                c.execute("SELECT `RedX Area Name`, `RedX Area ID` from dsu_shopup_mapping where `district` like '%"+geo_address['district']+"%' and `Barikoi unions` like '%"+geo_address['unions']+"%' ")
                check_result = c.fetchall() 
            if len(check_result)==0:
                c = conn.cursor()
                c.execute("SELECT `RedX Area Name`, `RedX Area ID` from dsu_shopup_mapping where `district` like '%"+geo_address['district']+"%' and `Barikoi subdistrict` like '%"+geo_address['thana']+"%' ")
                check_result = c.fetchall() 
            area_info['redx_area']=check_result[0][0]
            area_info['redx_area_id']=check_result[0][1]
        except Exception as e:
            print(e)
            pass
    return area_info
if __name__ == "__main__":
    geo_address={
        "Address": "Moriyom Villa, House 7, Road 32, Rupnagar, Mirpur, Dhaka",
        "area": "Mirpur",
        "city": "Dhaka",
        "district": "Dhaka",
        "latitude": "23.819038343260633",
        "longitude": "90.35503360220201",
        "pType": "Residential",
        "postCode": 1216,
        "thana": "Rupnagar",
        "uCode": "LOLM9148",
        "unions": None
    }
    #get_subarea_by_parsing(geo_address)
