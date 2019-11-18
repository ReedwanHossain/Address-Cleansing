from flask_cors import CORS
import requests
from json import dumps
from flask import Flask, request, send_from_directory, make_response
from flask_restful import reqparse, abort, Api, Resource
from fuzzywuzzy import fuzz
import urllib
import re
import csv


from dbconf.initdb import DBINIT
dbinit = DBINIT()
dbinit.load_area()
dbinit.load_subarea()
dbinit.load_dsu()

from miniparser import MiniParser
from spellcheck import SpellCheck
class Address(object):
       
    # initializaion............................
    def __init__(self):
        self.dict_data = []
        self.addresskey = 'address'
        self.namekey = 'name'
        self.housekey = 'House'
        self.buildingkey = 'building'
        self.roadkey = 'road'
        self.ssareakey = 'supersubarea'
        self.subareakey = 'subarea'
        self.areakey = 'area'
        self.districtkey = 'district'
        self.sub_districtkey = 'sub_district'
        self.unionkey = 'union'
        self.blockkey='block'
        # flags.......................
        self.area_flag = False
        self.area_pos = 0
        self.subarea_flag = False
        self.subarea_pos = 0
        self.matched = {}
        #init value...................
        self.matched[self.housekey] = None
        self.matched[self.buildingkey] = None
        self.matched[self.roadkey] = None
        self.matched[self.ssareakey] = None
        self.matched[self.subareakey] = None
        self.matched[self.areakey] = None
        self.matched[self.districtkey] = None
        self.matched[self.sub_districtkey] = None
        self.matched[self.unionkey] = None
        self.matched[self.blockkey] = None
        self.tempArray = []
        self.usedToken= []
        self.matched_array = []
        self.area_pattern = None
        self.get_multiple_subarea=[]
        self.get_multiple_area=[]
        self.subarea_list_pattern=[]
        
    status_pattern= {
    'house':'',
    'road':'',
    'block':'',
    'ssarea':'',
    'subarea':'',

    }

    prefix_dict = ['', 'east', 'west', 'north', 'south', 'middle', 'purba', 'poschim', 'uttar', 'dakshin', 'moddho', 'dokkhin', 'dakkhin']

    address_component = ['','sarani','sarak','rasta','goli','lane','code','street','floor','level', 'house', 'plot', 'road', 'block', 'section', 'sector', 'avenue']
    
    building_name_key = ['building','plaza' , 'market', 'bazar' , 'villa' , 'cottage' , 'mansion' , 'vila' , 'tower' , 'place' , 'complex' , 'center' , 'centre' , 'mall' , 'square', 'monjil' , 'manjil' , 'building' , 'headquarter' , 'bhaban', 'mosque', 'masjid', 'mosjid','hospital','university','school','mandir','mondir','police station', 'club', 'garage', 'office', 'restaurent', 'cafe', 'hotel', 'garments', 'park', 'field', 'garden', 'studio', 'stadium', 'meusium', 'institute', 'store', 'college', 'varsity', 'coaching', 'library', 'tution', 'bank', 'atm', 'agent', 'Ministry', 'workshop', 'saloon', 'tailors', 'pharmacy', 'textile', 'laundry', 'hall']
    tempList=['ka','kha','ga','gha','uma','ca','cha','ja','jha','za','zha','ta','tha','da','dha','na','pa','pha','fa','ma','ra','la','ha','ya', 'gp']
    rep2 = {
        #' east':' east ', ' west':' west ', ' north':' north ', ' south':' south ', ' middle':' middle ', ' purba':' purba ', ' poschim':' poschim ', ' uttar':' uttar ', ' dakshin':' dakshin ', ' moddho':' moddho ', ' dokkhin':' dokkhin ', ' dakkhin':' dakkhin ',
        "rd#": " road ", "rd-": " road  ", " rd": " road  "," road#": " road  ", "rd:": " road  ", "r:": " road ", "r#": " road ","road #": " road ", " r ": " road ", " r-": " road ", " ,r-": " road ",",r":" road ", "h#": " house ", "h-": " house ", "h:": " house ", " h ": " house ",
        "bl-":" block ","bl ":" block ", " b ":" block ", "bl#":" block ", "bl:":" block ", "b-":" block ","b:":" block ", "b#":" block ", 'sec-': ' sector ', ' sec ':' sector ', 'sec#': ' sector ', 'sec:': ' sector ', 's-': ' sector ', ' s-': ' sector ', 's#': ' sector ', 's:': ' sector ', ' s ': ' sector ',
        'house': ' house ', 'house:': ' house ', 'road': ' road ', 'road:': ' road ', 'block': ' block ', 'block-': ' block ', 'block:': ' block ', 'block#': ' block ', 'section': ' section ','section:': ' section ', 'sector': ' sector ','sector:': ' sector ',
        'house no': ' house ', 'house no ': ' house ', 'houseno:': ' house ', 'road no': ' road ', 'road no': ' road ', 'block no': ' block ', 'blockno': ' block ', 'section no': ' section ','sectionno': ' section ', 'sector no': ' sector ','sector': ' sector ',
        'ave-': ' avenue ', 'ave:': ' avenue ', 'ave#': ' avenue ','ave:': ' avenue ', 'avenue:': ' avenue ', 'avenue-': ' avenue ', 'avenue#': ' avenue ', 'number':'', 'no :': '', 'no:': '', 'no -': '', 'no-': '', 'no =': '','no#': '', 'no=': '', 'no.': '', 'plot':' ',
    } 
    
    area_dict = {"nikunjo": " nikunja ", "nikunja": " nikunja ", "mirpur": " mirpur ", "uttara": " uttara ", "banani": " banani ", "mohammadpur": " mohammadpur ", "gulshan": " gulshan ", "baridhara": " baridhara ", "mdpur":"mohammadpur"} # define desired replacements here
    
    def multiple_replace(self, dict, text):
        # Create a regular expression  from the dictionary keys
        regex = re.compile("(%s)" % "|".join(map(re.escape, dict.keys())))
        # For each match, look-up corresponding value in dictionary
        return regex.sub(lambda mo: dict[mo.string[mo.start():mo.end()]], text) 


    def check_district(self, token, idx):
        dist_token = self.multiple_replace(self.area_dict, token.lower())
        #dist_token = word_tokenize(dist_token)
        dist_token = dist_token.split()

        district_list = dbinit.get_dsu()
        for j, district in enumerate(district_list):
                if (dist_token[0].lower() == district[2].lower() and dist_token[0].lower() in self.cleanAddressStr.lower()):
                    self.matched[self.districtkey] = district[2].lower()
                    return True


    def check_sub_district(self, token, idx):
        sub_dist_token = self.multiple_replace(self.area_dict, token.lower())
        #sub_dist_token = word_tokenize(sub_dist_token)
        sub_dist_token = sub_dist_token.split()
        with open('./dsu.csv','rt')as f:
          sub_district_list = csv.reader(f)
          for j, sub_district in enumerate(sub_district_list):
                if (sub_dist_token[0].lower() == sub_district[1].lower() and sub_dist_token[0].lower() in self.cleanAddressStr.lower()):
                    self.matched[self.sub_districtkey] = sub_district[1].lower()
                    return True

    def check_union(self, token, idx):
        union_token = self.multiple_replace(self.area_dict, token.lower())
        #union_token = word_tokenize(union_token)
        union_token = union_token.split()
        with open('./dsu.csv','rt')as f:
          union_list = csv.reader(f)
          for j, union in enumerate(union_list):
                if (union_token[0].lower() == union[0].lower() and union_token[0].lower() in self.cleanAddressStr.lower()):
                    self.matched[self.unionkey] = union[0].lower()
                    return True




    def check_area(self, token, idx):

        area_token = self.multiple_replace(self.area_dict, token.lower())
        #area_token = word_tokenize(area_token)
        area_token = area_token.split()
        
        area_list = dbinit.get_area()
        for j, area in enumerate(area_list):
            if (area_token[0].lower() == area.lower() and area_token[0].lower() in self.cleanAddressStr.lower()):
                self.matched[self.areakey] = area.lower()
                # matched_array.append(area[0].lower())
                self.area_flag = True 
                self.area_pos = idx
                self.get_multiple_area.append(area.lower())
                return True


    def check_sub_area(self, token, idx):
        
        if self.area_flag== True:
            area = self.matched[self.areakey].lower()
            if (idx-self.area_pos == 1 and any(char.isdigit() for char in self.tempArray[idx])):
                if(area.lower() == 'mirpur'):
                    token = 'section '+ self.tempArray[idx]
                elif(area.lower() == 'uttara'):
                    token = 'sector '+ self.tempArray[idx]
                
                subarea_list = dbinit.get_subarea()
                for j, subarea in enumerate(subarea_list):
                    if (area.lower() == subarea[0].lower() and token.lower() == subarea[1].lower()):
                        self.matched[self.subareakey] = token.lower()
                        self.subarea_flag = True
                        self.get_multiple_subarea.append(token.lower())
                        tempObj = {
                            'area': subarea[0].strip().lower(),
                            'subarea': subarea[1].lower(),
                            'pattern': [subarea[2], subarea[3], subarea[4], subarea[5], subarea[6]]                            }
                        self.subarea_list_pattern.append(tempObj)
                        return True

            elif(abs(idx-self.area_pos) > 1 or abs(idx-self.area_pos) == 1 and not any(char.isdigit() for char in self.tempArray[idx])):
                token = token.lstrip('[0:!@#$-=+.]')
                token = token.rstrip('[:!@#$-=+.]')
                prefix_flag = False      
                if ((token.lower() =='section' or token.lower() =='sector') and token.lower() in self.cleanAddressStr.lower() and idx < len(self.tempArray)-1):
                        self.matched[self.subareakey] = token +' '+ self.tempArray[idx+1]
                        if (area.lower()=='mirpur'):
                            self.matched[self.subareakey] = 'section' +' '+ self.tempArray[idx+1]
                            self.get_multiple_subarea.append('section' +' '+ self.tempArray[idx+1])
                            tempObj = {
                                'area': self.matched[self.areakey].lower(),
                                'subarea': self.matched[self.subareakey].lower(),
                                'pattern': ['H', 'H', 'H', 'L', 'H']                            
                            }
                            self.subarea_list_pattern.append(tempObj)
                        elif(area.lower()=='uttara'):
                            self. matched[self.subareakey] = 'sector' +' '+ self.tempArray[idx+1]
                            self.get_multiple_subarea.append('sector' +' '+ self.tempArray[idx+1])
                            tempObj = {
                                'area': self.matched[self.areakey].lower(),
                                'subarea': self.matched[self.subareakey].lower(),
                                'pattern': ['H', 'H', 'L', 'L', 'H'] 
                            }  
                            self.subarea_list_pattern.append(tempObj)
                        self.subarea_flag = True
                        return True

                subarea_list = dbinit.get_subarea()
                for j, subarea in enumerate(subarea_list):
                    # subarea[0] = subarea[0].strip()

                    if ( (token.lower() in subarea[1].lower() and subarea[1].lower() in self.cleanAddressStr.lower())):
                        self.matched[self.subareakey] = subarea[1].lower()
                        self.get_multiple_subarea.append(subarea[1].lower())
                        tempObj = {
                            'area': subarea[0].strip().lower(),
                            'subarea': subarea[1].lower(),
                            'pattern': [subarea[2], subarea[3], subarea[4], subarea[5], subarea[6]]                            
                        }  
                        self.subarea_list_pattern.append(tempObj)
                        # matched_array.append(matched[subareakey])
                        self.subarea_flag = True
        

        elif self.area_flag == False:
            subarea_list = dbinit.get_subarea()
            for j, subarea in enumerate(subarea_list):
                if (token.lower() in subarea[1].lower() and subarea[1].lower() in self.cleanAddressStr.lower()):
                    self.matched[self.subareakey] = subarea[1].lower()
                    self.matched[self.areakey] = subarea[0].lower()

                    self.get_multiple_subarea.append(subarea[1].lower())
                    self.get_multiple_area.append(subarea[0].lower())
                    tempObj = {
                        'area': subarea[0].strip().lower(),
                        'subarea': subarea[1].lower(),
                        'pattern': [subarea[2], subarea[3], subarea[4], subarea[5], subarea[6]]                            
                    }  
                    self.subarea_list_pattern.append(tempObj)
                    # matched_array.append(matched[areakey])
                    # matched_array.append(matched[subareakey])
                    self.subarea_flag = True
                    break

    def check_super_sub_area(self, token, idx):
        if ('block' in self.cleanAddressStr and 'mirpur' in self.cleanAddressStr.lower() and token == 'block'):
            if idx != len(self.tempArray)-1:
                self.matched[self.ssareakey] = token+" "+self.tempArray[idx+1]
                return True


    def check_holding(self, token, idx):
        tempList=['ka','kha','ga','gha','uma','ca','cha','ja','jha','za','zha','ta','tha','da','dha','na','pa','pha','fa','ma','ra','la','ha','ya', 'gp','rrrr']
        if (any(char.isdigit() for char in token) or token in tempList or re.match(r'^[a-z]$',token)) and idx < len(self.tempArray)-1 and self.matched[self.housekey]==None:
            if idx == 0 and self.tempArray[idx+1].lower()!='floor':
                self.matched[self.housekey] = token
                if ((any(char.isdigit() for char in self.tempArray[idx+1])) or re.match(r'^[a-z]$', self.tempArray[idx+1]) or (self.tempArray[idx+1] in tempList)) and idx < len(self.tempArray)-2 :
                    self.matched[self.housekey] = self.matched[self.housekey]+"-"+self.tempArray[idx+1] 
                    if idx < len(self.tempArray)-3:
                        if ((any(char.isdigit() for char in self.tempArray[idx+2])) or re.match(r'^[a-z]$', self.tempArray[idx+2]) or (self.tempArray[idx+2] in tempList)) :
                            self.matched[self.housekey] = self.matched[self.housekey]+"-"+self.tempArray[idx+2]
                return True


            if self.tempArray[idx-1].lower() not in self.address_component :
                check_match=0

                area_list = dbinit.get_subarea()
                for j, area in enumerate(area_list):
                    if area[0].lower()==self.tempArray[idx-1].lower():
                        check_match=1
                        break
                if self.matched[self.housekey]==None:
                    self.matched[self.housekey]=""
                if check_match==0 and token not in self.matched[self.housekey]:
                    self.matched[self.housekey]=token
                    if ((any(char.isdigit() for char in self.tempArray[idx+1])) or re.match(r'^[a-z]$', self.tempArray[idx+1]) or (self.tempArray[idx+1] in tempList))  and idx < len(self.tempArray)-2: 
                        self.matched[self.housekey] = self.matched[self.housekey]+"-"+self.tempArray[idx+1] 
                        if ((any(char.isdigit() for char in self.tempArray[idx+2])) or re.match(r'^[a-z]$', self.tempArray[idx+2]) or (self.tempArray[idx+2] in tempList)) and idx < len(self.tempArray)-3:
                             self.matched[self.housekey] = self.matched[self.housekey]+"-"+self.tempArray[idx+2] 
                    return True 
            return True


        elif ((token.lower() == 'house' or token.lower() == 'plot') and idx < len(self.tempArray)-1):
            tempList=set(tempList)
            if (any(char.isdigit() for char in self.tempArray[idx+1])) or (self.tempArray[idx+1] in tempList) or (re.match(r'^[a-z]$', self.tempArray[idx+1])) or (re.match(r'^[a-z]/[a-z]$', self.tempArray[idx+1])):
            #chk_house_no=re.search(r'\w', self.tempArray[idx+1].strip(","))
            #if chk_house_no:

                self.matched[self.housekey] = self.tempArray[idx+1]
                if idx < len(self.tempArray)-2:
                    p1=re.match(r'[0-9]+', self.tempArray[idx+2])
                    p2=re.match(r'^[a-z]$', self.tempArray[idx+2])
                    p3=re.match(r'^[A-Z]$', self.tempArray[idx+2])
                    if p1 or p2 or p3 or (self.tempArray[idx+2] in tempList):
                        self.matched[self.housekey] = self.tempArray[idx+1]+"-"+self.tempArray[idx+2]
                        if idx < len(self.tempArray)-3:
                            if ((any(char.isdigit() for char in self.tempArray[idx+3])) or re.match(r'^[a-z]$', self.tempArray[idx+3]) or (self.tempArray[idx+3] in tempList)) :
                                self.matched[self.housekey]=self.matched[self.housekey]+"-"+self.tempArray[idx+3]

                    # matched_array.append(tempArray[idx+1])
                return True


    def check_holding_name(self, token,idx):
        if any( char in token for char in self.building_name_key) and self.matched[self.buildingkey]==None:
            if idx != len(self.tempArray)-1 and idx != 0 :
                i=idx-1
                building_str = ''
                self.matched[self.buildingkey]=building_str
                while i>=0:
                    if any(char.isdigit() for char in self.tempArray[i]):
                        break
                    if not i==0 and (self.tempArray[i-1] in self.address_component or self.tempArray[i-1] in self.tempList):
                        if not any(char.isdigit() for char in self.tempArray[i]):
                            building_str = self.tempArray[i]+ " " + building_str
                            break
                        
                        break
                    building_str = self.tempArray[i] +" "+ building_str
                    i=i-1
                self.matched[self.buildingkey] = self.matched[self.buildingkey] +", "+building_str + token
                return True






    
    def check_block(self, token, idx):
        tempList=['ka','kha','ga','gha','uma','ca','cha','ja','jha','za','zha','ta','tha','da','dha','na','pa','pha','fa','ma','ra','la','ha','ya', 'gp']
        tempList=set(tempList)
        if (token.lower() == 'block' and idx < len(self.tempArray)-1):
            p=re.match(r'^(?=.*[0-9])(?=.*[a-zA-Z])([a-zA-Z0-9]+)$', self.tempArray[idx+1])
            p1=re.match(r'[0-9]+', self.tempArray[idx+1])
            p2=re.match(r'^[a-z]$', self.tempArray[idx+1])
            p3=re.match(r'^[A-Z]$', self.tempArray[idx+1])
            p_slash=re.match(r'(^[a-z])/[0-9]+$',self.tempArray[idx+1])
            p_hi=re.match(r'(^[a-z])-[0-9]+$',self.tempArray[idx+1])
            if p or p1 or p2 or p3 or p_slash or p_hi or (self.tempArray[idx+1] in tempList):
                self.matched[self.blockkey] = self.tempArray[idx+1]
            return True



    def check_road(self, road, idx):
        tempList=['ka','kha','ga','gha','uma','ca','cha','ja','jha','za','zha','ta','tha','da','dha','na','pa','pha','fa','ma','ra','la','ha','ya', 'gp']
        if 'road' in road or 'ave' in road or 'lane' in road or 'sarani' in road or 'soroni' in road or 'rd#' in road or 'sarak' in road or 'sharak' in road or 'shorok' in road or 'sharani' in road or 'highway' in road or 'path' in road or 'poth' in road or 'chowrasta' in road or 'sarak' in road or 'rasta' in road or 'sorok' in road or 'goli' in road or 'street' in road or 'line' in road :
            if 'ave' in road:
                road = 'avenue'

            if idx != len(self.tempArray)-1:
                if (any(char.isdigit() for char in self.tempArray[idx+1])):
                    num=re.findall(r'\d+', self.tempArray[idx+1])
                    num = max(map(int, num))
                    if(self.matched[self.roadkey]==None and num<1000):
                            self.matched[self.roadkey] = road+" "+self.tempArray[idx+1]
                            return True
                    #road x avenue y
                    if self.matched[self.roadkey]==None:
                        self.matched[self.roadkey]=''
                    if num<1000:
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
                        if any(char.isdigit() for char in self.tempArray[i]) or self.tempArray[i] in self.address_component:
                            break
                        if not i==0 and (self.tempArray[i-1] in self.address_component or self.tempArray[i-1] in self.building_name_key or self.tempArray[i-1] in tempList ):
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
        
    def check_address_status(self):
        area_pattern = dbinit.get_subarea()
        checkst=0
        getarea=0
        
        assignaddress=1
        self.matched[self.areakey]=self.matched[self.areakey].replace(',','')
        if self.matched[self.areakey] not in self.cleanAddressStr:
            same_sub_area_count=1
        self.matched[self.areakey]=self.matched[self.areakey].strip()
        if self.matched[self.areakey] in self.tempArray:
            assignaddress=0
        for j, status in enumerate(area_pattern):

            area_name=status[0].lower()
            sub_area_name=status[1].lower()
            house_st=status[2]
            road_st=status[3]
            block_st=status[4]
            ssarea_st=status[5]
            subarea_st=status[6]
            
            dict_areakey=self.matched[self.areakey].replace(',','')
            dict_sub_areakey=self.matched[self.subareakey].replace(',','')

            if self.matched[self.areakey]=='':
                checkst=1
                break
            if dict_sub_areakey.strip() == sub_area_name.strip() and area_name.strip()!=dict_areakey.strip() and assignaddress==1:
                same_sub_area_count+=1
                if same_sub_area_count>=2:
                    checkst=1
                    break

            elif dict_sub_areakey.strip() == sub_area_name.strip() and area_name.strip()==dict_areakey.strip():
                getarea=1
                if house_st=='H' and self.matched[self.housekey]=='':
                    checkst=1
                if road_st=='H' and self.matched[self.roadkey]=='':
                    checkst=1
                if block_st=='H' and self.matched[self.blockkey]=='':
                    checkst=1
                if ssarea_st=='H' and self.matched[self.ssareakey]=='':
                    checkst=1
                if subarea_st=='H' and self.matched[self.subareakey]=='':
                    checkst=1
        
        if checkst==1 or getarea==0:
            return "incomplete"
        elif getarea==1 and checkst==0:
            return "complete"
        else:
            return "incomplete"



    def parse_address(self, input_address):
        input_address = " "+input_address
        input_address = input_address.lower()
        
        input_address = re.sub(r',',' ', input_address)
        input_address = re.sub( r'#|"',' ', input_address )
        input_address=input_address.lower()+"  "
        input_address="  "+input_address.lower()
        input_address=re.sub(r'\([^)]*\)', '', input_address)
        #behind to hospital delete text

        if re.search('\d{5}',input_address):
            temp_input_address=input_address.split()
            for i,t in enumerate(temp_input_address):
                if re.search('\d{5}',t):
                    temp_input_address[i]=""
            input_address = ' '.join(str(e) for e in temp_input_address)
        '''
        decimal_find=re.search(r'\d(.)\d',input_address)
        if  not re.search(r'\d(.)\d',input_address):
            input_address=input_address.replace("."," ")
        '''
        input_address=input_address.replace("-"," ")
        input_address=input_address.replace(":"," ")
        input_address=input_address.replace(" no "," ")
        
        try:
            first_street=re.match(r'\W*(\w[^,. !?"]*)', input_address).groups()[0]
        except:
            first_street=""
        if 'street' in first_street or 'street:' in first_street or first_street=='street' or first_street=='street:' or first_street=='office:' or first_street=='address:':
            input_address=input_address.replace(first_street," ")
        
        input_address=re.sub(r'(behind|nearby|near|near by|near to|opposite|beside)[^)]*(building|plaza|market|villa|cottage|mansion|vila|tower|place|complex|center|mall|monjil|manjil|building|headquarter|bhaban|mosque|masjid|mosjid|hospital|university|school|mandir|mondir|police station)', '', input_address)
        #delete flat no. or etc
        temp_input_address=input_address.split()
        if 'flat' in input_address:
            temp_input_address=input_address.split()
            for i,t in enumerate(temp_input_address):
                if i < len(temp_input_address)-1:
                    if t=='flat' and any(char.isdigit() for char in temp_input_address[i+1]):
                        temp_input_address.remove(temp_input_address[i])
                        temp_input_address.remove(temp_input_address[i])
                        break
            input_address = ' '.join(str(e) for e in temp_input_address)

        input_address=re.sub(r'(post code|post|zip code|postal code|postcode|zipcode|postalcode|dhaka)(\s*)(-|:)*(\s*)(\d+)(\s*)','',input_address)

        input_address=re.sub(r'((\s*)(floor|room|flat|level|flr|suite|suit)(\s*(no)*(:)*\s*(-)*\s*)(([0-9]+|\d+)((th|rd|st|nd))))(\s*)|(\s*)((\s*)(([0-9]+|\d+)(th|rd|st|nd))(\s*(:)*\s*(-)*\s*)(floor|flat|level|room|flr|suite|suit))(\s*)|(((\s*)(floor|flat|level|room|flr|suite|suit)(\s*(:)*\s*(-)*\s*)([0-9]*\d*[a-z]*)))(\s*)|(\s*)(((floor|flat|level|room|flr|suite|suit)(no)*(\s*)(([0-9]+|\d+))(th|rd|st|nd)[a-z]+))(\s*)', ' ', input_address)
        input_address=re.sub(r'(\s+[1-9]+|\d+)(th|rd|st|nd)\s+',' ',input_address)
        input_address=input_address.replace(',',' ')
        all_num_list=re.findall(r'\d+', input_address)
        if len(all_num_list)>0:
            max_num_in_string = max(map(int, all_num_list))
            if max_num_in_string>2000:
                max_num_in_string=str(max_num_in_string)
                input_address=input_address.replace(max_num_in_string,'')

        cut_hbrs=re.search(r'(house(\s+)(-|/|:)*(\s*))((h|b|r|s)(\s+))',input_address)
        check_hbrs=0
        if(cut_hbrs):
            check_hbrs=1
            cut_hbrs=cut_hbrs.group(5)
            input_address=re.sub(r'(house(\s+)(-|/|:)*(\s*))((h|b|r|s)(\s+))',r'\1rrrr ',input_address)

        input_address=re.sub('(h|b|r|s)((\s*)(plaza|market|villa|cottage|mansion|vila|tower|place|complex|center|centremall|monjil|manjil|building|headquarter))',r'\1. \2',input_address)
        block_h=re.search('block(\s*)(no)*(:)*(-)*(\s*)(h)',input_address)
        if block_h:
            self.matched[self.blockkey] = 'h'
            input_address = re.sub('block(\s*)(no)*(:)*(-)*(\s*)(h)',' ', input_address)

        block_b=re.search('block(\s*)(no)*(:)*(-)*(\s*)(b)',input_address)
        if block_b:
            self.matched[self.blockkey] = 'b'
            input_address = re.sub('block(\s*)(no)*(:)*(-)*(\s*)(b)',' ', input_address)
        
        block_r=re.search('block(\s*)(no)*(:)*(-)*(\s*)(r)',input_address)
        if block_r:
            self.matched[self.blockkey] = 'r'
            input_address = re.sub('block(\s*)(no)*(:)*(-)*(\s*)(r)',' ', input_address)
        
        block_s=re.search('block(\s*)(no)*(:)*(-)*(\s*)(s)',input_address)
        if block_s:
            self.matched[self.blockkey] = 's'
            input_address = re.sub('block(\s*)(no)*(:)*(-)*(\s*)(s)',' ', input_address)
        input_address = re.sub( r'([a-zA-Z]+)(\d+)', r'\1-\2', input_address ) #insert a '-' between letters and number
        input_address = re.sub( r'(\d+)([a-zA-Z]+)', r'\1-\2', input_address ) #insert a '-' between letters and number
        # pre-processing...........................................................

        #input_address = re.sub( r'h\s+tower','h* tower', input_address)
        expand = self.multiple_replace(self.rep2, input_address.lower())
        expand = self.multiple_replace(self.area_dict, expand.lower())
        #unknown char remove
        expand = re.sub( r'#|"',' ', expand )
        if(check_hbrs==1):
            expand=expand.replace('rrrr',cut_hbrs.strip())

        #spell_checker
        input_address=expand
        input_address = re.sub( r'([a-zA-Z])(\d)', r'\1*\2', input_address )
        x = input_address.split("*")
        input_address = " "
        spell_check=SpellCheck('area-list.txt')
        for i in x:
            i=i.strip()
            if len(i)>5:
                spell_check.check(i)
                i=str(spell_check.correct())
            input_address+=i
        expand=input_address
        self.clone_input_address = input_address
                
        expand=expand.lower()+"  "
        #expand=re.sub(r'((\s*)(floor|flat|level)(\s*(:)*\s*(-)*\s*)([0-9]+((th|rd|st|nd)))) | ((\s*)([0-9]+(th|rd|st|nd))(\s*(:)*\s*(-)*\s*)(floor|flat|level)(\s*))  | ((floor|flat|level)[0-9]+(th|rd|st|nd)*[a-z]+) ', ' ', expand)
        #addresscomponents = word_tokenize(expand)
        addresscomponents = expand.split()

        for i, comp in enumerate(addresscomponents):
                comp=comp.strip()
                if comp == "," or comp == "":
                    continue
               
                temp = comp.lstrip('[0:!@#$-=+.]')
                temp = temp.rstrip('[:!@#$-]=+.')
                temp = temp.strip(" ")
                if(temp != ""):
                    self.tempArray.append(temp)
        self.cleanAddressStr = ' '.join(self.tempArray)
        self.cleanAddressStr = re.sub(r" ?\([^)]+\)", "", self.cleanAddressStr)
        if 'mirpur' in self.cleanAddressStr and 'sector' in self.cleanAddressStr:
            self.cleanAddressStr = self.cleanAddressStr.replace("sector","section")
        if 'uttara' in self.cleanAddressStr and 'section' in self.cleanAddressStr:
            self.cleanAddressStr = self.cleanAddressStr.replace("section","sector")
        #self.tempArray = word_tokenize(self.cleanAddressStr)

                #self.cleanAddressStr="mrpr s2"

        # Parsing..............................
        for i, comp in enumerate(self.tempArray):
                comp=comp.strip()

                if (self.check_sub_area(comp, i)):
                    self.matched_array.append(self.matched[self.subareakey])
                    continue
                if (self.check_area(comp, i)):
                    self.matched_array.append(self.matched[self.areakey])
                    continue
                # if (self.check_super_sub_area(comp, i)):
                #     self.matched_array.append(self.matched[self.ssareakey])
                #     continue
                if (self.check_road(comp, i)):
                    self.matched_array.append(self.matched[self.roadkey])
                    continue
                if  (self.check_block(comp, i)):
                    self.matched_array.append(self.matched[self.blockkey])
                    continue
                if (self.check_holding(comp, i)):
                    self.matched_array.append(self.matched[self.housekey])
                    continue
                if (self.check_holding_name(comp, i)):
                    self.matched_array.append(self.matched[self.buildingkey])
                    continue            
                if (self.check_district(comp, i)) :
                    if (self.matched[self.areakey]==None or self.matched[self.areakey]==''):
                        self.matched_array.append(self.matched[self.districtkey])
                        
                    continue
                if (self.check_sub_district(comp, i)) :
                    if (self.matched[self.areakey]==None or self.matched[self.areakey]==''):
                        self.matched_array.append(self.matched[self.sub_districtkey])
                    continue
                if (self.check_union(comp, i)) :
                    if (self.matched[self.areakey]==None or self.matched[self.areakey]==''):
                        self.matched_array.append(self.matched[self.unionkey])
                    continue
        getsubarea=list(set(self.get_multiple_subarea))
        subarea_min = ''
        subarea_high = ''
        max_H=-1
        min_H=5
        if len(getsubarea)>=2:
            for j, subarea in enumerate(self.subarea_list_pattern):
                
                if max_H<subarea['pattern'].count('H') and subarea['subarea'].strip() not in self.get_multiple_area:
                    max_H=subarea['pattern'].count('H')
                    subarea_high=subarea['subarea']
                if min_H>subarea['pattern'].count('H') and subarea['subarea'].strip() not in self.get_multiple_area:
                    min_H=subarea['pattern'].count('H')
                    subarea_min=subarea['subarea']
                    
            self.matched[self.subareakey]=subarea_high
            for j, subarea in enumerate(self.subarea_list_pattern):
                if  (subarea['subarea'].strip()==subarea_high.strip()) and (((subarea['pattern'][0])=='H' and self.matched[self.housekey]==None) or ((subarea['pattern'][0])=='H' and self.matched[self.housekey]=='') or ((subarea['pattern'][1])=='H' and self.matched[self.roadkey]==None) or ((subarea['pattern'][1])=='H' and self.matched[self.roadkey]=='') or ((subarea['pattern'][2])=='H' and self.matched[self.blockkey]==None) or ((subarea['pattern'][2])=='H' and self.matched[self.blockkey]=='') or ((subarea['pattern'][3])=='H' and self.matched[self.ssareakey]==None) or ((subarea['pattern'][3])=='H' and self.matched[self.ssareakey]=='')):
                    self.matched[self.subareakey]=subarea_min
                    break
        


        
        # if len(getsubarea)>=2:
        #     for subarea in getsubarea:
        #         if subarea not in self.get_multiple_area:
        #             self.matched[self.subareakey]=subarea.lower()
 
        

        getarea=list(set(self.get_multiple_area))
        if len(getarea)>=2:
            chk=0
            for area in getarea:
                subarea_list = dbinit.get_subarea()
                for j, subarea in enumerate(subarea_list):
                    if subarea[0].lower()==area and subarea[1].lower()==self.matched[self.subareakey] and area in self.tempArray:
                        self.matched[self.areakey]=area.lower()
                        chk=1
                        break
                    if subarea[0].lower()==area and subarea[1].lower()==self.matched[self.subareakey] and chk==0:
                        #area=area.rstrip(',')
                        self.matched[self.areakey]=area.lower()
                        break

 


            

        
        # status_checking= self.check_address_status()
        final_address = self.bind_address()     
        #self.search_addr_bkoi(final_address)   

        obj = {
            'status' : self.check_address_status(),
            'address' : final_address,
            'geocoded' : self.search_addr_bkoi2(final_address)
        }
        self.__init__()
        return obj





    def search_addr_bkoi(self, data,qstring):
        print('.....at search..........')
        # print(qstring)
        # url="http://54.254.209.206/api/search/autocomplete/exact"
        # r = requests.post(url, params={'q': qstring})

        # try:
        #     data = r.json()
        #     pass
        # except Exception as e:
        #     return {}
         
        match_counter_max = 0
        match_address_max = ''
        match_obj_max = {}
        for i in data:
            geocoded_area = i['area']
            match_counter = 0
            geo_addr_comp = i['new_address'].split(',')
            i['new_address'] = i['new_address'].strip()
            i['new_address'] = i['new_address'].strip(',')
            if geocoded_area.strip().lower() in qstring or self.matched[self.subareakey] in i['new_address'] or self.matched[self.areakey] in i['new_address']:
                for j, addr_comp in enumerate(geo_addr_comp):
                    if (match.strip() in addr_comp.strip().lower() for match in qstring.split(',')) or addr_comp.strip().lower() in qstring :
                        match_counter = match_counter +1
                if match_counter_max < match_counter:
                    match_counter_max = match_counter
                    match_address_max = i['new_address'].lower()
                    match_obj_max = i
                    
            else :
                for j, addr_comp in enumerate(geo_addr_comp):
                    if addr_comp.strip().lower() in qstring:
                        match_counter = match_counter +1
                if match_counter_max < match_counter:
                    match_counter_max = match_counter
                    match_address_max = i['new_address'].lower()
                    match_obj_max = i

        return match_obj_max

            # result=fuzz.ratio(qstring.lower(), i['Address'].lower())

    def search_addr_bkoi2(self, qstring):
        obj=MiniParser()
        print(self.matched)
        print('.....at search..........')
        #print(qstring)
        url="https://admin.barikoi.xyz/v1/search/autocomplete/web"
        r = requests.post(url, params={'search': qstring})
        try:
            datas = r.json()
            print("got it")
            data=datas['places']
            pass
        except Exception as e:
            print("Failed to get data...................")
            return {}
        
        geocoded_addr_comp=""
        geocoded_holding=None
        geocoded_floor=None
        geocoded_block=""
        geocoded_subarea=""
        geocoded_area=""
        final_addr=""
        maximum=-1
        geocoded_address_with_area=""
        similarity=0
        mp=MiniParser()
        for i in data:
            geocoded_area = i['area']
            geocoded_area=geocoded_area.strip().lower()
            #geocoded_address_with_area=i['address']+", "+geocoded_area
            geocoded_address_with_area=i['new_address']
            geocoded_addr_comp=mp.parse(geocoded_address_with_area)
            #print(geocoded_addr_comp)
            #print(geocoded_area)
            geocoded_holding=geocoded_addr_comp['holding']
            geocoded_house=geocoded_addr_comp['house']
            geocoded_floor=geocoded_addr_comp['floor']
            geocoded_road=geocoded_addr_comp['road']
            geocoded_block=geocoded_addr_comp['block']
            geocoded_subarea=geocoded_addr_comp['subarea']
            print(i['new_address'])
            #print(geocoded_holding)
            #print("matching.................")
            #print(geocoded_subarea)
            #print(self.matched[self.subareakey].strip().strip(',').strip())

            if (geocoded_area==self.matched[self.areakey].strip().strip(',').strip() or geocoded_area==self.matched[self.subareakey].strip().strip(',').strip()  or geocoded_subarea==self.matched[self.areakey].strip().strip(',').strip()  ) and (geocoded_subarea.lower().strip()== self.matched[self.subareakey].strip().strip(',').strip() ) :
                #print(geocoded_addr_comp)
                if self.matched[self.blockkey]!="":
                    if self.matched[self.blockkey].strip().strip(',').strip() ==geocoded_block:
                        if self.matched[self.roadkey].strip().strip(',').strip() ==geocoded_road:
                            similarity=fuzz.ratio(self.matched[self.housekey].strip().strip(',').strip() ,geocoded_house)
                            if similarity>maximum:
                                final_addr=i
                                maximum=similarity
                        elif self.matched[self.roadkey].strip().strip(',').strip() in geocoded_road or geocoded_road in self.matched[self.roadkey].strip().strip(',').strip() and geocoded_road!="":
                            similarity=fuzz.ratio(self.matched[self.housekey].strip().strip(',').strip() ,geocoded_house)
                            if similarity>maximum:
                                final_addr=i
                                maximum=similarity
                        elif fuzz.ratio(self.matched[self.roadkey].strip().strip(',').strip() ,geocoded_road)>90 and geocoded_road!="":
                            similarity=fuzz.ratio(self.matched[self.housekey].strip().strip(',').strip() ,geocoded_house)
                            if similarity>maximum:
                                final_addr=i
                                maximum=similarity
                if self.matched[self.blockkey]=="":
                    #print("paisere.........................................")
                    #print(geocoded_road)
                    if self.matched[self.roadkey].strip().strip(',').strip() == geocoded_road:
                        similarity=fuzz.ratio(self.matched[self.housekey].strip().strip(',').strip() ,geocoded_house)
                        if similarity>maximum:
                            final_addr=i
                            maximum=similarity
                            print("797...............")
                    elif self.matched[self.roadkey].strip().strip(',').strip() in geocoded_road or geocoded_road in self.matched[self.roadkey].strip().strip(',').strip() and geocoded_road!="":
                        similarity=fuzz.ratio(self.matched[self.housekey].strip().strip(',').strip() ,geocoded_house)
                        if similarity>maximum:
                            final_addr=i
                            maximum=similarity
                            print("803...............")
                            print(geocoded_road)
                            print(self.matched[self.roadkey].strip().strip(',').strip())

                    elif fuzz.ratio(self.matched[self.roadkey].strip().strip(',').strip() ,geocoded_road)>90 and geocoded_road!="":
                        similarity=fuzz.ratio(self.matched[self.housekey].strip().strip(',').strip() ,geocoded_house)
                        if similarity>maximum:
                            final_addr=i
                            maximum=similarity
                            print("812...............")
                print("for data : "+i['new_address'])
                print(similarity)
        if final_addr=="":
            print("from prev 1")
            final_addr=self.search_addr_bkoi(data,qstring)

        return final_addr



    def bind_address(self):

        try:
            self.matched[self.buildingkey] = self.matched[self.buildingkey]+", "
        except Exception as e:
            self.matched[self.buildingkey] = '' 
        try:
            self.matched[self.housekey]=self.matched[self.housekey].strip('-')
            if any(char.isdigit() for char in self.matched[self.housekey]):
                self.matched[self.housekey] = "house "+self.matched[self.housekey]+", "
            else:
                self.matched[self.housekey] = ''
        except Exception as e:
            self.matched[self.housekey] = '' 

        try:
            self.matched[self.roadkey] = self.matched[self.roadkey]+", "
        except Exception as e:
            self.matched[self.roadkey] = ''
        try:
            self.matched[self.blockkey] = "block "+self.matched[self.blockkey]+", "
        except Exception as e:
            self.matched[self.blockkey] = ''

        # try:
        #     self.matched[self.ssareakey] = self.matched[self.ssareakey]+", "
        # except Exception as e:
        #     self.matched[self.ssareakey] = ''

        try:
            self.matched[self.subareakey] = self.matched[self.subareakey]+", "
        except Exception as e:
            self.matched[self.subareakey] = ''

        try:
            self.matched[self.areakey] = self.matched[self.areakey]+", "
        except Exception as e:
            self.matched[self.areakey] = ''

        try:
            if (self.matched[self.areakey]==None or self.matched[self.areakey]==''):
                self.matched[self.unionkey] = self.matched[self.unionkey]+", "
            else:
                self.matched[self.unionkey] = ''
        except Exception as e:
            self.matched[self.unionkey] = ''

        try:
            if (self.matched[self.areakey]==None or self.matched[self.areakey]==''):
                self.matched[self.sub_districtkey] = self.matched[self.sub_districtkey]+", "
            else:
                self.matched[self.sub_districtkey]= ''
        except Exception as e:
            self.matched[self.sub_districtkey] = ''

        try:
            if (self.matched[self.areakey]==None or self.matched[self.areakey]==''):
                self.matched[self.districtkey] = self.matched[self.districtkey]+","
            else:
                self.matched[self.districtkey]= ''
        except Exception as e:
            self.matched[self.districtkey] = ''
        print(self.matched)
        print('887-------------------------------------'+ self.matched[self.buildingkey].strip().replace(',','').strip()+'-----------'+self.matched[self.roadkey].strip(','))
        # if self.matched[self.roadkey].strip().replace('road','').replace(',','').strip() in self.matched[self.buildingkey] and self.matched[self.buildingkey]!= '' and self.matched[self.roadkey]!='':
        #     self.matched[self.buildingkey]=self.matched[self.buildingkey].replace(self.matched[self.roadkey].strip().replace('road','').replace(',','').strip(),'')
        if self.matched[self.buildingkey].strip().replace(',','').strip() in self.matched[self.roadkey].strip(',').strip() and self.matched[self.buildingkey]!= '' and self.matched[self.roadkey]!='' :
            self.matched[self.buildingkey]=''
        #     print("893-------------------------")
        # self.matched[self.buildingkey]=self.matched[self.buildingkey].strip()
        if self.matched[self.subareakey]==self.matched[self.areakey]:
            full_address = self.matched[self.buildingkey] + self.matched[self.housekey] + self.matched[self.roadkey] + self.matched[self.blockkey] + self.matched[self.areakey] + self.matched[self.unionkey] + self.matched[self.sub_districtkey] + self.matched[self.districtkey]
        else:
            full_address = self.matched[self.buildingkey] + self.matched[self.housekey] + self.matched[self.roadkey] + self.matched[self.blockkey] + self.matched[self.subareakey] + self.matched[self.areakey] + self.matched[self.unionkey] + self.matched[self.sub_districtkey] + self.matched[self.districtkey]

        full_address = full_address.lstrip(' ,')
        full_address = full_address.rstrip(' ,')
        if len(self.matched_array)<1:
            full_address = self.clone_input_address.lstrip().rstrip()
        
        return full_address


#Flask App.................................

