import requests


def ReverseGeocode(lat, lon, KEY):
    url = "https://barikoi.xyz/v1/api/search/reverse/geocode/server/"+KEY+"/place?longitude="+lon+"&latitude="+lat +"&district=true&sub_district=true&union=true"
    obj = requests.get(url)
    return obj.json()

def fillUp(obj, KEY):
    if obj['district'] == None or obj['thana'] == None or obj['unions'] == None:
        try:
            rev_obj = ReverseGeocode(obj['latitude'], obj['longitude'],KEY)['place']
            if obj['district'] == None:
                obj['district'] = rev_obj['district']
            if obj['thana'] == None:
                obj['thana'] = rev_obj['sub_district']
            if obj['unions'] == None:
                obj['unions'] = rev_obj['union']
        except Exception as e:
            print('In fillUp function')
            print(e)
            pass
    return obj
