from flask_cors import CORS
import requests
from json import dumps
from flask import Flask, request, send_from_directory, make_response
from flask_restful import reqparse, abort, Api, Resource
from fuzzywuzzy import fuzz
import urllib
import re
import csv
import enchant



from dbconf.initdb import DBINIT
dbinit = DBINIT()
dbinit.load_area()
dbinit.load_subarea()
dbinit.load_dsu()

from miniparser import MiniParser
from spellcheck import SpellCheck
class AddressParser(object):
       
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
        self.subarea_pattern='subarea_pattern'
        # flags.......................
        self.area_flag = False
        self.area_pos = 0
        self.subarea_flag = False
        self.reverse_house_pattern=False
        self.reverse_road_pattern=False
        self.reverse_goli_pattern=False
        self.reverse_lane_pattern=False
        self.reverse_block_pattern=False
        self.reverse_section_pattern=False
        self.reverse_sector_pattern=False
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
        self.matched[self.subarea_pattern]=[]
        self.tempArray = []
        self.usedToken= []
        self.matched_array = []
        self.area_pattern = None
        self.get_multiple_subarea=[]
        self.get_multiple_area=[]
        self.subarea_list_pattern=[]
        self.GeoTrueFor={}    
    reverse_pattern= {
    'house':'',
    'road':'',
    'goli':'',
    'lane':'',
    'block':'',
    'ssarea':'',
    'subarea':'',

    }


    prefix_dict = ['', 'east', 'west', 'north', 'south', 'middle', 'purba', 'poschim', 'uttar', 'dakshin', 'moddho', 'dokkhin', 'dakkhin']

    address_component = ['','sarani','sarak','rasta','goli','lane','code','street','floor','level', 'house', 'plot', 'road', 'block', 'section', 'sector', 'avenue']
    
    building_name_key = ['building','plaza' , 'market', 'bazar' , 'villa' , 'nibash', 'cottage' , 'mansion', 'mension', 'vila' , 'tower' , 'place' , 'complex' , 'center' , 'centre' , 'mall' , 'square', 'monjil' , 'manjil' , 'palace' , 'headquarter' , 'bhaban', 'mosque', 'masjid', 'mosjid','hospital','university','school','mandir','mondir','police station', 'club', 'garage', 'office', 'restaurent', 'cafe', 'hotel', 'garments', 'park', 'field', 'garden', 'studio', 'stadium', 'meusium', 'institute', 'store', 'college', 'varsity', 'coaching', 'library', 'tution', 'bank', 'atm', 'agent', 'Ministry', 'workshop', 'saloon', 'tailors', 'pharmacy', 'textile', 'laundry', 'hall', 'enterprise', 'shop', 'court', 'parliament', 'showroom', 'warehouse', 'electronics', 'optics', 'dokan', 'bitan', 'senitary', 'square', 'sports', 'motors', 'automobile', 'builders', 'service', 'developers', 'firm', 'limited', 'private', 'tech', 'company', 'incorporation', 'hardware', 'soft', 'software', 'solutions', 'bistro', 'printings', 'ghor', 'farm', 'fashions', 'style', 'pharma', 'medicine', 'church', 'girja', 'medical', 'clinic', 'somity', 'association', 'foundation', 'madrasa', 'kithcen', 'restora', 'stand', 'terminal', 'stop', 'care', 'dresser', 'tank', 'pump', 'corner', 'stationoery', 'kutir']
    tempList=['ka','kha','ga','gha','uma','ca','cha','ja','jha','za','zha','ta','tha','da','dha','na','pa','pha','fa','ma','ra','la','ha','ya', 'gp']
    rep2 = {
        #' east':' east ', ' west':' west ', ' north':' north ', ' south':' south ', ' middle':' middle ', ' purba':' purba ', ' poschim':' poschim ', ' uttar':' uttar ', ' dakshin':' dakshin ', ' moddho':' moddho ', ' dokkhin':' dokkhin ', ' dakkhin':' dakkhin ',
        "rd#": " road ", "rd-": " road  ", " rd": " road  "," road#": " road  ", "rd:": " road  ", "r:": " road ", "r#": " road ","road #": " road "," r-": " road ", " ,r-": " road ",",r":" road "," r ":" road ", "h#": " house ", "h-": " house ", "h:": " house ", " h ": " house ",
        "bl-":" block "," blk ":" block ", " blk: ":" block ", " blk- ":" block ", " blk# ":" block ", " blk":" block ", "bl ":" block ", " b ":" block ", "bl#":" block ", "bl:":" block ", "b-":" block ","b:":" block ", "b#":" block ", 'sec-': ' sector ', 'sec.': ' sector ', ' sec ':' sector ', 'sec#': ' sector ', 'sec:': ' sector ', 's-': ' sector ', ' s-': ' sector ', 's#': ' sector ', 's:': ' sector ', ' s ': ' sector ',
        'house': ' house ', 'house:': ' house ',' basha ':' house ',' basa ':' house ',' bari ':' house ', 'road:': ' road ', 'block': ' block ', 'block-': ' block ', 'block:': ' block ', 'block#': ' block ', 'section': ' section ','section:': ' section ', 'sector': ' sector ','sector:': ' sector ',
        'house no': ' house ', 'house no ': ' house ', 'houseno:': ' house ', 'road no': ' road ', ' no ':'', 'road no.': ' road ', 'block no': ' block ', 'blockno': ' block ', 'section no': ' section ','sectionno': ' section ', 'sector no': ' sector ','sector': ' sector ','number':'', 'no :': '', 'no:': '', 'no -': '', 'no-': '', 'no =': '','no#': '', 'no=': '', 'no.': '',
        'ave-': ' avenue ', 'ave:': ' avenue ', 'ave#': ' avenue ','ave:': ' avenue ', 'avenue:': ' avenue ', 'avenue-': ' avenue ', 'avenue#': ' avenue ', ' ln': ' lane ',' ln#': ' lane ', ' ln:': ' lane', ' ln-': ' lane', ' len ': ' lane ', 'plot':' ', ' ltd.':' limited', ' pvt.':' private', ' inc.':' incorporation', ' co.':' company',
    } 
    rep1 = {
        #' east':' east ', ' west':' west ', ' north':' north ', ' south':' south ', ' middle':' middle ', ' purba':' purba ', ' poschim':' poschim ', ' uttar':' uttar ', ' dakshin':' dakshin ', ' moddho':' moddho ', ' dokkhin':' dokkhin ', ' dakkhin':' dakkhin ',
        "rd#": " road ", "rd-": " road  ", " rd": " road  "," road#": " road  ", "rd:": " road  ",
        "bl-":" block "," blk ":" block ", " blk: ":" block ", " blk- ":" block ", " blk# ":" block ", " blk":" block ", "bl ":" block ", "bl#":" block ", "bl:":" block ",  'sec-': ' sector ', ' sec ':' sector ', 'sec#': ' sector ','sec.': ' sector ', 'sec:': ' sector ',
        'house': ' house ', 'house:': ' house ',' basha ':' house ',' basa ':' house ',' bari ':' house ', 'road:': ' road ', 'block': ' block ', 'block-': ' block ', 'block:': ' block ', 'block#': ' block ', 'section': ' section ','section:': ' section ', 'sector': ' sector ','sector:': ' sector ',
        'house no': ' house ', 'house no ': ' house ', 'houseno:': ' house ', 'road no': ' road ', 'road no.': ' road ', 'block no': ' block ', 'blockno': ' block ', 'section no': ' section ','sectionno': ' section ', 'sector no': ' sector ','sector': ' sector ',
        'ave-': ' avenue ', 'ave:': ' avenue ', 'ave#': ' avenue ','ave:': ' avenue ', 'avenue:': ' avenue ', 'avenue-': ' avenue ', 'avenue#': ' avenue ', ' ln': ' lane ',' ln#': ' lane ', ' ln:': ' lane', ' ln-': ' lane',  'plot':' ', ' ltd.':' limited', ' pvt.':' private', ' inc.':' incorporation', ' co.':' company',
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
                    if (token.lower().strip()=='section' or token.lower().strip()=='sector') and len(self.tempArray)-1>idx:
                        if token.lower().strip()+" "+self.tempArray[idx+1]==subarea[1].lower():
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
                    else:
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
        if (any(char.isdigit() for char in token) or token in tempList or re.match(r'^[a-z]$',token)) and idx < len(self.tempArray)-1 and (self.matched[self.housekey]==None or self.matched[self.housekey]==''):
            if idx == 0 and self.tempArray[idx+1].lower()!='floor':
                self.matched[self.housekey] = token
                print('holding token 267')
                print(token)
                if ((any(char.isdigit() for char in self.tempArray[idx+1])) or re.match(r'^[a-z]$', self.tempArray[idx+1]) or (self.tempArray[idx+1] in tempList)) and idx < len(self.tempArray)-2 :
                    self.matched[self.housekey] = self.matched[self.housekey]+"-"+self.tempArray[idx+1] 
                    if idx < len(self.tempArray)-3:
                        if ((any(char.isdigit() for char in self.tempArray[idx+2])) or re.match(r'^[a-z]$', self.tempArray[idx+2]) or (self.tempArray[idx+2] in tempList)) :
                            self.matched[self.housekey] = self.matched[self.housekey]+"-"+self.tempArray[idx+2]
                return True


            if self.tempArray[idx-1].lower() not in self.address_component :
                check_match=0
                print('279------------')
                print(token)
                area_list = dbinit.get_subarea()
                for j, area in enumerate(area_list):
                    if area[0].lower()==self.tempArray[idx-1].lower():
                        check_match=1
                        break
                if self.matched[self.housekey]==None:
                    self.matched[self.housekey]=""
                if check_match==0 and token not in self.matched[self.housekey]:
                    self.matched[self.housekey]=token
                    print('290----------- '+self.matched[self.housekey])
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
        tempList=['ka','kha','ga','gha','uma','ca','cha','ja','jha','za','zha','ta','tha','da','dha','na','pa','pha','fa','ma','ra','la','ha','ya', 'gp','rrrr']
        if any( char in token for char in self.building_name_key) and self.matched[self.buildingkey]==None:
            if idx != len(self.tempArray) and idx != 0 :
                i=idx-1
                building_str = ''
                self.matched[self.buildingkey]=building_str
                while i>=0:
                    if any(char.isdigit() for char in self.tempArray[i]):
                        break
                    if not i==0 and (self.tempArray[i-1] in self.address_component or self.tempArray[i-1] in tempList):
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
        p=0
        if (token.lower() == 'block' and idx < len(self.tempArray)-1):
            p=re.match(r'^(?=.*[0-9])(?=.*[a-zA-Z])([a-zA-Z0-9]+)$', self.tempArray[idx+1])
            p1=re.match(r'[0-9]+', self.tempArray[idx+1])
            p2=re.match(r'^[a-z]$', self.tempArray[idx+1])
            p3=re.match(r'^[A-Z]$', self.tempArray[idx+1])
            p_slash=re.match(r'(^[a-z])/[0-9]+$',self.tempArray[idx+1])
            p_hi=re.match(r'(^[a-z])-[0-9]+$',self.tempArray[idx+1])
            if p or p1 or p2 or p3 or p_slash or p_hi or (self.tempArray[idx+1] in tempList):
                self.matched[self.blockkey] = self.tempArray[idx+1]
                p=1
                return True
            else:
                p=0

        if (token.lower() == 'block' and idx <= len(self.tempArray) and p==0):
            p=re.match(r'^(?=.*[0-9])(?=.*[a-zA-Z])([a-zA-Z0-9]+)$', self.tempArray[idx-1])
            p1=re.match(r'[0-9]+', self.tempArray[idx-1])
            p2=re.match(r'^[a-z]$', self.tempArray[idx-1])
            p3=re.match(r'^[A-Z]$', self.tempArray[idx-1])
            p_slash=re.match(r'(^[a-z])/[0-9]+$',self.tempArray[idx-1])
            p_hi=re.match(r'(^[a-z])-[0-9]+$',self.tempArray[idx-1])
            if p or p1 or p2 or p3 or p_slash or p_hi or (self.tempArray[idx-1] in tempList) or(self.tempArray[idx-1] not in self.matched_array):
                self.matched[self.blockkey] = self.tempArray[idx-1]
            return True



    def check_road(self, road, idx):
       
        tempList=['ka','kha','ga','gha','uma','ca','cha','ja','jha','za','zha','ta','tha','da','dha','na','pa','pha','fa','ma','ra','la','ha','ya', 'gp']
        if 'road' == road or 'avenue'==road or 'ave' == road or 'lane' == road or 'sarani' == road or 'soroni' == road or 'rd#' == road or 'sarak' == road or 'sharak' == road or 'shorok' == road or 'sharani' == road or 'highway' == road or 'path' == road or 'poth' == road or 'chowrasta' == road or 'sarak' == road or 'rasta' == road or 'sorok' == road or 'goli' == road or 'street' == road or 'line' == road :
            if 'ave' == road:
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
                        if not i==0 and (self.tempArray[i-1] in self.address_component or self.tempArray[i-1] in self.building_name_key or self.tempArray[i-1] in tempList or ( re.match(r'^[a-z]$', self.tempArray[i-1]) and self.tempArray[i-2]=='block' )  ):
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



    def rupantor_parse_address(self, input_address):
        input_address = " "+input_address
        input_address = input_address.lower()
        
        if input_address.strip().lstrip(',').rstrip(',') == '' :
            return  {
                'status' : 'Not An Address',
                'address' : input_address,
                'geocoded' :{},
            }
            
        input_address = re.sub(r',',' ', input_address)
        input_address = re.sub( r'#|"',' ', input_address )
        input_address=input_address.lower()+"  "
        input_address="  "+input_address.lower()
        input_address=re.sub(r'\([^)]*\)', '', input_address)
        input_address = re.sub( r'(\d+)(no\s+)', r'\1 \2', input_address )
        input_address = re.sub( r'(\s+no)(\d+)', r'\1 \2', input_address )
        input_address = "  "+input_address
        input_address = self.multiple_replace(self.rep1, input_address.lower())
        ###Check Reverse pattern like 3 no house
        self.Check_Reverse_Key(input_address)
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
        input_address=input_address.replace(";"," ")
        input_address=input_address.replace("-"," ")
        input_address=input_address.replace("–"," ")
        input_address=input_address.replace(":"," ")
        input_address=input_address.replace(" no "," ")
        print("508-----------------"+input_address)
        try:
            first_street=re.match(r'\W*(\w[^,. !?"]*)', input_address).groups()[0]
        except:
            first_street=""
        if 'street' in first_street or 'street:' in first_street or first_street=='street' or first_street=='street:' or first_street=='office:' or first_street=='address:' or first_street=='address':
            input_address=input_address.replace(first_street," ")
        
        input_address=re.sub(r'(behind|nearby|near|near by|near to|opposite|opposite of|beside)[^)]*(building|plaza|market|villa|cottage|mansion|vila|tower|place|complex|center|mall|monjil|manjil|building|headquarter|bhaban|mosque|masjid|mosjid|hospital|university|school|mandir|mondir|police station|park)', '', input_address)
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

        input_address=re.sub(r'(post code|post|zip code|postal code|postcode|zipcode|postalcode|dhaka)(\s*)(-|:)*(\s*)(\d{4})(\s*)','',input_address)

        input_address=re.sub(r'((\s+)(apt|apartment|floor|room|flat|level|flr|suite|suit)(\s+(no)*[.]*(:)*\s*(-)*\s*)(([0-9]+|\d+)((th|rd|st|nd))))(\s*)|(\s*)((\s*)(([0-9]+|\d+)(th|rd|st|nd))(\s*(:)*\s*(-)*\s+)(apt|apartment|floor|flat|level|room|flr|suite|suit))(\s*)|(((\s+)(apt|apartment|floor|flat|level|room|flr|suite|suit)(\s*(:)*\s*(-)*\s*)([0-9]*\d*[a-z]*)))(\s*)|(\s+)(((apt|apartment|floor|flat|level|room|flr|suite|suit)(no)*(\s*)(([0-9]+|\d+))(th|rd|st|nd)[a-z]+))(\s*)', '  ', input_address)
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
        block_h=re.search('block(\s*)(no)*(:)*(-)*(\s*)(h )',input_address)
        if block_h:
            self.matched[self.blockkey] = 'h'
            input_address = re.sub('block(\s*)(no)*(:)*(-)*(\s*)(h )',' ', input_address)

        block_b=re.search('block(\s*)(no)*(:)*(-)*(\s*)(b )',input_address)
        if block_b:
            self.matched[self.blockkey] = 'b'
            input_address = re.sub('block(\s*)(no)*(:)*(-)*(\s*)(b )',' ', input_address)
        
        block_r=re.search('block(\s*)(no)*(:)*(-)*(\s*)(r )',input_address)
        if block_r:
            self.matched[self.blockkey] = 'r'
            input_address = re.sub('block(\s*)(no)*(:)*(-)*(\s*)(r )',' ', input_address)
        
        block_s=re.search('block(\s*)(no)*(:)*(-)*(\s*)(s )',input_address)
        if block_s:
            self.matched[self.blockkey] = 's'
            input_address = re.sub('block(\s*)(no)*(:)*(-)*(\s*)(s )',' ', input_address)

        b_block=re.search('\s+b(\s*)(:)*(-)*(\s*)block',input_address)
        if b_block:
            self.matched[self.blockkey] = 'b'
            input_address = re.sub('\s+b(\s*)(:)*(-)*(\s*)block',' ', input_address)

        h_block=re.search('\s+b(\s*)(:)*(-)*(\s*)block',input_address)
        if h_block:
            self.matched[self.blockkey] = 'h'
            input_address = re.sub('\s+h(\s*)(:)*(-)*(\s*)block',' ', input_address)
        input_address = re.sub( r'([a-zA-Z]+)(\d+)', r'\1-\2', input_address ) #insert a '-' between letters and number
        input_address = re.sub( r'(\d+)([a-zA-Z]+)', r'\1-\2', input_address ) #insert a '-' between letters and number
        # pre-processing...........................................................

        #input_address = re.sub( r'h\s+tower','h* tower', input_address)
        print('////////////////////')
        #print("574-----------------"+input_address)
        print(input_address)
        if (re.search('.com|.xyz|.net|.co|.inc|.org|.bd.com|.edu|\d+\.\d+', input_address) == None):
            input_address = input_address.replace(".","  ")
            print(input_address)
            print('##############################')
        input_address = "  "+input_address
        expand = self.multiple_replace(self.rep2, input_address.lower())
        expand = self.multiple_replace(self.area_dict, expand.lower())
        #print("579-----------------"+input_address)
        #unknown char remove
        expand = re.sub( r'#|"',' ', expand )
        if(check_hbrs==1):
            expand=expand.replace('rrrr',cut_hbrs.strip())
        input_address=expand


        input_address = re.sub( r'([a-zA-Z])(\d)', r'\1*\2', input_address )
        print('INPUT ADDRESS............')
        print(input_address)
        print(input_address)
        x = input_address.split("*")
        input_address = " "
        #spell_checker
        # print('before spellcheck '+expand)
        spell_check=SpellCheck('area-list.txt')
        for i in x:
            i=i.strip()
            if len(i)>5:
                spell_check.check(i)
                i=str(spell_check.correct())
            input_address+=i
        expand=input_address
        # print('after spellcheck '+expand)
        self.clone_input_address = input_address
                
        expand=expand.lower()+"  "
        #expand=re.sub(r'((\s*)(floor|flat|level)(\s*(:)*\s*(-)*\s*)([0-9]+((th|rd|st|nd)))) | ((\s*)([0-9]+(th|rd|st|nd))(\s*(:)*\s*(-)*\s*)(floor|flat|level)(\s*))  | ((floor|flat|level)[0-9]+(th|rd|st|nd)*[a-z]+) ', ' ', expand)
        #addresscomponents = word_tokenize(expand)
        addresscomponents = expand.split()
        # print(addresscomponents)
        temp_str_address = ''
        for i, comp in enumerate(addresscomponents):
            # print(comp)
            # print(enchant.Dict("en_US").check(comp))

            if 'road' in comp and enchant.Dict("en_US").check(comp) == False and comp != 'road':
                comp = comp.replace('road', ' road')
            temp_str_address += " "+comp

        # print('....................................................')
        # print(temp_str_address)
        addresscomponents = temp_str_address.split()

        for i, comp in enumerate(addresscomponents):
                comp=comp.strip()
                if comp == "," or comp == "":
                    continue
               
                temp = comp.lstrip('[0:|!@#$-=+.]')
                temp = temp.rstrip('[:|!@#$-]=+.')
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
            # print(comp)

            if (self.check_sub_area(comp, i)):
                # print('in check sub area')
                # print(comp)
                self.matched_array.append(self.matched[self.subareakey])
                continue
            if (self.check_area(comp, i)):
                self.matched_array.append(self.matched[self.areakey])
                continue
            # if (self.check_super_sub_area(comp, i)):
            #     self.matched_array.append(self.matched[self.ssareakey])
            #     continue
            if (self.check_road(comp, i)):
                # print('in check road')
                # print(comp)
                self.matched_array.append(self.matched[self.roadkey])
                continue
            if  (self.check_block(comp, i)):
                # print('in check block')
                # print(comp)
                self.matched_array.append(self.matched[self.blockkey])
                continue
            if (self.check_holding(comp, i)):
                # print('in check holding')
                # print(comp)
                self.matched_array.append(self.matched[self.housekey])
                continue
            if (self.check_holding_name(comp, i)):
                # print('in check holding name'+ comp)
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

            # print(self.matched)

        # if self.matched[self.roadkey]!='' or self.matched[self.roadkey]!=None:
        #     self.matched[self.roadkey]=self.matched[self.roadkey].replace('-','/')
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
 
        # subarea_list = dbinit.get_subarea()

        getarea=list(set(self.get_multiple_area))
        if len(getarea)>=2:
            chk=0
            for area in getarea:
                subarea_list = dbinit.get_subarea()
                try:
                    if self.matched[self.subareakey] in self.matched[self.roadkey]:
                        self.matched[self.subareakey] = ""
                except Exception as e:
                    print('Subarea key marked safe from road name')

                try:
                    if self.matched[self.subareakey]in self.matched[self.buildingkey]:
                        self.matched[self.subareakey] = ""
                except Exception as e:
                    print('Subarea key marked safe from building name')
                for j, subarea in enumerate(subarea_list):
                    if subarea[0].lower()==area and subarea[1].lower()==self.matched[self.subareakey] and area in self.tempArray:
                        self.matched[self.areakey]=area.lower()
                        chk=1
                        break
                    if subarea[0].lower()==area and subarea[1].lower()==self.matched[self.subareakey] and chk==0:
                        #area=area.rstrip(',')
                        self.matched[self.areakey]=area.lower()
                        break

 
        # if self.reverse_pattern['road']!=self.matched[self.roadkey]:
        #     self.matched[self.roadkey]=self.reverse_pattern['road']
        if self.reverse_house_pattern==True and self.reverse_pattern['house']!=self.matched[self.housekey]:
            self.matched[self.housekey]=self.reverse_pattern['house']
        if self.reverse_road_pattern==True and self.reverse_pattern['road']!=self.matched[self.roadkey]:
            self.matched[self.roadkey]=self.reverse_pattern['road']
        if self.reverse_goli_pattern==True and self.reverse_pattern['goli']!=self.matched[self.roadkey]:
            self.matched[self.roadkey]=self.reverse_pattern['goli']
        if self.reverse_lane_pattern==True and self.reverse_pattern['lane']!=self.matched[self.roadkey]:
            self.matched[self.roadkey]=self.reverse_pattern['lane']
        if self.reverse_block_pattern==True and self.reverse_pattern['block']!=self.matched[self.blockkey]:
            self.matched[self.blockkey]=self.reverse_pattern['block']
        if self.reverse_sector_pattern==True and self.reverse_pattern['sector']!=self.matched[self.subareakey]:
            if self.matched[self.areakey]=='mirpur':
                self.reverse_pattern['sector']=self.reverse_pattern['sector'].replace('sector','section')
                self.matched[self.subareakey]=self.reverse_pattern['sector']
            elif self.matched[self.areakey]=='uttara':
                self.matched[self.subareakey]=self.reverse_pattern['sector']

        print('------------------------------------------=====================================')
        #print(self.subarea_list_pattern)
        #print(self.get_multiple_area)
        #print(self.get_multiple_subarea)
        s_pattern=[]
        if len(self.subarea_list_pattern)>0:
            for patterns in self.subarea_list_pattern:
                if patterns['subarea']==self.matched[self.subareakey]:
                    s_pattern=patterns['pattern']
                    self.matched[self.subarea_pattern]=s_pattern
                    break

        
        # status_checking= self.check_address_status()
        final_address = self.bind_address()     
        #self.search_addr_bkoi(final_address)  
        obj = {

            'status' : self.check_address_status(),
            'address' : final_address,
            'area' : self.matched[self.areakey],
            'parsed_house':self.matched[self.housekey],
            'parsed_building_name':self.matched[self.buildingkey],
            'parsed_road':self.matched[self.roadkey],
            'parsed_block':self.matched[self.blockkey],
            'parsed_super_subarea':self.matched[self.ssareakey],
            'parsed_subarea':self.matched[self.subareakey],
            'parsed_area':self.matched[self.areakey],
            'parsed_district':self.matched[self.districtkey],
            'parsed_sub_district':self.matched[self.sub_districtkey],
            'parsed_union':self.matched[self.unionkey],
        }
        self.__init__()

        return obj

    def Check_Confidence_Score(self):
        p=1
        score=0
        print(self.matched[self.subarea_pattern])
        print(self.GeoTrueFor)
        if len(self.matched[self.subarea_pattern])>0 and len(self.GeoTrueFor)>0:
            print(self.matched[self.subarea_pattern][4])
            print(self.GeoTrueFor['subareakey'])
            if self.matched[self.subarea_pattern][4]=='H' and self.GeoTrueFor['subareakey']==1:
                score+=50
                if self.matched[self.subarea_pattern][2]=='H' and self.GeoTrueFor['blockkey']==1:
                    score+=30
                    if self.matched[self.subarea_pattern][1]=='H' and self.GeoTrueFor['roadkey']==1:
                        score+=10
                    if self.matched[self.subarea_pattern][1]=='H' and self.GeoTrueFor['roadkey']==2:
                        score+=8
                    if self.matched[self.subarea_pattern][1]=='H' and self.GeoTrueFor['roadkey']==3:
                        score+=4
                    if self.matched[self.subarea_pattern][1]!='H' :
                        score+=10
                        self.GeoTrueFor['roadkey']=1
                    if self.matched[self.subarea_pattern][1]=='H' and self.GeoTrueFor['roadkey']==0:
                        self.GeoTrueFor['roadkey']=5
                    if self.matched[self.housekey]!="":
                        score+=10-(self.GeoTrueFor['roadkey']*2)
                elif self.matched[self.subarea_pattern][2]=='H' and self.GeoTrueFor['blockkey']==0:
                    score+=0
                    if self.matched[self.subarea_pattern][1]=='H' and self.GeoTrueFor['roadkey']==1:
                        score+=10//2
                    if self.matched[self.subarea_pattern][1]=='H' and self.GeoTrueFor['roadkey']==2:
                        score+=8//2
                    if self.matched[self.subarea_pattern][1]=='H' and self.GeoTrueFor['roadkey']==3:
                        score+=4//2
                    if self.matched[self.subarea_pattern][1]!='H' :
                        score+=10//2
                    if self.matched[self.subarea_pattern][1]=='H' and self.GeoTrueFor['roadkey']==0:
                        self.GeoTrueFor['roadkey']=5
                    if self.matched[self.housekey]!="":
                        score+=10-(self.GeoTrueFor['roadkey']*2)
                    else :
                        score+=10-(self.GeoTrueFor['roadkey'])*(self.GeoTrueFor['roadkey'])
                elif self.matched[self.subarea_pattern][2]!='H':
                    score+=30
                    if self.matched[self.subarea_pattern][1]=='H' and self.GeoTrueFor['roadkey']==1:
                        score+=10
                    if self.matched[self.subarea_pattern][1]=='H' and self.GeoTrueFor['roadkey']==2:
                        score+=8
                    if self.matched[self.subarea_pattern][1]=='H' and self.GeoTrueFor['roadkey']==3:
                        score+=4
                    if self.matched[self.subarea_pattern][1]=='H' and self.GeoTrueFor['roadkey']==0:
                        self.GeoTrueFor['roadkey']=5
                    if self.matched[self.subarea_pattern][1]!='H':
                        score+=10
                        self.GeoTrueFor['roadkey']=1
                    if self.matched[self.housekey]!="":
                        score+=10-(self.GeoTrueFor['roadkey']*2)

                else:
                    score=score-(self.matched[self.subarea_pattern].count('H')-1)*(self.matched[self.subarea_pattern].count('H')-1)
        if self.matched[self.areakey]=="" and self.matched[self.areakey]==None:
            score=20
        print(str(score)+"%")
        return None
    def Check_Reverse_Key(self,s):
        house_key=''
        road_key=''
        block_key=''
        sector_key=''
        goli_key=''
        #s='oaishf ka/4    no house las, 4 number   road block no 5'
        pattern_house=re.search('(ka)*[a-z]*\d*/*[a-z]*(ka)*\d+\s+(no|number)\s+house\s+',s)
        pattern_road=re.search('(ka)*[a-z]*\d*/*[a-z]*(ka)*\d+\s+(no|number)\s+road\s+',s)
        pattern_goli=re.search('(ka)*[a-z]*\d*/*[a-z]*(ka)*\d+\s+(no|number)\s+goli\s+',s)
        pattern_lane=re.search('(ka)*[a-z]*\d*/*[a-z]*(ka)*\d+\s+(no|number)\s+lane\s+',s)
        pattern_block=re.search('(ka)*[a-z]*\d*/*[a-z]*(ka)*\d+\s+(no|number)\s+block\s+',s)
        pattern_sector=re.search('(ka)*[a-z]*\d*/*[a-z]*(ka)*\d+\s+(no|number)\s+sector\s+',s)
        if pattern_house:
            house_key=pattern_house.group().split()[0]
            print("house "+house_key)
            self.reverse_house_pattern=True
            self.reverse_pattern['house']=house_key
        if pattern_road:
            road_key=pattern_road.group().split()[0]
            self.reverse_road_pattern=True
            print("road "+road_key)
            self.reverse_pattern['road']="road "+road_key
        if pattern_goli:
            goli_key=pattern_goli.group()
            self.reverse_goli_pattern=True
            print("goli "+goli_key)
            self.reverse_pattern['goli']=goli_key
        if pattern_lane:
            lane_key=pattern_lane.group().split()[0]
            self.reverse_lane_pattern=True
            print("lane "+lane_key)
            self.reverse_pattern['lane']="lane "+lane_key
        if pattern_block:
            block_key=pattern_block.group().split()[0]
            self.reverse_block_pattern=True
            print("block "+block_key)
            self.reverse_pattern['block']=block_key
        if pattern_sector:
            sector_key=pattern_sector.group().split()[0]
            self.reverse_sector_pattern=True
            print("sector "+sector_key)
            self.reverse_pattern['sector']="sector "+sector_key
        return None


    def search_addr_bkoi(self, data,qstring):
        # print('.....at search..........')
        # # print(qstring)
        # url="http://54.254.209.206/api/search/autocomplete/exact"
        # r = requests.post(url, params={'q': qstring})

        # try:
        #     data = r.json()
        #     pass
        # except Exception as e:
        #     return {}
        # print(qstring+"693.......................")
        match_counter_max = -1
        match_address_max = ''
        match_obj_max = {}
        # print(self.matched)
        for i in data:
            geocoded_area = i['area']
            match_counter = 0
            i['new_address']= i['new_address'].lower()
            geo_addr_comp = i['new_address'].split(',')
            i['new_address'] = i['new_address'].strip()
            i['new_address'] = i['new_address'].strip(',')
            if geocoded_area.strip().lower() in qstring or self.matched[self.subareakey] in i['new_address'] or self.matched[self.areakey] in i['new_address']:
                # print("704..................")
                for j, addr_comp in enumerate(geo_addr_comp):
                    # print(addr_comp)
                    if any(match.strip() in addr_comp.strip().lower() for match in qstring.split(',')) or (addr_comp.strip().lower() in qstring and addr_comp.strip().lower()!=''):
                        match_counter = match_counter +1
                        # print(match_counter)
                if match_counter_max < match_counter:
                    match_counter_max = match_counter
                    match_address_max = i['new_address'].lower()
                    match_obj_max = i
                # print(match_counter_max)
                # print(match_address_max)

                    
            else :
                # print("714..................")
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
        # print(self.matched)
        # print('.....at search..........')
        ## print(qstring)
        url="http://elastic.barikoi.com/api/search/autocomplete/exact"
        r = requests.post(url, params={'q': qstring})
        try:
            datas = r.json()
            # print("got it")
            data=datas
            pass
        except Exception as e:
            # print("Failed to get data...................")
            return {}
        
        geocoded_addr_comp=""
        geocoded_holding=None
        geocoded_floor=None
        geocoded_block=""
        geocoded_subarea=""
        geocoded_area=""
        final_addr=""
        maximum=-1
        maximum_exact=-1
        maximum_exact_b=-1
        geocoded_address_with_area=""
        similarity=0
        mp=MiniParser()
        matched_road_flag = 0
        without_road_maximum=0
        exact_addr=''
        gotHoldings=[]
        TrueFor={'housekey':0,'roadkey':0,'blockkey':0,'ssareakey':0,'subareakey':0,}
        matched_house_key = self.matched[self.housekey]
        if any(char.isdigit() for char in self.matched[self.housekey]):
            self.matched[self.housekey] = re.findall('\d+',self.matched[self.housekey])[0]
        print('H O U S E Number..........')
        print(self.matched[self.housekey])
        count=0
        for i in data:
            geocoded_area = i['area']
            geocoded_area=geocoded_area.strip().lower()
            #geocoded_address_with_area=i['address']+", "+geocoded_area
            geocoded_address_with_area=i['new_address']
            geocoded_addr_comp=mp.parse(geocoded_address_with_area.lower())
            ## print(geocoded_addr_comp)
            ## print(geocoded_area)
            geocoded_holding=geocoded_addr_comp['holding'].strip()
            geocoded_house=geocoded_addr_comp['house'].strip()
            geocoded_floor=geocoded_addr_comp['floor'].strip()
            geocoded_road=geocoded_addr_comp['road'].strip()
            geocoded_block=geocoded_addr_comp['block'].strip()
            geocoded_subarea=geocoded_addr_comp['subarea'].strip()
            #print(geocoded_addr_comp['multiple_subarea'])
            if len(geocoded_addr_comp['multiple_subarea'])>=2:
                for sarea in geocoded_addr_comp['multiple_subarea']:
                    #print(sarea)
                    if sarea.strip()!=geocoded_area.strip() and sarea in geocoded_address_with_area.lower():
                        geocoded_subarea=sarea.strip()
            print('=============================================================================')
            print(geocoded_address_with_area)
            print(geocoded_area+'    '+self.matched[self.areakey].strip().strip(',').strip())
            print(geocoded_subarea+'    '+self.matched[self.subareakey].strip().strip(',').strip())
            holding=''
            holding=geocoded_house
            if any(char.isdigit() for char in geocoded_house):
                geocoded_house = re.findall('\d+',geocoded_house)[0]
            if (geocoded_area.strip()==self.matched[self.areakey].strip().strip(',').strip() or geocoded_area.strip()==self.matched[self.subareakey].strip().strip(',').strip()  or geocoded_subarea.strip()==self.matched[self.areakey].strip().strip(',').strip()  ) and (geocoded_subarea.lower().strip()== self.matched[self.subareakey].strip().strip(',').strip() or any(self.matched[self.subareakey].strip().strip(',').strip()== subareas.strip().strip(',').strip() for subareas in  geocoded_addr_comp['multiple_subarea'] )) and self.matched[self.subareakey].strip().strip(',').strip()!='':
                print('when subarea provided................................. '+self.matched[self.subareakey].strip().strip(',').strip()+' vs '+geocoded_subarea)
                if self.matched[self.blockkey]!="":
                    if self.matched[self.blockkey].strip().strip(',').strip() ==geocoded_block:
                        print('when block provided....... '+self.matched[self.blockkey].strip().strip(',').strip()+' vs '+geocoded_block)
                        if self.matched[self.roadkey].strip().strip(',').strip() == geocoded_road and self.matched[self.roadkey].strip().strip(',').strip()!='':
                            print('when road provided.............. '+self.matched[self.roadkey].strip().strip(',').strip()+' vs '+geocoded_road)
                            matched_road_flag=1
                            similarity=fuzz.ratio(self.matched[self.housekey].strip().strip(',').strip() ,geocoded_house)
                            gotHoldings.append(holding)
                            if similarity>maximum_exact_b:
                                final_addr=i
                                exact_addr = i
                                maximum_exact_b=similarity
                                TrueFor['subareakey']=1
                                TrueFor['blockkey']=1
                                TrueFor['roadkey']=1
                                TrueFor['housekey']=1
                        elif (self.matched[self.roadkey].strip().strip(',').strip() in geocoded_road or geocoded_road in self.matched[self.roadkey].strip().strip(',').strip()) and self.matched[self.roadkey].strip().strip(',').strip()!="" and matched_road_flag == 0 and geocoded_road !="":
                            print('when road not exact.........'+self.matched[self.roadkey].strip().strip(',').strip()+' vs '+ geocoded_road)
                            similarity=fuzz.ratio(self.matched[self.housekey].strip().strip(',').strip() ,geocoded_house)
                            gotHoldings.append(holding)
                            if similarity>maximum:
                                final_addr=i
                                maximum=similarity
                                TrueFor['subareakey']=1
                                TrueFor['blockkey']=1
                                TrueFor['roadkey']=2
                                TrueFor['housekey']=1
                        elif (fuzz.ratio(self.matched[self.roadkey].strip().strip(',').strip() ,geocoded_road)>80) and self.matched[self.roadkey].strip().strip(',').strip()!="" and matched_road_flag==0 and geocoded_road !="":
                            print('road match in fuzzy')
                            similarity=fuzz.ratio(self.matched[self.housekey].strip().strip(',').strip() ,geocoded_house)
                            gotHoldings.append(holding)
                            if similarity>maximum:
                                final_addr=i
                                maximum=similarity
                                TrueFor['subareakey']=1
                                TrueFor['blockkey']=1
                                TrueFor['roadkey']=3
                                TrueFor['housekey']=1
                        elif self.matched[self.roadkey].strip().strip(',').strip()=="" and matched_road_flag==0:
                            print('road empty')
                            similarity=fuzz.ratio(self.matched[self.housekey].strip().strip(',').strip() ,geocoded_house)
                            gotHoldings.append(holding)
                            if similarity>without_road_maximum:
                                final_addr=i
                                without_road_maximum=similarity
                                TrueFor['subareakey']=1
                                TrueFor['blockkey']=1
                                TrueFor['roadkey']=0
                                TrueFor['housekey']=1
                if self.matched[self.blockkey]=="":
                    print('when block is empty .............. '+self.matched[self.blockkey].strip().strip(',').strip()+' vs '+geocoded_block)
                    if self.matched[self.roadkey].strip().strip(',').strip() == geocoded_road and self.matched[self.roadkey].strip().strip(',').strip()!='':
                        print('when road provided ............. '+self.matched[self.roadkey].strip().strip(',').strip()+' vs '+ geocoded_road)
                        matched_road_flag = 1
                        similarity_exact=fuzz.ratio(self.matched[self.housekey].strip().strip(',').strip() ,geocoded_house)
                        gotHoldings.append(holding)
                        if similarity_exact>maximum_exact:
                            final_addr=i
                            exact_addr=i
                            maximum_exact=similarity_exact

                            TrueFor['subareakey']=1
                            TrueFor['blockkey']=0
                            TrueFor['roadkey']=1
                            TrueFor['housekey']=1
                    elif (self.matched[self.roadkey].strip().strip(',').strip() in geocoded_road or geocoded_road in self.matched[self.roadkey].strip().strip(',').strip()) and self.matched[self.roadkey].strip().strip(',').strip()!="" and matched_road_flag == 0 and geocoded_road !="":
                        print('when road not exact.............. '+self.matched[self.roadkey].strip().strip(',').strip()+' vs '+ geocoded_road)
                        similarity=fuzz.ratio(self.matched[self.housekey].strip().strip(',').strip() ,geocoded_house)
                        gotHoldings.append(holding)
                        if similarity>maximum:
                            final_addr=i
                            maximum=similarity
                            # print("803...............")
                            # print(geocoded_road)
                            # print(self.matched[self.roadkey].strip().strip(',').strip())
                            TrueFor['subareakey']=1
                            TrueFor['blockkey']=0
                            TrueFor['roadkey']=2
                            TrueFor['housekey']=1

                    elif (fuzz.ratio(self.matched[self.roadkey].strip().strip(',').strip() ,geocoded_road)>80) and self.matched[self.roadkey].strip().strip(',').strip()!="" and matched_road_flag == 0 and geocoded_road !="":
                        print('road match in fuzzy............'+self.matched[self.roadkey].strip().strip(',').strip()+' vs '+ geocoded_road)
                        similarity=fuzz.ratio(self.matched[self.housekey].strip().strip(',').strip() ,geocoded_house)
                        gotHoldings.append(holding)
                        if similarity>maximum:
                            final_addr=i
                            maximum=similarity
                            TrueFor['subareakey']=1
                            TrueFor['blockkey']=0
                            TrueFor['roadkey']=3
                            TrueFor['housekey']=1
                    elif self.matched[self.roadkey].strip().strip(',').strip()=="" and matched_road_flag==0:
                        print('road empty')
                        similarity=fuzz.ratio(self.matched[self.housekey].strip().strip(',').strip() ,geocoded_house)
                        gotHoldings.append(holding)
                        print("from 1183")
                        count+=1
                        print(count)
                        if similarity>without_road_maximum:
                            final_addr=i
                            without_road_maximum=similarity
                            TrueFor['subareakey']=1
                            TrueFor['blockkey']=0
                            TrueFor['roadkey']=0
                            TrueFor['housekey']=1                    
                

            elif (geocoded_area.strip()==self.matched[self.areakey].strip().strip(',').strip() and self.matched[self.subareakey].strip().strip(',').strip()==''):
                print('subarea missing.....................')
                if self.matched[self.blockkey]!="":
                    if self.matched[self.blockkey].strip().strip(',').strip() ==geocoded_block:
                        print("got block............ "+self.matched[self.blockkey].strip().strip(',').strip()+' vs '+geocoded_block)
                        if self.matched[self.roadkey].strip().strip(',').strip() ==geocoded_road:
                            print("got road.................... "+ self.matched[self.roadkey].strip().strip(',').strip()+' vs '+ geocoded_road)
                            matched_road_flag=1
                            similarity=fuzz.ratio(self.matched[self.housekey].strip().strip(',').strip() ,geocoded_house)
                            gotHoldings.append(holding)
                            if similarity>maximum_exact_b:
                                final_addr=i
                                exact_addr = i
                                maximum_exact_b=similarity
                                TrueFor['subareakey']=1
                                TrueFor['blockkey']=1
                                TrueFor['roadkey']=1
                                TrueFor['housekey']=1
                        elif (self.matched[self.roadkey].strip().strip(',').strip() in geocoded_road or geocoded_road in self.matched[self.roadkey].strip().strip(',').strip()) and geocoded_road!="" and matched_road_flag == 0:
                            print('didnt got road exact............'+ self.matched[self.roadkey].strip().strip(',').strip()+' vs '+ geocoded_road)
                            similarity=fuzz.ratio(self.matched[self.housekey].strip().strip(',').strip() ,geocoded_house)
                            gotHoldings.append(holding)
                            if similarity>maximum:
                                final_addr=i
                                maximum=similarity
                                TrueFor['subareakey']=1
                                TrueFor['blockkey']=1
                                TrueFor['roadkey']=2
                                TrueFor['housekey']=1
                        elif (fuzz.ratio(self.matched[self.roadkey].strip().strip(',').strip() ,geocoded_road)>80) and geocoded_road!="" and matched_road_flag==0:
                            print('road match in fuzzy............'+self.matched[self.roadkey].strip().strip(',').strip()+' vs '+ geocoded_road)
                            similarity=fuzz.ratio(self.matched[self.housekey].strip().strip(',').strip() ,geocoded_house)
                            gotHoldings.append(holding)
                            if similarity>maximum:
                                final_addr=i
                                maximum=similarity
                                TrueFor['subareakey']=1
                                TrueFor['blockkey']=1
                                TrueFor['roadkey']=3
                                TrueFor['housekey']=1
                        elif self.matched[self.roadkey].strip().strip(',').strip()=="" and matched_road_flag==0:
                            print('road empty')
                            similarity=fuzz.ratio(self.matched[self.housekey].strip().strip(',').strip() ,geocoded_house)
                            gotHoldings.append(holding)
                            if similarity>without_road_maximum:
                                final_addr=i
                                without_road_maximum=similarity
                                TrueFor['subareakey']=1
                                TrueFor['blockkey']=1
                                TrueFor['roadkey']=0
                                TrueFor['housekey']=1
                if self.matched[self.blockkey]=="":
                    print("when block is empty.......... " +self.matched[self.blockkey].strip().strip(',').strip()+' vs '+geocoded_block)
                    print(geocoded_road)
                    if self.matched[self.roadkey].strip().strip(',').strip() == geocoded_road:
                        print('got road............'+ self.matched[self.roadkey].strip().strip(',').strip()+' vs '+ geocoded_road)
                        matched_road_flag = 1
                        similarity_exact=fuzz.ratio(self.matched[self.housekey].strip().strip(',').strip() ,geocoded_house)
                        gotHoldings.append(holding)
                        if similarity_exact>maximum_exact:
                            final_addr=i
                            exact_addr=i
                            maximum_exact=similarity_exact
                            TrueFor['subareakey']=1
                            TrueFor['blockkey']=0
                            TrueFor['roadkey']=1
                            TrueFor['housekey']=1
                            # print("797...............")
                    elif (self.matched[self.roadkey].strip().strip(',').strip() in geocoded_road or geocoded_road in self.matched[self.roadkey].strip().strip(',').strip()) and geocoded_road!="" and matched_road_flag == 0:
                        print('didnt got road exact................ '+ self.matched[self.roadkey].strip().strip(',').strip()+' vs '+ geocoded_road)
                        similarity=fuzz.ratio(self.matched[self.housekey].strip().strip(',').strip() ,geocoded_house)
                        gotHoldings.append(holding)
                        if similarity>maximum:
                            final_addr=i
                            maximum=similarity
                            # print("803...............")
                            # print(geocoded_road)
                            # print(self.matched[self.roadkey].strip().strip(',').strip())
                            TrueFor['subareakey']=1
                            TrueFor['blockkey']=0
                            TrueFor['roadkey']=2
                            TrueFor['housekey']=1

                    elif (fuzz.ratio(self.matched[self.roadkey].strip().strip(',').strip() ,geocoded_road)>80) and geocoded_road!="" and self.matched[self.roadkey].strip().strip(',').strip()!="" and matched_road_flag == 0:
                        print('road match in fuzzy............'+self.matched[self.roadkey].strip().strip(',').strip()+' vs '+ geocoded_road)
                        similarity=fuzz.ratio(self.matched[self.housekey].strip().strip(',').strip() ,geocoded_house)
                        gotHoldings.append(holding)
                        if similarity>maximum:
                            final_addr=i
                            maximum=similarity
                            TrueFor['subareakey']=1
                            TrueFor['blockkey']=0
                            TrueFor['roadkey']=3
                            TrueFor['housekey']=1
                    elif self.matched[self.roadkey].strip().strip(',').strip()=="" and matched_road_flag==0:
                        print('road empty')
                        similarity=fuzz.ratio(self.matched[self.housekey].strip().strip(',').strip() ,geocoded_house)
                        gotHoldings.append(holding)
                        if similarity>without_road_maximum:
                            final_addr=i
                            without_road_maximum=similarity
                            TrueFor['subareakey']=1
                            TrueFor['blockkey']=0
                            TrueFor['roadkey']=0
                            TrueFor['housekey']=1
        self.matched[self.housekey] = matched_house_key
        self.GeoTrueFor=TrueFor
        print(gotHoldings)
        print(len(gotHoldings))
        if matched_road_flag==1:
            final_addr=exact_addr
            self.GeoTrueFor=TrueFor
        if final_addr=="":
            print("from prev 1")
            print(self.matched)
            final_addr=self.search_addr_bkoi(data,qstring)

        try:
            prop_filter = {
            'Address': final_addr['new_address'],
            'latitude': final_addr['latitude'],
            'longitude': final_addr['longitude'],
            'city': final_addr['city'],
            'area': final_addr['area'],
            'postCode': final_addr['postCode'],
            'pType': final_addr['pType'],
            'uCode': final_addr['uCode']
        }
        except Exception as e:
            prop_filter = {}


        return prop_filter



    def bind_address(self):

        # print('900..............in  bind ')
        # print(self.matched)
        try:
            # print('903..............in buildingkey check ')
            # print(self.matched)
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
            # print('928----------------- '+self.matched[self.subareakey])
            if self.matched[self.subareakey].lstrip(' ,').rstrip(' , ') == '':
                self.matched[self.subareakey] = None

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
        # print(self.matched)
        # print('887-------------------------------------'+ self.matched[self.buildingkey].strip().replace(',','').strip()+'-----------'+self.matched[self.roadkey].strip(','))
        # if self.matched[self.roadkey].strip().replace('road','').replace(',','').strip() in self.matched[self.buildingkey] and self.matched[self.buildingkey]!= '' and self.matched[self.roadkey]!='':
        #     self.matched[self.buildingkey]=self.matched[self.buildingkey].replace(self.matched[self.roadkey].strip().replace('road','').replace(',','').strip(),'')
        # print(self.matched[self.subareakey].strip().replace(',','').strip())

        if (self.matched[self.buildingkey].lstrip(' ,').rstrip(' , ') in self.matched[self.roadkey].lstrip(' ,').rstrip(' , ')  and self.matched[self.buildingkey].lstrip(' ,').rstrip(' , ') != '' and self.matched[self.roadkey].lstrip(' ,').rstrip(' , ')!='') or( self.matched[self.subareakey].lstrip(' ,').rstrip(' , ') == self.matched[self.buildingkey].lstrip(' ,').rstrip(' , ') and self.matched[self.subareakey].lstrip(' ,').rstrip(' , ')!='' and self.matched[self.buildingkey].lstrip(' ,').rstrip(' , ')!= '') :
            # print('977 =------------ ')
            self.matched[self.buildingkey]=''
            # print("905-------------------------")
        # self.matched[self.buildingkey]=self.matched[self.buildingkey].strip()
        if self.matched[self.subareakey]==self.matched[self.areakey]:
            # print('982......same AS')
            print(self.matched)
            full_address = self.matched[self.buildingkey] + self.matched[self.housekey] + self.matched[self.roadkey] + self.matched[self.blockkey] + self.matched[self.areakey] + self.matched[self.unionkey] + self.matched[self.sub_districtkey] + self.matched[self.districtkey]
        else:
            full_address = self.matched[self.buildingkey] + self.matched[self.housekey] + self.matched[self.roadkey] + self.matched[self.blockkey] + self.matched[self.subareakey] + self.matched[self.areakey] + self.matched[self.unionkey] + self.matched[self.sub_districtkey] + self.matched[self.districtkey]

        full_address = full_address.lstrip(' ,')
        full_address = full_address.rstrip(' ,')
        # print("990--------------------")
        # print(self.matched)
        # print(self.get_multiple_area)
        # print(self.get_multiple_subarea)
        # print(len(self.matched_array))
        if len(self.matched_array)<1:
            # print("913...........................")
            full_address = self.clone_input_address.lstrip().rstrip()
        print('......................................1090')
        print(self.tempArray)
        print(self.matched)
        
        return full_address


#Flask App.................................

