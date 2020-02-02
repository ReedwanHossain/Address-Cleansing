from flask_cors import CORS
import json
from flask import Flask, request, send_from_directory, make_response
from flask_restful import reqparse, abort, Api, Resource
import urllib
import re
# import io
import codecs
import csv
from bkoi_parser import Address
from bkoi_normalizer import AddressParser
from custom_banglish_transformer.bkoi_transformer import Transformer
from dbconf.db_operations import Operations
import similarity


app = Flask(__name__)
CORS(app)

add_parse = Address()

@app.route('/uploader', methods = ['POST'])
def upload_file():
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
              result_array.append({'input-address': input_address ,'clean-address': result['address'], 'status':  result['status'], 'geocoded-address':  result['geocoded']['Address']})
            except Exception as e:
              result_array.append({'input-address': input_address ,'clean-address': result['address'], 'status':  result['status'], 'geocoded-address':  'Failed to GeoCode'})

                       
        csv_columns = ['input-address' ,'clean-address', 'status', 'geocoded-address']
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


@app.route('/address/matcher', methods = ['POST'])
def matcher():
    add_trans = None
    add_trans = Transformer()
    addr1 = request.form.get('addr1')
    addr2 = request.form.get('addr2')
    addr1=add_trans.bangla_to_english(addr1)
    addr2=add_trans.bangla_to_english(addr2)
    addr1=similarity.bkoi_addess_cleaner(addr1)
    addr2=similarity.bkoi_addess_cleaner(addr2)
    print(addr1+"   "+addr2)
    print (similarity.bkoi_address_matcher(addr1,addr2))
    return similarity.bkoi_address_matcher(addr1,addr2)


@app.route('/parse', methods = ['POST'])
def parse_it():
   addr = request.form.get('addr')
   # de_addr = urllib.unquote(addr)
   # print "address.........."+de_addr
   return add_parse.parse_address(addr)



@app.route('/parser', methods = ['GET'])
def parser():
   addr = request.args.get('addr')
   # de_addr = urllib.unquote(addr)
   # print "address.........."+de_addr
   return add_parse.parse_address(addr)



@app.route('/transform', methods = ['GET'])
def transform_addr():
   add_trans = None
   add_trans = Transformer()
   addr = request.args.get('addr')
   # de_addr = urllib.unquote(addr)
   # print "address.........."+de_addr
   return add_trans.bangla_to_english(addr)


@app.route('/transformer', methods = ['POST'])
def transformer_addr():
   add_trans = None
   add_trans = Transformer()
   addr = request.form.get('addr')
   # de_addr = urllib.unquote(addr)
   # print "address.........."+de_addr
   return add_trans.bangla_to_english(addr)

@app.route('/rupantor/parse', methods = ['POST'])
def rupantor_parse():
   ob_trans = None
   ob_parse = None
   ob_trans = Transformer()
   ob_parse = AddressParser()
   addr = request.form.get('addr')
   print("Vatiza called ................... "+addr)
   return ob_parse.rupantor_parse_address(ob_trans.bangla_to_english(addr))

@app.route('/transparse', methods = ['POST'])
def transform_parse():
   add_trans = None
   add_parse = None
   add_trans = Transformer()
   add_parse = Address()
   addr = request.form.get('addr')
   return add_parse.parse_address(add_trans.bangla_to_english(addr))


### insert new keyword
@app.route('/keyword', methods = ['POST'])
def keyword_insert():
  con=Operations()
  bn=None
  en=None
  bn = request.form.get('bn')
  en = request.form.get('en')
  user_id = request.form.get('user_id')
  if bn==None or en==None:
    return "got a blank input"
  return con.keyword_insert(en,bn,user_id)

### Search keyword
@app.route('/keyword/search', methods = ['POST'])
def search_keyword():
  con=Operations()
  en=None 
  en=request.form.get('en')
  if en==None:
    return "got a blank input"
  return con.search_keyword(en)

### Delete Keyword
@app.route('/keyword/<int:kw_id>', methods=['DELETE'])
def delete_keyword():
    con=Operations()
    return con.delete_keyword(kw_id)



### insert new area
@app.route('/area', methods = ['POST'])
def area_insert():
  con=Operations()
  area=None
  area = request.form.get('areaname')
  if area==None :
    return "got a blank input"
  return con.area_insert(area)


### Search Area
@app.route('/area/search', methods = ['POST'])
def search_area():
  con=Operations()
  area=None 
  area=request.form.get('area')
  if area==None:
    return "got a blank input"
  return con.search_area(area)

### Delete Area
@app.route('/area/<int:area_id>', methods=['DELETE'])
def delete_area(area_id):
    con=Operations()
    return con.delete_area(area_id)

### insert new subarea
@app.route('/subarea', methods = ['POST'])
def subarea_insert():
  con=Operations()
  area=None
  subarea=None
  fhouse=None
  froad=None
  fblock=None
  fsuparea=None
  fsubarea=None
  area = request.form.get('area')
  subarea = request.form.get('subarea')
  fhouse = request.form.get('fhouse')
  froad = request.form.get('froad')
  fblock = request.form.get('fblock')
  fsuparea = request.form.get('fsuparea')
  fsubarea = request.form.get('fsubarea')
  if area==None or subarea==None or fhouse==None or froad==None or fblock==None or fsuparea==None or fsubarea==None:
    return "got a blank input"
  return con.subarea_insert(area,subarea,fhouse,froad,fblock,fsuparea,fsubarea)

### Search Subarea
@app.route('/subarea/search', methods = ['POST'])
def search_subarea():
  con=Operations()
  subarea=None 
  subarea=request.form.get('subarea')
  if subarea==None:
    return "got a blank input"
  return con.search_subarea(subarea)


### Delete Area
@app.route('/subarea/<int:subarea_id>', methods=['DELETE'])
def delete_subarea(subarea_id):
    con=Operations()
    return con.delete_subarea(subarea_id)

### insert new union,division,subdivision
@app.route('/dsu', methods = ['POST'])
def dsu_insert():
  con=Operations()
  union=None
  subdivision=None
  division=None
  union = request.form.get('union')
  subdivision = request.form.get('subdivision')
  division = request.form.get('division')

  if union==None or subdivision==None or division==None:
    return "got a blank input"
  return con.dsu_insert(union,subdivision,division)


### Search DSU
@app.route('/dsu/search', methods = ['POST'])
def search_dsu():
  con=Operations()
  dsu=None 
  dsu=request.form.get('dsu')
  if dsu==None:
    return "got a blank input"
  return con.search_dsu(dsu)

### Delete DSU
@app.route('/dsu/<int:dsu_id>', methods=['DELETE'])
def delete_dsu(dsu_id):
    con=Operations()
    return con.delete_dsu(dsu_id)


if __name__ == '__main__':
    app.run(debug=True, host = '127.0.0.1', port = 8010)
