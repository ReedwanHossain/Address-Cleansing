from flask_cors import CORS
import json
from flask import Flask, request, send_from_directory, make_response
from flask_restful import reqparse, abort, Api, Resource
import urllib
import re
# import io
import codecs
import csv
from logging.handlers import RotatingFileHandler
from time import strftime
from bkoi_parser import Address
from custom_banglish_transformer.bkoi_transformer import Transformer

import logging
import traceback

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
            result_array.append({'input-address': input_address ,'clean-address': result['address'], 'status':  result['status'], 'geocoded-address':  result['geocoded']['Address']})
           
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


@app.route('/transparse', methods = ['POST'])
def transform_parse():
   add_trans = None
   add_parse = None
   add_trans = Transformer()
   add_parse = Address()
   addr = request.form.get('addr')
   return add_parse.parse_address(add_trans.bangla_to_english(addr))



@app.after_request
def after_request(response):
    """ Logging after every request. """
    # This avoids the duplication of registry in the log,
    # since that 500 is already logged via @app.errorhandler.
    if response.status_code != 500:
        ts = strftime('[%Y-%b-%d %H:%M]')
        logger.error('%s %s %s\n%s\n%s\n=================',
                      ts,
                      request.remote_addr,
                      request.full_path,
                      request.form.to_dict(),
                      json.loads(response.data)
                      )
    return response


@app.errorhandler(Exception)
def exceptions(e):
    """ Logging after every Exception. """
    ts = strftime('[%Y-%b-%d %H:%M]')
    tb = traceback.format_exc()
    logger.error('%s %s %s %s\n%s\n5xx INTERNAL SERVER ERROR\n%s\n===============',
                  ts,
                  request.remote_addr,
                  request.method,
                  request.full_path,
                  request.form.to_dict(),
                  tb)
    return "Internal Server Error", 500




if __name__ == '__main__':
    # maxBytes to small number, in order to demonstrate the generation of multiple log files (backupCount).
    handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=50)
    # getLogger(__name__):   decorators loggers to file + werkzeug loggers to stdout
    # getLogger('werkzeug'): decorators loggers to file + nothing to stdout
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.ERROR)
    logger.addHandler(handler)
    app.run(debug=True, host = '127.0.0.1', port = 8010)
