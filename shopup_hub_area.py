import sqlite3
import requests
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

def gethub_area(geo_address):
    subarea=get_subarea(geo_address['latitude'],geo_address['longitude'])
    area_info={'RedX Area':None,'RedX Area ID':None}
    check_result=[]
    try:
        conn=getcon()
        c = conn.cursor()
        c.execute("SELECT `RedX Area`, `RedX Area ID` from Mapping where `city`='"+geo_address['city']+"' and `area`='"+geo_address['area']+"' and  `subarea`='"+subarea+"' ")
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
        area_info['RedX Area']=check_result[0][0]
        area_info['RedX Area ID']=check_result[0][1]
    except Exception as e:
        print(e)
        pass

    #print(area_info)
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
    gethub_area(geo_address)