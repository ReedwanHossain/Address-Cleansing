import reverese_geo


def fillUp(obj, KEY):
    if obj['district'] == None or obj['thana'] == None or obj['unions'] == None:
        try:
            rev_obj = reverese_geo.ReverseGeocode(
                obj['latitude'], obj['longitude'],KEY)['place']
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
