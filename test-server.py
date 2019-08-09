from flask_cors import CORS
from flask import Flask, request
from flask_restful import reqparse, abort, Api, Resource
import urllib
import re
import nltk
import csv
from nltk.tokenize import sent_tokenize, word_tokenize
#nltk.download('all')
class Address(object):
       
    # initializaion............................
    def __init__(self):
        self.dict_data = []
        self.addresskey = 'address'
        self.namekey = 'name'
        self.housekey = 'House'
        self.roadkey = 'road'
        self.ssareakey = 'supersubarea'
        self.subareakey = 'subarea'
        self.areakey = 'area'
        self.house_nokey = 'house_no'
        self.road_idkey = 'road_id'
        self.area_idkey = 'area_id'
        self.subarea_idkey = 'subarea_id'
        self.supersubarea_idkey = 'supersubarea_id'
        # flags.......................
        self.area_flag = False
        self.area_pos = 0
        self.subarea_flag = False
        self.subarea_pos = 0
        self.matched = {}
        #init value...................
        self.matched[self.housekey] = None
        self.matched[self.roadkey] = None
        self.matched[self.ssareakey] = None
        self.matched[self.subareakey] = None
        self.matched[self.areakey] = None
        self.cleanAddressStr = ''
        self.tempArray = []
        self.matched_array = []

    prefix_dict = ['', 'east', 'west', 'north', 'south', 'middle', 'purba', 'poschim', 'uttar', 'dakshin', 'moddho', 'dokkhin', 'dakkhin']

    address_component = ['', 'house', 'plot', 'road', 'block', 'section', 'sector', 'avenue']

    rep2 = {
        "rd#": " road ", "rd-": " road  ", "rd:": " road  ", "r:": " road ", "r#": " road ", " r-": " road ", " ,r-": " road ", "h#": " house ", "h-": " house ", "h:": " house ",
        "bl-":" block ","bl#":" block ", "bl:":" block ", "b-":" block ","b:":" block ", "b#":" block ", 'sec-': ' section ','sec#': ' section ', 'sec:': ' section ', 's-': ' sector ', 's#': ' sector ', 's:': ' sector ',
        'house': ' house ', 'house:': ' house ', 'road': ' road ', 'road:': ' road ', 'block-': ' block ', 'block:': ' block ', 'section': ' section ','section:': ' section ', 'sector': ' sector ','sector:': ' sector ',
        'house no': ' house ', 'houseno:': ' house ', 'road no': ' road ', 'road no': ' road ', 'block no': ' block ', 'blockno': ' block ', 'section no': ' section ','sectionno': ' section ', 'sector no': ' sector ','sector': ' sector ',
        'ave-': ' avenue ', 'ave:': ' avenue ', 'ave#': ' avenue ','ave:': ' avenue ', 'avenue:': ' avenue ', 'avenue-': ' avenue ', 'avenue#': ' avenue ', 'no :': '', 'no:': '', 'no -': '', 'no-': '', 'no =': '', 'no=': '', 'no.': '',
    } 
    area_dict = {"mirpur": " mirpur ", "uttara": " uttara ", "banani": " banani ", "mohammadpur": " mohammadpur ", "gulshan": " gulshan ", "baridhara": " baridhara ", "mdpur":"mohammadpur"} # define desired replacements here
        
    def multiple_replace(self, dict, text):
        # Create a regular expression  from the dictionary keys
        regex = re.compile("(%s)" % "|".join(map(re.escape, dict.keys())))
        # For each match, look-up corresponding value in dictionary
        return regex.sub(lambda mo: dict[mo.string[mo.start():mo.end()]], text) 

    def check_area(self, token, idx):

        area_token = self.multiple_replace(self.area_dict, token.lower())
        area_token = word_tokenize(area_token)
        with open('./area-list.csv','rt')as f:
          area_list = csv.reader(f)
          for j, area in enumerate(area_list):
                if (area_token[0].lower() == area[0].lower() and area_token[0].lower() in self.cleanAddressStr.lower()):
                    self.matched[self.areakey] = area[0].lower()
                    # matched_array.append(area[0].lower())
                    self.area_flag = True 
                    self.area_pos = idx
                    for i, comp in enumerate(self.tempArray):
                        self.check_sub_area(comp, i)
                        continue
                    return True


    def check_sub_area(self, token, idx):
        
        if self.area_flag== True:
            area = self.matched[self.areakey].lower()
            if (idx-self.area_pos == 1 and any(char.isdigit() for char in self.tempArray[idx])):
                # print "tempArray[idx] from subarea "+tempArray[idx]
                if(area.lower() == 'mirpur'):
                    token = 'section '+ self.tempArray[idx]
                elif(area.lower() == 'uttara'):
                    token = 'sector '+ self.tempArray[idx]
                elif token == 'block' and area.lower() == 'bashundhara' or area.lower() == 'banani' or area.lower() == 'khilgaon' or area.lower() == 'banasree' or area.lower() == 'baridhara' or area.lower() == 'lalmatia':
                    if idx != len(self.tempArray)-1:
                        token = token+" "+self.tempArray[idx+1]
                with open('./subarea-list.csv','rt')as f:
                    subarea_list = csv.reader(f)
                    for j, subarea in enumerate(subarea_list):
                        if (area.lower() == subarea[0].lower() and token.lower() == subarea[1].lower()):
                            self.matched[self.subareakey] = token.lower()
                            self.subarea_flag = True
                            return True

            elif(abs(idx-self.area_pos) > 1 or abs(idx-self.area_pos) == 1 and not any(char.isdigit() for char in self.tempArray[idx])):
                token = token.lstrip('[0:!@#$-=+.]')
                token = token.rstrip('[:!@#$-=+.]')
                prefix_flag = False      
                if (token.lower() =='section' or token.lower() =='sector' and token.lower() in self.cleanAddressStr.lower()):
                        self.matched[self.subareakey] = token +' '+ self.tempArray[idx+1]
                        if (area.lower()=='mirpur'):
                            self.matched[self.subareakey] = 'section' +' '+ self.tempArray[idx+1]
                        elif(area.lower()=='uttara'):
                          self. matched[self.subareakey] = 'sector' +' '+ self.tempArray[idx+1]
                        self.subarea_flag = True
                        return True

                with open('./subarea-list.csv','rt')as f:
                    subarea_list = csv.reader(f)
                    for j, subarea in enumerate(subarea_list):
                        if (area.lower() == subarea[0].lower() and (token.lower() in subarea[1].lower() and subarea[1].lower() in self.cleanAddressStr.lower())):
                            self.matched[self.subareakey] = subarea[1].lower()
                            # matched_array.append(matched[subareakey])
                            self.subarea_flag = True
        

        elif self.area_flag == False:
            with open('./subarea-list.csv','rt')as f:
                subarea_list = csv.reader(f)
                for j, subarea in enumerate(subarea_list):
                    if (token.lower() in subarea[1].lower() and subarea[1].lower() in self.cleanAddressStr.lower()):
                        self.matched[self.subareakey] = subarea[1].lower()
                        self.matched[self.areakey] = subarea[0].lower()
                        # matched_array.append(matched[areakey])
                        # matched_array.append(matched[subareakey])
                        self.subarea_flag = True
                        return True        


    def check_super_sub_area(self, token, idx):
        if ('block' in self.cleanAddressStr and 'mirpur' in self.cleanAddressStr.lower() and token == 'block'):
            if idx != len(self.tempArray)-1:
                self.matched[self.ssareakey] = token+" "+self.tempArray[idx+1]
                return True


    def check_holding(self, token, idx):
        if (any(char.isdigit() for char in token)):
            if idx == 0:
                self.matched[self.housekey] = token
                # matched_array.append(token)
                return True

        elif ((token.lower() == 'house' or token.lower() == 'plot') and idx < len(self.tempArray)-1):
            if (any(char.isdigit() for char in self.tempArray[idx+1])):
                self.matched[self.housekey] = self.tempArray[idx+1]
                # matched_array.append(tempArray[idx+1])
                return True



    def check_road(self, road, idx):
        if 'road' in road or 'ave' in road or 'lane' in road or 'sarani' in road or 'soroni' in road or 'rd' in road or 'rd#' in road or 'sarak' in road or 'sharak' in road or 'shorok' in road or 'sharani' in road or 'highway' in road or 'path' in road or 'poth' in road or 'chowrasta' in road or 'rasta' in road or 'sorok' in road or 'goli' in road or 'street' in road:
            if idx != len(self.tempArray)-1:
                if (any(char.isdigit() for char in self.tempArray[idx+1])):
                    if(self.matched[self.roadkey]==None):
                            self.matched[self.roadkey] = road+" "+self.tempArray[idx+1]
                            return True
                    self.matched[self.roadkey] = self.matched[self.roadkey] +", "+road+" " +self.tempArray[idx+1]
                    return True
            if idx != 0:
                if (not any(char.isdigit() for char in self.tempArray[idx-1])):
                    i = idx-1
                    road_str =  ''
                    if (not self.matched[self.areakey] == None and self.tempArray[i] == self.matched[self.areakey]):
                        self.matched[self.roadkey] = self.matched[self.areakey] +" "+ road
                        return True

                    while i>=0:
                        if not i==0 and self.tempArray[i-1] in self.address_component or self.tempArray[i-1] in self.matched_array:
                            if not any(char.isdigit() for char in self.tempArray[i]):
                                road_str = self.tempArray[i]+ " " + road_str
                                break
                            break
                        road_str = self.tempArray[i] +" "+ road_str
                        i=i-1
                    if(self.matched[self.roadkey]==None):
                        self.matched[self.roadkey] = road_str + road
                        return True
                    self.matched[self.roadkey] = self.matched[self.roadkey] +", "+road_str + road
                    # matched_array.append(matched[roadkey])
                    return True

    def parse_address(self, input_address):
        input_address = " "+input_address
        input_address = re.sub( r'([a-zA-Z])(\d)', r'\1-\2', input_address ) #insert a '-' between letters and number

        # pre-processing...........................................................
        expand = self.multiple_replace(self.rep2, input_address.lower())
        expand = self.multiple_replace(self.area_dict, expand.lower())
        addresscomponents = word_tokenize(expand)

        for i, comp in enumerate(addresscomponents):
                comp=comp.strip()
                if comp == "," or comp == "":
                    continue
               
                temp = comp.lstrip('[0:!@#$-=+.]')
                temp = temp.rstrip('[:!@#$-]=+.')
                temp = temp.strip(" ");
                if(temp != ""):
                    self.tempArray.append(temp)
                # print comp.rstrip('[!@#$-]')
        print "final pre-processing "
        self.cleanAddressStr = ' '.join(self.tempArray)
        self.cleanAddressStr = re.sub(r" ?\([^)]+\)", "", self.cleanAddressStr)
        print self.cleanAddressStr
        self.tempArray = word_tokenize(self.cleanAddressStr)
        print self.tempArray
        print "\n"

        # Parsing..............................
        for i, comp in enumerate(self.tempArray):
                comp=comp.strip()
                # print(comp)
                if (self.check_area(comp, i)):
                    self.matched_array.append(self.matched[self.areakey])
                    pass
                if (self.check_sub_area(comp, i)):
                    self.matched_array.append(self.matched[self.subareakey])
                    pass
                if (self.check_super_sub_area(comp, i)):
                    self.matched_array.append(self.matched[self.ssareakey])
                    pass
                if (self.check_holding(comp, i)):
                    self.matched_array.append(self.matched[self.housekey])
                    pass
                if (self.check_road(comp, i)):
                    self.matched_array.append(self.matched[self.roadkey])
                    pass


        print('Parse Result')

        final_address = self.bind_address()
        return final_address

    def bind_address(self):
        try:
            self.matched[self.housekey] = "house "+self.matched[self.housekey]+", "
        except Exception as e:
            self.matched[self.housekey] = '' 

        try:
            self.matched[self.roadkey] = self.matched[self.roadkey]+", "
        except Exception as e:
            self.matched[self.roadkey] = ''

        try:
            self.matched[self.ssareakey] = self.matched[self.ssareakey]+", "
        except Exception as e:
            self.matched[self.ssareakey] = ''

        try:
            self.matched[self.subareakey] = self.matched[self.subareakey]+", "
        except Exception as e:
            self.matched[self.subareakey] = ''

        try:
            self.matched[self.areakey] = self.matched[self.areakey]+","
        except Exception as e:
            self.matched[self.areakey] = ''

        full_address = self.matched[self.housekey] + self.matched[self.roadkey] + self.matched[self.ssareakey] + self.matched[self.subareakey] + self.matched[self.areakey]
        full_address = full_address.lstrip(' ,')
        full_address = full_address.rstrip(' ,')
        return full_address
        


    # def file_parse(self, test_data):

    #     for t, td in enumerate(test_data):
    #         input_address = td['address']
    #         # input_address = raw_input('Enter Address: ')
    #         input_address = " "+input_address
    #         print input_address+"\n"
    #         input_address = re.sub( r'([a-zA-Z])(\d)', r'\1-\2', input_address ) #insert a '-' between letters and number
    #         expand = self.multiple_replace(self.rep2, input_address.lower())
    #         expand = self.multiple_replace(self.area_dict, expand.lower())
    #         addresscomponents = word_tokenize(expand)

    #         for i, comp in enumerate(addresscomponents):
    #                 comp=comp.strip()
    #                 if comp == "," or comp == "":
    #                     continue
                   
    #                 temp = comp.lstrip('[0:!@#$-=+.]')
    #                 temp = temp.rstrip('[:!@#$-]=+.')
    #                 temp = temp.strip(" ");
    #                 if(temp != ""):
    #                     self.tempArray.append(temp)
    #                 # print comp.rstrip('[!@#$-]')
    #         print "final pre-processing "
    #         self.cleanAddressStr = ' '.join(self.tempArray)
    #         self.cleanAddressStr = re.sub(r" ?\([^)]+\)", "", self.cleanAddressStr)
    #         print self.cleanAddressStr
    #         self.tempArray = word_tokenize(self.cleanAddressStr)
    #         print self.tempArray
    #         print "\n"

    #         # Parsing..............................
    #         for i, comp in enumerate(self.tempArray):
    #                 comp=comp.strip()
    #                 # print(comp)
    #                 if (self.check_area(comp, i)):
    #                     self.matched_array.append(self.matched[self.areakey])
    #                     print 'area'
    #                     pass
    #                 if (self.check_sub_area(comp, i)):
    #                     self.matched_array.append(self.matched[self.subareakey])
    #                     print 'subarea'
    #                     pass
    #                 if (self.check_super_sub_area(comp, i)):
    #                     self.matched_array.append(self.matched[self.ssareakey])
    #                     print 'ssarea check'
    #                     pass
    #                 if (self.check_holding(comp, i)):
    #                     self.matched_array.append(self.matched[self.housekey])
    #                     print 'holding check'
    #                     pass
    #                 if (self.check_road(comp, i)):
    #                     self.matched_array.append(self.matched[self.roadkey])
    #                     print 'road check'
    #                     pass


    #         print('Parse Result')
    #         print self.matched
    #         print ('................................................................................')
    #         self.dict_data.append(self.matched)


    #     csv_columns = ['address', 'area','subarea','supersubarea', 'house', 'road']
    #     csv_file = "outputfile.csv"
    #     try:
    #         with open(csv_file, 'w') as csvfile:
    #             writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
    #             writer.writeheader()
    #             for data in sefl.dict_data:
    #                 writer.writerow(data)
    #     except IOError:
    #         print("I/O error") 
    #     return 'done'



#Flask App.................................
app = Flask(__name__)
CORS(app)

# @app.route('/uploader', methods = ['GET', 'POST'])
# def upload_file():
#    if request.method == 'POST':
#       add_parse = None
#       add_parse = Address()
#       fstring = csv.DictReader(request.files['file'])
#       add_parse.file_parse(fstring)
#       return 'okk'

@app.route('/parse', methods = ['GET'])
def parse_it():
   add_parse = None
   add_parse = Address()
   addr = request.args.get('addr')
   de_addr = urllib.unquote(addr)
   print "address.........."+de_addr
   return add_parse.parse_address(de_addr)


if __name__ == '__main__':
    app.run(debug=True, host = '127.0.0.1', port = 8070)