from flask_cors import CORS
#import json
from flask import Flask, request, jsonify, send_file, send_from_directory, make_response
from flask_restful import reqparse, abort, Api, Resource
import pandas as pd
import urllib
import re
import os
from werkzeug.utils import secure_filename
# import io
import codecs
import csv
from bkoi_parser import Address
from bkoi_normalizer import AddressParser
from custom_banglish_transformer.bkoi_transformer import Transformer
from bkoi_e2b import ReverseTransformer
from dbconf.db_operations import Operations
import similarity
import shopup_hub_area
import shutil
import geo_distance
from string import capwords
app = Flask(__name__)
#CORS(app, resources={r"/*": {"origins": ["https://rupantor.barikoi.com", "http://localhost", "https://admin.barikoi.xyz"]}})
CORS(app)
BASE_PATH = os.getcwd()
#print(BASE_PATH)
if not os.path.exists(BASE_PATH+'/UPLOADED_FILE'):
    os.makedirs(BASE_PATH+'/UPLOADED_FILE')
UPLOAD_FOLDER = BASE_PATH + '/UPLOADED_FILE'
# shutil.rmtree(UPLOAD_FOLDER)
ALLOWED_EXTENSIONS = set(['txt', 'json', 'csv'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
add_parse = Address()


@app.route('/file/upload', methods=['GET', 'POST'])
def upload_file():
    try:
        shutil.rmtree(UPLOAD_FOLDER)
        os.makedirs(UPLOAD_FOLDER)
    except:
        pass
    # check if the post request has the file part
    if 'file' not in request.files:
        resp = jsonify({'message': 'No file part in the request'})
        resp.status_code = 400
        return resp
    file = request.files['file']
    if file.filename == '':
        resp = jsonify({'message': 'No file selected for uploading'})
        resp.status_code = 400
        return resp
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        print(type(filename))
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        if filename.rsplit('.', 1)[1].lower() == 'csv':
            file_status = "None"
            try:
                file_status = run_csv(filename)
                if file_status == "None":
                    resp = jsonify(
                        {'message': 'Something Went wrong!'})
                    resp.status_code = 403
                    return resp
                # return 'ok'
                # resp = jsonify({'message': 'File successfully uploaded'})
                #resp.status_code = 200
                return send_from_directory(directory=UPLOAD_FOLDER, filename=filename.rsplit('.')[1]+'_converted.csv', as_attachment=True)
            except Exception as e:
                print(e)
                resp = jsonify(
                    {'message': 'Make sure input_address column exist in file !'})
                resp.status_code = 203
                return resp
    else:
        resp = jsonify({'message': 'Allowed file types are txt, json, csv'})
        resp.status_code = 400
        return resp


def run_csv(filename):
    filter_obj={}
    thana_param = "yes"
    district_param = "yes"
    add_trans = Transformer()
    add_parse = Address()
    df = pd.read_csv(UPLOAD_FOLDER + "/" + filename)
    if "input_address" not in df:
        return "None"

    with open(UPLOAD_FOLDER+'/'+filename.rsplit('.')[1]+'_converted.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["input_address", "fixed_address", "geocoded_address",
                         "latitude", "longitude", "confidence_score_percentage", "status"])
        for i in df['input_address']:
            print(i)
            res = add_parse.parse_address(add_trans.bangla_to_english(i), thana_param, district_param,filter_obj)
            try:
                writer.writerow([i, res['address'], res['geocoded']
                                 ['Address'], res['geocoded']['latitude'], res['geocoded']['longitude'], res['confidence_score_percentage'], res['status']])
            except Exception as e:
                print(e)
                writer.writerow([i, res])
        file.close()
    return "Done"


@app.route('/uploader', methods=['POST'])
def uploading_file():
    if request.method == 'POST':
        result_array = []
        # f = request.files['file']
        # stream = io.StringIO(f.stream.read().decode("UTF8"), newline=None)
        # csv_input = csv.reader(stream)
        # print(csv_input)
        # fstring = csv.DictReader(request.files['file'])

        flask_file = request.files['file']
        if not flask_file:
            return 'Upload a CSV file'

        stream = codecs.iterdecode(flask_file.stream, 'utf-8')
        for td in csv.DictReader(stream, dialect=csv.excel):
            input_address = td['address']
            print(input_address)
            result = add_parse.parse_address(input_address)
            try:
                result_array.append(
                    {'input-address': input_address, 'clean-address': result['address'], 'status':  result['status'], 'geocoded-address':  result['geocoded']['Address']})
            except Exception as e:
                result_array.append(
                    {'input-address': input_address, 'clean-address': result['address'], 'status':  result['status'], 'geocoded-address':  'Failed to GeoCode'})

        csv_columns = ['input-address', 'clean-address',
                       'status', 'geocoded-address']
        csv_file = "parsed.csv"

        try:
            with open(csv_file, 'w') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
                writer.writeheader()
                for data in result_array:
                    writer.writerow(data)
        except IOError:
            print("I/O error")

    try:
        return send_from_directory('.', 'parsed.csv', attachment_filename='parsed.csv', as_attachment=True)
    except FileNotFoundError:
        abort(404)


@app.route('/address/matcher', methods=['POST'])
def matcher():
    add_trans = None
    add_trans = Transformer()
    addr1 = request.form.get('addr1')
    addr2 = request.form.get('addr2')
    inAdd1 = addr1
    inAdd2 = addr2
    addr1 = add_trans.bangla_to_english(addr1)
    addr2 = add_trans.bangla_to_english(addr2)
    addr1 = similarity.bkoi_addess_cleaner(addr1)
    addr2 = similarity.bkoi_addess_cleaner(addr2)
    # print(addr1+"   "+addr2)
    # print (similarity.bkoi_address_matcher(addr1,addr2,inadd1,inadd2))

    return similarity.bkoi_address_matcher(addr1, addr2, inAdd1, inAdd2)



@app.route('/transform', methods=['GET'])
def transform_addr():
    add_trans = None
    add_trans = Transformer()
    addr = request.args.get('addr')
    # de_addr = urllib.unquote(addr)
    # print "address.........."+de_addr
    return add_trans.bangla_to_english(addr)

# English to Bangla Transformer
@app.route('/btransformer', methods=['POST'])
def btransform_addr():
    add_trans = None
    add_trans = ReverseTransformer()
    addr = request.form.get('addr')
    # de_addr = urllib.unquote(addr)
    # print "address.........."+de_addr
    return add_trans.english_to_bangla(addr)


@app.route('/transformer', methods=['POST'])
def transformer_addr():
    add_trans = None
    add_trans = Transformer()
    addr = request.form.get('addr')
    # de_addr = urllib.unquote(addr)
    # print "address.........."+de_addr
    return add_trans.bangla_to_english(addr)




@app.route('/test', methods=['POST'])
def test():
    add_trans = None
    add_parse = None
    add_trans = Transformer()
    add_parse = Address()
    addr = request.form.get('addr')
    return add_parse.check_room(add_trans.bangla_to_english(addr))




@app.route('/geocoder', methods=['POST'])
def geocoder():
    filter_obj={}
    return_obj={'Address':None,'area':None,'latitude':None,'longitude':None}
    add_trans = None
    add_parse = None
    thana_param = None
    district_param = None
    add_trans = Transformer()
    add_parse = Address()
    addr = request.form.get('addr')
    raw_input=addr
    if re.search('[\u0995-\u09B9\u09CE\u09DC-\u09DF]|[\u0985-\u0994]|[\u09BE-\u09CC\u09D7]|(\u09BC)|()[০-৯]',addr):
        try:
            add_trans = Transformer()
            addr=add_trans.bangla_to_english(addr)
        except Exception as e:
            pass

    try:
        obj = add_parse.parse_address(addr, thana_param, district_param,filter_obj)
    except Exception as e:
        import get_geo_search_data
        obj['geocoded']=get_geo_search_data.get_geo_data(addr,addr)[0]
        obj['address']=addr
        obj['confidence_score_percentage']=0
        obj['address_bn']=""
        obj['input_address']=raw_input
        obj['parsed_address']={}
        obj['status']='incomplete'

    try:
        print(obj['geocoded']['Address'])
        #print(type(return_obj['Address']))
        return_obj['Address']=obj['geocoded']['Address']
        return_obj['area']=obj['geocoded']['area']
        return_obj['latitude']=obj['geocoded']['latitude']
        return_obj['longitude']=obj['geocoded']['longitude']
        obj['geocoded']=return_obj
        obj['input_address']=raw_input
        obj['fixed_address']=obj['address']
        del obj['address']
        del obj['parsed_address']
        del obj['matched_keys']
    except Exception as e:
        print(e)
        pass
    #print(return_obj)
    return jsonify(obj)

@app.route('/parse', methods=['POST'])
def parse():
    #print (request.environ['HTTP_ORIGIN'])
    filter_obj={}
    obj=[]
    add_trans = None
    add_parse = None
    thana_param = None
    district_param = None
    add_trans = Transformer()
    add_parse = Address()
    addr = request.form.get('addr')
    area = request.form.get('area')
    city = request.form.get('city')
    if area!=None and area!="":
        filter_obj['area']=[capwords(area)]
    if city!=None and city!="":
        filter_obj['city']=[capwords(city)]
    print(filter_obj)
    print(addr)
    try:
        thana_param = request.form.get('thana')
    except Exception as e:
        thana_param = None

    try:
        district_param = request.form.get('district')
    except Exception as e:
        district_param = None
    
    addr_en=addr
    if re.search('[\u0995-\u09B9\u09CE\u09DC-\u09DF]|[\u0985-\u0994]|[\u09BE-\u09CC\u09D7]|(\u09BC)|()[০-৯]',addr):
        try:
            add_trans = Transformer()
            addr_en=add_trans.bangla_to_english(addr)
        except Exception as e:
            pass
    try:
        obj = add_parse.parse_address(addr_en, thana_param, district_param,filter_obj)
    except Exception as e:
        pass


    return jsonify(obj)


@app.route('/transparse', methods=['POST'])
def transform_parse():
    #print (request.environ['HTTP_ORIGIN'])
    filter_obj={}
    obj={}
    add_trans = None
    add_parse = None
    thana_param = None
    district_param = None
    add_trans = Transformer()
    add_parse = Address()
    addr = request.form.get('addr')
    area = request.form.get('area')
    city = request.form.get('city')
    if area!=None and area!="":
        filter_obj['area']=[capwords(area)]
    if city!=None and city!="":
        filter_obj['city']=[capwords(city)]
    print(filter_obj)
    print(addr)
    try:
        thana_param = request.form.get('thana')
    except Exception as e:
        thana_param = None

    try:
        district_param = request.form.get('district')
    except Exception as e:
        district_param = None
    
    addr_en=addr
    if re.search('[\u0995-\u09B9\u09CE\u09DC-\u09DF]|[\u0985-\u0994]|[\u09BE-\u09CC\u09D7]|(\u09BC)|()[০-৯]',addr):
        try:
            add_trans = Transformer()
            addr_en=add_trans.bangla_to_english(addr)
        except Exception as e:
            pass
    try:
        obj = add_parse.parse_address(addr_en, thana_param, district_param,filter_obj)
        obj['input_address']=addr
    except Exception as e:
        import get_geo_search_data
        obj['geocoded']=get_geo_search_data.get_geo_data(addr,addr,filter_obj)[0]
        obj['address']=addr
        obj['confidence_score_percentage']=0
        obj['address_bn']=""
        obj['input_address']=addr
        obj['parsed_address']={}
        obj['status']='incomplete'

    try:
        del obj['matched_keys']
    except Exception as e:
        print(e)
        pass

    return jsonify(obj)




@app.route('/shopup/route', methods=['POST'])
def shopup_route():
    route_info={'hub_name':None,'area_name':None,'route_name':None}
    shopup_obj={'route_info':route_info,'geocoded':None,'strength':0}
    return_obj={'Address':None,'area':None,'latitude':None,'longitude':None}
    filter_obj={}
    add_trans = None
    add_parse = None
    thana_param = None
    district_param = None
    add_parse = Address()
    addr = request.form.get('addr')
    hub_id = request.form.get('hub_id')
    area = request.form.get('redx_area')
    if area!=None and area!="":
        barikoi_areas=shopup_hub_area.get_barikoi_comp_from_shopup(area.strip())
        print(barikoi_areas)
        if len(barikoi_areas)>0:
            filter_obj['city']=barikoi_areas[0][0]
            filter_obj['area']=barikoi_areas[0][1]
    print(filter_obj)
    try:
        thana_param = request.form.get('thana')
    except Exception as e:
        thana_param = None

    try:
        district_param = request.form.get('district')
    except Exception as e:
        district_param = None
    addr_en=addr
    if re.search('[\u0995-\u09B9\u09CE\u09DC-\u09DF]|[\u0985-\u0994]|[\u09BE-\u09CC\u09D7]|(\u09BC)|()[০-৯]',addr):
        try:
            add_trans = Transformer()
            addr_en=add_trans.bangla_to_english(addr)
        except Exception as e:
            pass
    obj = add_parse.parse_address(addr_en, thana_param, district_param,filter_obj)
    try:
        del obj['matched_keys']
    except Exception as e:
        print(e)
        pass
    try:
        #print(obj['geocoded']['latitude'])
        resp=shopup_hub_area.get_route_info(hub_id,obj['geocoded']['latitude'],obj['geocoded']['longitude'])
        print(resp)
        route_info['route_name']=resp[0][0]
        route_info['hub_name']=resp[0][2]
        route_info['area_name']=resp[0][1]
    except Exception as e:
        print(e)
        pass
    # #print(obj)
    try:
        #print(obj['address'])
        if (obj['parsed_address']['area']==obj['geocoded']['area'].lower() or ' '+obj['geocoded']['area'].lower()+' ' in ' '+addr_en.lower()+' ' or obj['confidence_score_percentage']>=60) and ['route_info']['route_name']!=None:
            shopup_obj['strength']=1
    except Exception as e:
        print(e)
        pass
    
    try:
        return_obj['Address']=obj['geocoded']['Address']
        return_obj['area']=obj['geocoded']['area']
        return_obj['latitude']=obj['geocoded']['latitude']
        return_obj['longitude']=obj['geocoded']['longitude']
        #shopup_obj['confidence_score_percentage']=obj['confidence_score_percentage']
        shopup_obj['input_address']=addr
        shopup_obj['geocoded']=return_obj
    except Exception as e:
        print(e)
        pass
    return jsonify(route_info)





@app.route('/shopup/verify', methods=['POST'])
def shopup_parse():
    filter_obj={}
    shopup_obj={'geocoded':{'Address':None,'area':None,'latitude':None,'longitude':None},'strength':0,'input_address':None}
    add_trans = None
    add_parse = None
    thana_param = None
    district_param = None
    add_parse = Address()
    addr = request.form.get('addr')
    #print(addr)
    try:
        thana_param = request.form.get('thana')
    except Exception as e:
        thana_param = None

    try:
        district_param = request.form.get('district')
    except Exception as e:
        district_param = None
    addr_en=addr
    if re.search('[\u0995-\u09B9\u09CE\u09DC-\u09DF]|[\u0985-\u0994]|[\u09BE-\u09CC\u09D7]|(\u09BC)|()[০-৯]',addr):
        try:
            add_trans = Transformer()
            addr_en=add_trans.bangla_to_english(addr)
        except Exception as e:
            pass
    obj = add_parse.parse_address(addr_en, thana_param, district_param,filter_obj)
    try:
        del obj['matched_keys']
    except Exception as e:
        print(e)
        pass
    try:
        shopup_obj['redx_info']=shopup_hub_area.gethub_area(obj['geocoded'])
    except Exception as e:
        print(e)
        pass
    print(obj)
    try:
        #print(obj['address'])
        if (obj['parsed_address']['area']==obj['geocoded']['area'].lower() or ' '+obj['geocoded']['area'].lower()+' ' in ' '+addr_en.lower()+' ' or obj['confidence_score_percentage']>=60) and shopup_obj['redx_info']['redx_area']!=None:
            shopup_obj['strength']=1
    except Exception as e:
        print(e)
        pass
    
    try:
        shopup_obj['geocoded']['Address']=obj['geocoded']['Address']
        shopup_obj['geocoded']['area']=obj['geocoded']['area']
        shopup_obj['geocoded']['latitude']=obj['geocoded']['latitude']
        shopup_obj['geocoded']['longitude']=obj['geocoded']['longitude']
        #shopup_obj['confidence_score_percentage']=obj['confidence_score_percentage']
        shopup_obj['input_address']=addr
    except Exception as e:
        print(e)
        pass
    return jsonify(shopup_obj)


@app.route('/shopup/geofence', methods=['POST'])
def shopup_geofence():
    filter_obj={}
    shopup_obj={'geocoded':{'Address':None,'area':None,'latitude':None,'longitude':None},'confidence_score_percentage':0,'input_address':None,'distance_m':None}
    add_trans = None
    add_parse = None
    thana_param = None
    district_param = None
    add_parse = Address()
    addr = request.form.get('addr')
    latitude=request.form.get('lat')
    longitude=request.form.get('lon')
    lat_lon_p='^-?(([-+]?)([\d]{1,3})((\.)(\d+))?)'
    if latitude==None or longitude==None or addr==None:
        return {"message": "Try with correct lat lon format"},422 
    if not re.match(lat_lon_p,latitude) or not re.match(lat_lon_p,longitude):
        return {"message": "Try with correct lat lon format"},422 

    addr_en=addr
    if re.search('[\u0995-\u09B9\u09CE\u09DC-\u09DF]|[\u0985-\u0994]|[\u09BE-\u09CC\u09D7]|(\u09BC)|()[০-৯]',addr):
        try:
            add_trans = Transformer()
            addr_en=add_trans.bangla_to_english(addr)
        except Exception as e:
            pass
    try:
        obj = add_parse.parse_address(addr_en, thana_param, district_param,filter_obj)
    except Exception as e:
        print(e)
        pass
    try:
        del obj['matched_keys']
    except Exception as e:
        print(e)
        pass
    try:
        shopup_obj['distance_m']=geo_distance.Distance(float(latitude),float(longitude),float(obj['geocoded']['latitude']),float(obj['geocoded']['longitude']))*1000
    except Exception as e:
        print(e)
        pass

    
    try:
        shopup_obj['geocoded']['Address']=obj['geocoded']['Address']
        shopup_obj['geocoded']['area']=obj['geocoded']['area']
        shopup_obj['geocoded']['latitude']=obj['geocoded']['latitude']
        shopup_obj['geocoded']['longitude']=obj['geocoded']['longitude']
        shopup_obj['confidence_score_percentage']=obj['confidence_score_percentage']
        shopup_obj['input_address']=addr
    except Exception as e:
        print(e)
        pass
    return jsonify(shopup_obj)

@app.route('/matchparse', methods=['POST'])
def match_parse():
    filter_obj={}
    add_trans = None
    add_parse = None
    thana_param = None
    district_param = None
    add_trans = Transformer()
    add_parse = Address()
    addr = request.form.get('addr')
    print(addr)
    try:
        thana_param = request.form.get('thana')
    except Exception as e:
        thana_param = None

    try:
        district_param = request.form.get('district')
    except Exception as e:
        district_param = None

    obj = add_parse.parse_address(add_trans.bangla_to_english(addr), thana_param, district_param,filter_obj)
    # if obj['confidence_score_percentage'] >= 75 and (obj['status'] == 'incomplete' or (obj['matched_keys']['housekey'] != 1 and obj['parsed_address']['pattern'][0] == 'H') or (obj['matched_keys']['roadkey'] != 1 and obj['parsed_address']['pattern'][1] == 'H') or (obj['matched_keys']['blockkey'] != 1 and obj['parsed_address']['pattern'][2] == 'H') or (obj['matched_keys']['subareakey'] != 1 and obj['parsed_address']['pattern'][4] == 'H')):
    if obj['confidence_score_percentage'] >= 75 and ((obj['matched_keys']['roadkey'] != 1 and obj['parsed_address']['pattern'][1] == 'H') or (obj['matched_keys']['blockkey'] != 1 and obj['parsed_address']['pattern'][2] == 'H') or (obj['matched_keys']['subareakey'] != 1 and obj['parsed_address']['pattern'][4] == 'H')):
        obj['FP'] = "yes"
    else:
        obj['FP'] = "no"
    return obj


# insert new keyword
@app.route('/keyword', methods=['POST'])
def keyword_insert():
    con = Operations()
    bn = None
    en = None
    bn = request.form.get('bn')
    en = request.form.get('en')
    user_id = request.form.get('user_id')
    if bn == None or en == None:
        return "got a blank input"
    return con.keyword_insert(en, bn, user_id)


# insert new keyword
@app.route('/keyword/update', methods=['POST'])
def keyword_update():
    con = Operations()
    kw_id = None
    bn = None
    en = None
    kw_id = request.form.get('kw_id')
    bn = request.form.get('bn')
    en = request.form.get('en')
    user_id = request.form.get('user_id')
    if bn == None or en == None:
        return "got a blank input"
    return con.keyword_update(kw_id, en, bn, user_id)

# Search keyword
@app.route('/keyword/search', methods=['POST'])
def search_keyword():
    con = Operations()
    en = None
    en = request.form.get('en')
    if en == None:
        return "got a blank input"
    return con.search_keyword(en)

# Delete Keyword
@app.route('/keyword/<int:kw_id>', methods=['DELETE'])
def delete_keyword(kw_id):
    con = Operations()
    return con.delete_keyword(kw_id)


# insert new area
@app.route('/area', methods=['POST'])
def area_insert():
    con = Operations()
    area = None
    area = request.form.get('areaname')
    if area == None:
        return "got a blank input"
    return con.area_insert(area)

# update area
@app.route('/area/update', methods=['POST'])
def area_update():
    con = Operations()
    area_id = None
    area = None
    area_id = request.form.get('area_id')
    area = request.form.get('areaname')

    if area == None:
        return "got a blank input"
    return con.area_update(area_id, area)


# Search Area
@app.route('/area/search', methods=['POST'])
def search_area():
    con = Operations()
    area = None
    area = request.form.get('area')
    if area == None:
        return "got a blank input"
    return con.search_area(area)

# Delete Area
@app.route('/area/<int:area_id>', methods=['DELETE'])
def delete_area(area_id):
    con = Operations()
    return con.delete_area(area_id)

# insert new subarea
@app.route('/subarea', methods=['POST'])
def subarea_insert():
    con = Operations()
    area = None
    subarea = None
    fhouse = None
    froad = None
    fblock = None
    fsuparea = None
    fsubarea = None
    area_regex = None
    subarea_regex = None
    area = request.form.get('area')
    subarea = request.form.get('subarea')
    fhouse = request.form.get('fhouse')
    froad = request.form.get('froad')
    fblock = request.form.get('fblock')
    fsuparea = request.form.get('fsuparea')
    fsubarea = request.form.get('fsubarea')
    area_regex = request.form.get('area_regex')
    subarea_regex = request.form.get('subarea_regex')
    if area == None or subarea == None or fhouse == None or froad == None or fblock == None or fsuparea == None or fsubarea == None or area_regex == None or subarea_regex == None:
        return "got a blank input"
    return con.subarea_insert(area, subarea, fhouse, froad, fblock, fsuparea, fsubarea, area_regex, subarea_regex)

# update subarea
@app.route('/subarea/update', methods=['POST'])
def subarea_update():
    con = Operations()
    subarea_id = None 
    area = None
    subarea = None
    fhouse = None
    froad = None
    fblock = None
    fsuparea = None
    fsubarea = None
    area_regex = None
    subarea_regex = None
    subarea_id = request.form.get('subarea_id')
    area = request.form.get('area')
    subarea = request.form.get('subarea')
    fhouse = request.form.get('fhouse')
    froad = request.form.get('froad')
    fblock = request.form.get('fblock')
    fsuparea = request.form.get('fsuparea')
    fsubarea = request.form.get('fsubarea')
    area_regex = request.form.get('area_regex')
    subarea_regex = request.form.get('subarea_regex')
    if area == None or subarea == None or fhouse == None or froad == None or fblock == None or fsuparea == None or fsubarea == None or area_regex == None or subarea_regex == None:
        return "got a blank input"
    return con.subarea_update(subarea_id, area, subarea, fhouse, froad, fblock, fsuparea, fsubarea, area_regex, subarea_regex)

# Search Subarea
@app.route('/subarea/search', methods=['POST'])
def search_subarea():
    con = Operations()
    subarea = None
    subarea = request.form.get('subarea')
    if subarea == None:
        return "got a blank input"
    return con.search_subarea(subarea)


# Delete Area
@app.route('/subarea/<int:subarea_id>', methods=['DELETE'])
def delete_subarea(subarea_id):
    con = Operations()
    return con.delete_subarea(subarea_id)

# insert new union,division,subdivision
@app.route('/dsu', methods=['POST'])
def dsu_insert():
    con = Operations()
    union = None
    subdivision = None
    division = None
    union = request.form.get('union')
    subdivision = request.form.get('subdivision')
    division = request.form.get('division')

    if union == None or subdivision == None or division == None:
        return "got a blank input"
    return con.dsu_insert(union, subdivision, division)


# Update union,division,subdivision
@app.route('/dsu/update', methods=['POST'])
def dsu_update():
    con = Operations()
    dsu_id = None
    union = None
    subdivision = None
    division = None
    dsu_id = request.form.get('dsu_id')
    union = request.form.get('union')
    subdivision = request.form.get('subdivision')
    division = request.form.get('division')

    if union == None or subdivision == None or division == None:
        return "got a blank input"
    return con.dsu_update(dsu_id, union, subdivision, division)


# Search DSU
@app.route('/dsu/search', methods=['POST'])
def search_dsu():
    con = Operations()
    dsu = None
    dsu = request.form.get('dsu')
    if dsu == None:
        return "got a blank input"
    return con.search_dsu(dsu)

# Delete DSU
@app.route('/dsu/<int:dsu_id>', methods=['DELETE'])
def delete_dsu(dsu_id):
    con = Operations()
    return con.delete_dsu(dsu_id)


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8010)
