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
import similarity
from bkoi_e2b import ReverseTransformer


from dbconf.initdb import DBINIT


from miniparser import MiniParser
from spellcheck import SpellCheck


class Address(object):

    # initializaion............................
    def __init__(self):
        self.dict_data = []
        self.addresskey = 'address'
        self.namekey = 'name'
        self.flatkey = 'flat'
        self.housekey = 'House'
        self.buildingkey = 'building'
        self.roadkey = 'road'
        self.ssareakey = 'supersubarea'
        self.subareakey = 'subarea'
        self.areakey = 'area'
        self.districtkey = 'district'
        self.sub_districtkey = 'sub_district'
        self.unionkey = 'union'
        self.blockkey = 'block'
        self.subarea_pattern = 'subarea_pattern'
        # flags.......................
        self.area_flag = False
        self.area_pos = 0
        self.subarea_flag = False
        self.reverse_house_pattern = False
        self.reverse_road_pattern = False
        self.reverse_goli_pattern = False
        self.reverse_lane_pattern = False
        self.reverse_block_pattern = False
        self.reverse_section_pattern = False
        self.reverse_sector_pattern = False
        self.subarea_pos = 0
        self.matched = {}
        self.ambiguous_area = False
        self.ambiguous_subarea = False
        # init value...................
        self.matched[self.flatkey] = None
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
        self.matched[self.subarea_pattern] = []
        self.tempArray = []
        self.usedToken = []
        self.matched_array = []
        self.area_pattern = None
        self.confScore = 0
        self.get_multiple_subarea = []
        self.get_multiple_area = []
        self.subarea_list_pattern = []
        self.GeoTrueFor = {}
        self.dbinit = DBINIT()
        self.dbinit.load_area()
        self.dbinit.load_subarea()
        self.dbinit.load_dsu()
        self.globalAddress = ''
        self.extraHomeKeys = ''
        self.distance = 99
        self.name_search = None
        self.fixed_addr = ''
        self.get_geo_obj = []

    reverse_pattern = {
        'house': '',
        'road': '',
        'goli': '',
        'lane': '',
        'block': '',
        'ssarea': '',
        'subarea': '',

    }

    prefix_dict = ['', 'east', 'west', 'north', 'south', 'middle', 'purba',
                   'poschim', 'uttar', 'dakshin', 'moddho', 'dokkhin', 'dakkhin']

    address_component = ['', 'sarani', 'sarak', 'rasta', 'goli', 'lane', 'code', 'street',
                         'floor', 'level', 'house', 'plot', 'road', 'block', 'section', 'sector', 'avenue']

    building_name_key = ['building', 'plaza', 'market', 'bazar', 'villa', 'nibash', 'cottage', 'mansion', 'mension', 'vila', 'tower', 'place', 'complex', 'center', 'centre', 'mall', 'square', 'monjil', 'manjil', 'palace', 'headquarter', 'bhaban', 'mosque', 'masjid', 'mosjid', 'hospital', 'university', 'school', 'mandir', 'mondir', 'police station', 'club', 'garage', 'office', 'restaurent', 'cafe', 'hotel', 'garments', 'park', 'field', 'garden', 'studio', 'stadium', 'meusium', 'institute', 'store', 'college', 'varsity', 'coaching', 'library', 'tution', 'bank', 'atm', 'agent', 'Ministry', 'workshop', 'saloon', 'tailors', 'pharmacy',
                         'textile', 'laundry', 'hall', 'enterprise', 'shop', 'court', 'parliament', 'showroom', 'warehouse', 'electronics', 'optics', 'dokan', 'bitan', 'senitary', 'square', 'sports', 'motors', 'automobile', 'builders', 'service', 'developers', 'firm', 'limited', 'private', 'tech', 'company', 'incorporation', 'hardware', 'soft', 'software', 'solutions', 'bistro', 'printings', 'ghor', 'farm', 'fashions', 'style', 'pharma', 'medicine', 'church', 'girja', 'medical', 'clinic', 'somity', 'association', 'foundation', 'madrasa', 'kithcen', 'restora', 'stand', 'terminal', 'stop', 'care', 'dresser', 'tank', 'pump', 'corner', 'stationoery', 'kutir']
    tempList = ['ka', 'kha', 'ga', 'gha', 'uma', 'ca', 'cha', 'ja', 'jha', 'za', 'zha',
                'ta', 'tha', 'da', 'dha', 'na', 'pa', 'pha', 'fa', 'ma', 'ra', 'la', 'ha', 'ya', 'gp']
    rep2 = {
        # ' east':' east ', ' west':' west ', ' north':' north ', ' south':' south ', ' middle':' middle ', ' purba':' purba ', ' poschim':' poschim ', ' uttar':' uttar ', ' dakshin':' dakshin ', ' moddho':' moddho ', ' dokkhin':' dokkhin ', ' dakkhin':' dakkhin ',
        "rd#": " road ", "rd-": " road  ", " rode ": " road  ", " rd": " road  ", " road#": " road  ", "rd:": " road  ", "r:": " road ", "r#": " road ", "road #": " road ", " r-": " road ", " ,r-": " road ", ",r": " road ", " r ": " road ", "h#": " house ", "h-": " house ", "h:": " house ", " h ": " house ",
        "bl-": " block ", " blk ": " block ", " blc ": " block ", " blk: ": " block ", " blk- ": " block ", " blk# ": " block ", " blk": " block ", " bl ": " block ", " b ": " block ", "bl#": " block ", "bl:": " block ", "b-": " block ", "b:": " block ", "b#": " block ", 'sec-': ' sector ', 'sec.': ' sector ', ' sec ': ' sector ', 'sec#': ' sector ', 'sec:': ' sector ', 's-': ' sector ', ' s-': ' sector ', 's#': ' sector ', 's:': ' sector ', ' s ': ' sector ',
        'house': ' house ', 'house:': ' house ', ' basha ': ' house ', ' basa ': ' house ', ' bari ': ' house ', 'road:': ' road ', 'block': ' block ', 'block-': ' block ', 'block:': ' block ', 'block#': ' block ', 'section': ' section ', 'section:': ' section ', 'sector': ' sector ', 'sector:': ' sector ',
        'house no': ' house ', 'house no ': ' house ', 'houseno:': ' house ', 'road no': ' road ', ' no ': '', 'road no.': ' road ', 'block no': ' block ', 'blockno': ' block ', 'section no': ' section ', 'sectionno': ' section ', 'sector no': ' sector ', 'sector': ' sector ', 'number': '', 'no :': '', 'no:': '', 'no -': '', 'no-': '', 'no =': '', 'no#': '', 'no=': '', 'no.': '', ' num ': ' no ',
        'ave-': ' avenue ', 'ave:': ' avenue ', 'ave#': ' avenue ', 'ave:': ' avenue ', 'avenue:': ' avenue ', 'avenue-': ' avenue ', 'avenue#': ' avenue ', ' ln': ' lane ', ' ln#': ' lane ', ' ln:': ' lane', ' ln-': ' lane', ' len ': ' lane ', 'plot': ' ', ' ltd.': ' limited', ' pvt.': ' private', ' inc.': ' incorporation', ' co.': ' company',
    }
    rep1 = {
        # ' east':' east ', ' west':' west ', ' north':' north ', ' south':' south ', ' middle':' middle ', ' purba':' purba ', ' poschim':' poschim ', ' uttar':' uttar ', ' dakshin':' dakshin ', ' moddho':' moddho ', ' dokkhin':' dokkhin ', ' dakkhin':' dakkhin ',
        "rd#": " road ", "rd-": " road  ", " rode ": " road  ", " rd": " road  ", " road#": " road  ", "rd:": " road  ",
        "bl-": " block ", " blk ": " block ", " blc ": " block ", " blk: ": " block ", " blk- ": " block ", " blk# ": " block ", " blk": " block ", " bl ": " block ", "bl#": " block ", "bl:": " block ",  'sec-': ' sector ', ' sec ': ' sector ', 'sec#': ' sector ', 'sec.': ' sector ', 'sec:': ' sector ',
        'house': ' house ', 'house:': ' house ', ' basha ': ' house ', ' basa ': ' house ', ' bari ': ' house ', 'road:': ' road ', 'block': ' block ', 'block-': ' block ', 'block:': ' block ', 'block#': ' block ', 'section': ' section ', 'section:': ' section ', 'sector': ' sector ', 'sector:': ' sector ',
        'house no': ' house ', 'house no ': ' house ', 'houseno:': ' house ', 'road no': ' road ', 'road no.': ' road ', 'block no': ' block ', 'blockno': ' block ', 'section no': ' section ', 'sectionno': ' section ', 'sector no': ' sector ', 'sector': ' sector ',
        'ave-': ' avenue ', 'ave:': ' avenue ', 'ave#': ' avenue ', 'ave:': ' avenue ', 'avenue:': ' avenue ', 'avenue-': ' avenue ', 'avenue#': ' avenue ', ' ln': ' lane ', ' ln#': ' lane ', ' ln:': ' lane', ' ln-': ' lane',  'plot': ' ', ' ltd.': ' limited', ' pvt.': ' private', ' inc.': ' incorporation', ' co.': ' company',
    }

    area_dict = {"nikunjo": " nikunja ", "nikunja": " nikunja ", "mirpur": " mirpur ", "uttara": " uttara ", "banani": " banani ",
                 "mohammadpur": " mohammadpur ", "gulshan": " gulshan ", "baridhara": " baridhara ", "mdpur": "mohammadpur"}  # define desired replacements here

    def multiple_replace(self, dict, text):
        # Create a regular expression  from the dictionary keys
        regex = re.compile("(%s)" % "|".join(map(re.escape, dict.keys())))
        # For each match, look-up corresponding value in dictionary
        return regex.sub(lambda mo: dict[mo.string[mo.start():mo.end()]], text)

    def check_district(self, token, idx):
        dist_token = self.multiple_replace(self.area_dict, token.lower())
        # dist_token = word_tokenize(dist_token)
        dist_token = dist_token.split()

        district_list = self.dbinit.get_dsu()
        for j, district in enumerate(district_list):
            if (dist_token[0].lower() == district[2].lower() and dist_token[0].lower() in self.cleanAddressStr.lower()):
                self.matched[self.districtkey] = district[2].lower()
                return True

    def check_sub_district(self, token, idx):
        sub_dist_token = self.multiple_replace(self.area_dict, token.lower())
        # sub_dist_token = word_tokenize(sub_dist_token)
        sub_dist_token = sub_dist_token.split()
        with open('./dsu.csv', 'rt')as f:
            sub_district_list = csv.reader(f)
            for j, sub_district in enumerate(sub_district_list):
                if (sub_dist_token[0].lower() == sub_district[1].lower() and sub_dist_token[0].lower() in self.cleanAddressStr.lower()):
                    self.matched[self.sub_districtkey] = sub_district[1].lower()
                    return True

    def check_union(self, token, idx):
        union_token = self.multiple_replace(self.area_dict, token.lower())
        # union_token = word_tokenize(union_token)
        union_token = union_token.split()
        with open('./dsu.csv', 'rt')as f:
            union_list = csv.reader(f)
            for j, union in enumerate(union_list):
                if (union_token[0].lower() == union[0].lower() and union_token[0].lower() in self.cleanAddressStr.lower()):
                    self.matched[self.unionkey] = union[0].lower()
                    return True

    def check_area(self, token, idx):

        area_token = self.multiple_replace(self.area_dict, token.lower())
        # area_token = word_tokenize(area_token)
        area_token = area_token.split()

        area_list = self.dbinit.get_area()
        for j, area in enumerate(area_list):
            if (area_token[0].lower() == area.lower() and area_token[0].lower() in self.cleanAddressStr.lower()):
                self.matched[self.areakey] = area.lower()
                # matched_array.append(area[0].lower())
                self.area_flag = True
                self.area_pos = idx
                self.get_multiple_area.append(area.lower())
                return True

    def check_sub_area(self, token, idx):

        if self.area_flag == True:
            area = self.matched[self.areakey].lower()
            if (idx-self.area_pos == 1 and any(char.isdigit() for char in self.tempArray[idx])):
                if(area.lower() == 'mirpur'):
                    token = 'section ' + self.tempArray[idx]
                elif(area.lower() == 'uttara'):
                    token = 'sector ' + self.tempArray[idx]

                subarea_list = self.dbinit.get_subarea()
                for j, subarea in enumerate(subarea_list):
                    if (area.lower() == subarea[0].lower() and token.lower() == subarea[1].lower()):
                        self.matched[self.subareakey] = token.lower()
                        self.subarea_flag = True
                        self.get_multiple_subarea.append(token.lower())
                        tempObj = {
                            'area': subarea[0].strip().lower(),
                            'subarea': subarea[1].lower(),
                            'pattern': [subarea[2], subarea[3], subarea[4], subarea[5], subarea[6]]}
                        self.subarea_list_pattern.append(tempObj)
                        return True

            elif(abs(idx-self.area_pos) > 1 or abs(idx-self.area_pos) == 1 and not any(char.isdigit() for char in self.tempArray[idx])):
                token = token.lstrip('[0:!@#$-=+.]')
                token = token.rstrip('[:!@#$-=+.]')
                prefix_flag = False
                if ((token.lower() == 'section' or token.lower() == 'sector') and token.lower() in self.cleanAddressStr.lower() and idx < len(self.tempArray)-1):
                    self.matched[self.subareakey] = token + \
                        ' ' + self.tempArray[idx+1]
                    if (area.lower() == 'mirpur'):
                        self.matched[self.subareakey] = 'section' + \
                            ' ' + self.tempArray[idx+1]
                        self.get_multiple_subarea.append(
                            'section' + ' ' + self.tempArray[idx+1])
                        tempObj = {
                            'area': self.matched[self.areakey].lower(),
                            'subarea': self.matched[self.subareakey].lower(),
                            'pattern': ['H', 'H', 'H', 'L', 'H']
                        }
                        self.subarea_list_pattern.append(tempObj)
                    elif(area.lower() == 'uttara'):
                        self. matched[self.subareakey] = 'sector' + \
                            ' ' + self.tempArray[idx+1]
                        self.get_multiple_subarea.append(
                            'sector' + ' ' + self.tempArray[idx+1])
                        tempObj = {
                            'area': self.matched[self.areakey].lower(),
                            'subarea': self.matched[self.subareakey].lower(),
                            'pattern': ['H', 'H', 'L', 'L', 'H']
                        }
                        self.subarea_list_pattern.append(tempObj)
                    self.subarea_flag = True
                    return True

                subarea_list = self.dbinit.get_subarea()
                for j, subarea in enumerate(subarea_list):
                    # subarea[0] = subarea[0].strip()

                    if ((token.lower() in subarea[1].lower() and subarea[1].lower() in self.cleanAddressStr.lower())):
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
            #print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$1   "+token)
            subarea_list = self.dbinit.get_subarea()
            for j, subarea in enumerate(subarea_list):
                if (token.lower().strip() in subarea[1].lower().strip() and subarea[1].lower().strip() in self.cleanAddressStr.lower()):
                    #print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$1   "+token)
                    if (token.lower().strip() == 'section' or token.lower().strip() == 'sector') and len(self.tempArray)-1 > idx:
                        if token.lower().strip()+" "+self.tempArray[idx+1] == subarea[1].lower():
                            print("for section 12.......")
                            self.matched[self.subareakey] = subarea[1].lower()
                            self.matched[self.areakey] = subarea[0].lower()

                            self.get_multiple_subarea.append(
                                subarea[1].lower())
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
                        if "section" in subarea[1].lower() or "sector" in subarea[1].lower():
                            continue
                        #print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$2   "+token)
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
        tempList = ['ka', 'kha', 'ga', 'gha', 'uma', 'ca', 'cha', 'ja', 'jha', 'za', 'zha', 'ta',
                    'tha', 'da', 'dha', 'na', 'pa', 'pha', 'fa', 'ma', 'ra', 'la', 'ha', 'ya', 'gp', 'rrrr']
        if (any(char.isdigit() for char in token) or token in tempList or re.match(r'^[a-z]$', token)) and idx < len(self.tempArray)-1 and (self.matched[self.housekey] == None or self.matched[self.housekey] == ''):
            if idx == 0 and self.tempArray[idx+1].lower() != 'floor':
                self.matched[self.housekey] = token
                print('holding token 267')
                print(token)
                if ((any(char.isdigit() for char in self.tempArray[idx+1])) or re.match(r'^[a-z]$', self.tempArray[idx+1]) or (self.tempArray[idx+1] in tempList)) and idx < len(self.tempArray)-2:
                    self.matched[self.housekey] = self.matched[self.housekey] + \
                        "-"+self.tempArray[idx+1]
                    if idx < len(self.tempArray)-3:
                        if ((any(char.isdigit() for char in self.tempArray[idx+2])) or re.match(r'^[a-z]$', self.tempArray[idx+2]) or (self.tempArray[idx+2] in tempList)):
                            self.matched[self.housekey] = self.matched[self.housekey] + \
                                "-"+self.tempArray[idx+2]
                return True

            if self.tempArray[idx-1].lower() not in self.address_component:
                check_match = 0
                print('279------------')
                print(token)
                area_list = self.dbinit.get_subarea()
                for j, area in enumerate(area_list):
                    if area[0].lower() == self.tempArray[idx-1].lower():
                        check_match = 1
                        break
                if self.matched[self.housekey] == None:
                    self.matched[self.housekey] = ""
                if check_match == 0 and token not in self.matched[self.housekey]:
                    self.matched[self.housekey] = token
                    print('290----------- '+self.matched[self.housekey])
                    if ((any(char.isdigit() for char in self.tempArray[idx+1])) or re.match(r'^[a-z]$', self.tempArray[idx+1]) or (self.tempArray[idx+1] in tempList)) and idx < len(self.tempArray)-2:
                        self.matched[self.housekey] = self.matched[self.housekey] + \
                            "-"+self.tempArray[idx+1]
                        if ((any(char.isdigit() for char in self.tempArray[idx+2])) or re.match(r'^[a-z]$', self.tempArray[idx+2]) or (self.tempArray[idx+2] in tempList)) and idx < len(self.tempArray)-3:
                            self.matched[self.housekey] = self.matched[self.housekey] + \
                                "-"+self.tempArray[idx+2]
                    return True
            return True

        elif ((token.lower() == 'house' or token.lower() == 'plot') and idx < len(self.tempArray)-1):
            tempList = set(tempList)
            if (any(char.isdigit() for char in self.tempArray[idx+1])) or (self.tempArray[idx+1] in tempList) or (re.match(r'^[a-z]$', self.tempArray[idx+1])) or (re.match(r'^[a-z]/[a-z]$', self.tempArray[idx+1])):
                # chk_house_no=re.search(r'\w', self.tempArray[idx+1].strip(","))
                # if chk_house_no:

                self.matched[self.housekey] = self.tempArray[idx+1]
                if idx < len(self.tempArray)-2:
                    p1 = re.match(r'[0-9]+', self.tempArray[idx+2])
                    p2 = re.match(r'^[a-z]$', self.tempArray[idx+2])
                    p3 = re.match(r'^[A-Z]$', self.tempArray[idx+2])
                    if p1 or p2 or p3 or (self.tempArray[idx+2] in tempList):
                        self.matched[self.housekey] = self.tempArray[idx+1] + \
                            "-"+self.tempArray[idx+2]
                        if idx < len(self.tempArray)-3:
                            if ((any(char.isdigit() for char in self.tempArray[idx+3])) or re.match(r'^[a-z]$', self.tempArray[idx+3]) or (self.tempArray[idx+3] in tempList)):
                                self.matched[self.housekey] = self.matched[self.housekey] + \
                                    "-"+self.tempArray[idx+3]

                    # matched_array.append(tempArray[idx+1])
                return True

    def check_holding_name(self, token, idx):
        tempList = ['ka', 'kha', 'ga', 'gha', 'uma', 'ca', 'cha', 'ja', 'jha', 'za', 'zha', 'ta',
                    'tha', 'da', 'dha', 'na', 'pa', 'pha', 'fa', 'ma', 'ra', 'la', 'ha', 'ya', 'gp', 'rrrr']
        if any(char in token for char in self.building_name_key) and self.matched[self.buildingkey] == None:
            if idx != len(self.tempArray) and idx != 0:
                i = idx-1
                building_str = ''
                self.matched[self.buildingkey] = building_str
                while i >= 0:
                    if any(char.isdigit() for char in self.tempArray[i]):
                        break
                    if not i == 0 and (self.tempArray[i-1] in self.address_component or self.tempArray[i-1] in tempList):
                        if not any(char.isdigit() for char in self.tempArray[i]):
                            building_str = self.tempArray[i] + \
                                " " + building_str
                            break

                        break
                    building_str = self.tempArray[i] + " " + building_str
                    i = i-1
                self.matched[self.buildingkey] = self.matched[self.buildingkey] + \
                    ", "+building_str + token
                return True

    def check_block(self, token, idx):
        tempList = ['ka', 'kha', 'ga', 'gha', 'uma', 'ca', 'cha', 'ja', 'jha', 'za', 'zha',
                    'ta', 'tha', 'da', 'dha', 'na', 'pa', 'pha', 'fa', 'ma', 'ra', 'la', 'ha', 'ya', 'gp']
        tempList = set(tempList)
        p = 0
        if (token.lower() == 'block' and idx < len(self.tempArray)-1):
            p = re.match(
                r'^(?=.*[0-9])(?=.*[a-zA-Z])([a-zA-Z0-9]+)$', self.tempArray[idx+1])
            p1 = re.match(r'[0-9]+', self.tempArray[idx+1])
            p2 = re.match(r'^[a-z]$', self.tempArray[idx+1])
            p3 = re.match(r'^[A-Z]$', self.tempArray[idx+1])
            p_slash = re.match(r'(^[a-z])/[0-9]+$', self.tempArray[idx+1])
            p_hi = re.match(r'(^[a-z])-[0-9]+$', self.tempArray[idx+1])
            if p or p1 or p2 or p3 or p_slash or p_hi or (self.tempArray[idx+1] in tempList):
                self.matched[self.blockkey] = self.tempArray[idx+1]
                p = 1
                return True
            else:
                p = 0

        if (token.lower() == 'block' and idx <= len(self.tempArray) and p == 0):
            p = re.match(
                r'^(?=.*[0-9])(?=.*[a-zA-Z])([a-zA-Z0-9]+)$', self.tempArray[idx-1])
            p1 = re.match(r'[0-9]+', self.tempArray[idx-1])
            p2 = re.match(r'^[a-z]$', self.tempArray[idx-1])
            p3 = re.match(r'^[A-Z]$', self.tempArray[idx-1])
            p_slash = re.match(r'(^[a-z])/[0-9]+$', self.tempArray[idx-1])
            p_hi = re.match(r'(^[a-z])-[0-9]+$', self.tempArray[idx-1])
            if p or p1 or p2 or p3 or p_slash or p_hi or (self.tempArray[idx-1] in tempList) or(self.tempArray[idx-1] not in self.matched_array):
                self.matched[self.blockkey] = self.tempArray[idx-1]
            return True

    def check_road(self, road, idx):

        tempList = ['ka', 'kha', 'ga', 'gha', 'uma', 'ca', 'cha', 'ja', 'jha', 'za', 'zha',
                    'ta', 'tha', 'da', 'dha', 'na', 'pa', 'pha', 'fa', 'ma', 'ra', 'la', 'ha', 'ya', 'gp']
        if 'road' == road or 'avenue' == road or 'ave' == road or 'lane' == road or 'sarani' == road or 'soroni' == road or 'rd#' == road or 'sarak' == road or 'sharak' == road or 'shorok' == road or 'sharani' == road or 'highway' == road or 'path' == road or 'poth' == road or 'chowrasta' == road or 'sarak' == road or 'rasta' == road or 'sorok' == road or 'goli' == road or 'street' == road or 'line' == road:
            if 'ave' == road:
                road = 'avenue'

            if idx != len(self.tempArray)-1:
                if (any(char.isdigit() for char in self.tempArray[idx+1])):
                    num = re.findall(r'\d+', self.tempArray[idx+1])
                    num = max(map(int, num))
                    if(self.matched[self.roadkey] == None and num < 1000):
                        self.matched[self.roadkey] = road + \
                            " "+self.tempArray[idx+1]
                        return True
                    # road x avenue y
                    if self.matched[self.roadkey] == None:
                        self.matched[self.roadkey] = ''
                    if num < 1000:
                        self.matched[self.roadkey] = self.matched[self.roadkey] + \
                            ", "+road+" " + self.tempArray[idx+1]
                    return True
            if idx != 0:
                if (not any(char.isdigit() for char in self.tempArray[idx-1])):
                    i = idx-1
                    road_str = ''
                    if (not self.matched[self.areakey] == None and self.tempArray[i] == self.matched[self.areakey]):
                        self.matched[self.roadkey] = self.matched[self.areakey] + " " + road
                        return True

                    while i >= 0:
                        if any(char.isdigit() for char in self.tempArray[i]) or self.tempArray[i] in self.address_component:
                            break
                        if not i == 0 and (self.tempArray[i-1] in self.address_component or self.tempArray[i-1] in self.building_name_key or self.tempArray[i-1] in tempList or (re.match(r'^[a-z]$', self.tempArray[i-1]) and self.tempArray[i-2] == 'block')):
                            if not any(char.isdigit() for char in self.tempArray[i]):
                                road_str = self.tempArray[i] + " " + road_str
                                break
                            break
                        road_str = self.tempArray[i] + " " + road_str
                        i = i-1
                    if(self.matched[self.roadkey] == None):
                        self.matched[self.roadkey] = road_str + road
                        return True
                    self.matched[self.roadkey] = self.matched[self.roadkey] + \
                        ", "+road_str + road
                    # matched_array.append(matched[roadkey])
                    return True

    def check_apartment(self, address):
        address = address.lower()
        match_apartment = re.search(
            r'(apt|apartment)\s*(no)*[.]*(-)*(#)*(:)*(:-)*\s*([a-z](-)*[/]*[0-9]+|[0-9]+(-)*[/]*[a-z]|\d+)', address)
        if match_apartment:
            print(match_apartment.group())
            value = str(match_apartment.group(7))
            self.globalAddress = self.globalAddress.replace(
                match_apartment.group(), ' ')
            value = value.replace('-', '')
            value = value.replace(' ', '')
            return 'apartment '+value
        else:
            return "None"

    def check_room(self, address):
        address = address.lower()
        match_room = re.search(
            r'\s+room\s*(no)*[.]*(-)*(#)*(:)*(:-)*\s*(\d+)', address)
        if match_room:
            self.globalAddress = self.globalAddress.replace(
                match_room.group(), ' ')
            print(match_room.group(6))
            return 'room '+str(match_room.group(6))
        else:
            return "None"

    def check_flat(self, address):
        address = address.lower()
        match_flat = re.search(
            r'flat\s*(no)*[.]*(-)*(#)*(:)*(:-)*\s*([a-z](-)*[/]*[0-9]+|[0-9]+(-)*[/]*[a-z])', address)
        if match_flat:
            print(match_flat.groups())
            self.globalAddress = self.globalAddress.replace(
                match_flat.group(), ' ')
            value = str(match_flat.group(6))
            value = value.replace('-', '')
            value = value.replace(' ', '')
            return 'flat '+value
        else:
            return "None"

    def check_floor(self, address):
        address = address.lower()
        match_floor = re.search(
            r'(\d+s*th|1st|2nd|3rd)\s*(floor|flr)', address)
        if match_floor:
            self.globalAddress = self.globalAddress.replace(
                match_floor.group(), ' ')
            print(match_floor.groups())
            return 'floor '+str(match_floor.group(1))
        else:
            return "None"

    def check_level(self, address):
        address = address.lower()
        match_level = re.search(
            r'level\s*(-)*(#)*(:)*(:-)*\s*(\d+)', address)
        if match_level:
            self.globalAddress = self.globalAddress.replace(
                match_level.group(), ' ')
            print(match_level.groups())
            return str(match_level.group())
        else:
            return "None"

    def check_dhanmondi_road(self, addr):
        ss = re.search(
            r'(dh*a+nm(a+|o+|u+)nd(i+|e+|y+))\s*((10|11|12|13|14|15|27|1|2|3|4|5|6|7|8|9)\\*\/*a*)', addr)
        if ss:
            d = ss.groups()
            res = ss.group()
            print('road in dhanmondi')
            print(res)
            addr = addr.replace(res, d[0]+" road "+d[3])
        return addr

    def hasNumbers(self, inputString):
        return any(char.isdigit() for char in inputString)

    def check_address_status(self):
        area_pattern = self.dbinit.get_subarea()
        checkst = 0
        getarea = 0
        same_sub_area_count = 0
        assignaddress = 1
        self.matched[self.areakey] = self.matched[self.areakey].replace(
            ',', '')
        if self.matched[self.areakey] not in self.cleanAddressStr:
            same_sub_area_count = 1
        self.matched[self.areakey] = self.matched[self.areakey].strip()
        if self.matched[self.areakey] in self.tempArray:
            assignaddress = 0
        for j, status in enumerate(area_pattern):

            area_name = status[0].lower()
            sub_area_name = status[1].lower()
            house_st = status[2]
            road_st = status[3]
            block_st = status[4]
            ssarea_st = status[5]
            subarea_st = status[6]

            dict_areakey = self.matched[self.areakey].replace(',', '')
            dict_sub_areakey = self.matched[self.subareakey].replace(',', '')

            if self.matched[self.areakey] == '':
                checkst = 1
                break
            if dict_sub_areakey.strip() == sub_area_name.strip() and area_name.strip() != dict_areakey.strip() and assignaddress == 1:
                same_sub_area_count += 1
                if same_sub_area_count >= 2:
                    checkst = 1
                    break

            elif dict_sub_areakey.strip() == sub_area_name.strip() and area_name.strip() == dict_areakey.strip():
                getarea = 1
                if house_st == 'H' and self.matched[self.housekey] == '':
                    checkst = 1
                if road_st == 'H' and self.matched[self.roadkey] == '':
                    checkst = 1
                if block_st == 'H' and self.matched[self.blockkey] == '':
                    checkst = 1
                if ssarea_st == 'H' and self.matched[self.ssareakey] == '':
                    checkst = 1
                if subarea_st == 'H' and self.matched[self.subareakey] == '':
                    checkst = 1

        if checkst == 1 or getarea == 0:
            return "incomplete"
        elif getarea == 1 and checkst == 0:
            return "complete"
        else:
            return "incomplete"

    def check_all_home_keys(self, address):
        homeKeys = ''
        response = self.check_flat(address)
        if response != 'None':
            homeKeys += response+', '
        response = self.check_room(address)
        if response != 'None':
            homeKeys += response+', '
        response = self.check_floor(address)
        if response != 'None':
            homeKeys += response+', '
        response = self.check_level(address)
        if response != 'None':
            homeKeys += response+', '
        response = self.check_apartment(address)
        if response != 'None':
            homeKeys += response
        return homeKeys

    # Start parsing...

    def parse_address(self, input_address, thana_param, district_param):
        # adding extra space before inputted address and convert it into lowercase
        saveTortnAddr = input_address
        print(input_address)
        input_address = " "+input_address
        input_address = input_address.lower()

        self.globalAddress = input_address
        self.extraHomeKeys = self.check_all_home_keys(self.globalAddress)
        input_address = self.globalAddress
        # checking if address is blank , return
        if input_address.strip().lstrip(',').rstrip(',') == '':
            return {
                'status': 'Not An Address',
                'address': input_address,
                'input_address': saveTortnAddr,
            }

        # ******************barikoi keyword seacrh*************
        barikoi_search = re.match(
            '((bari\s*(-)*koi)\s*(technolog(ies|y))*\s*(limited|ltd\.*)*(office)*)|((bari\s*(-)*koi|bkoi)\s*(-)*2017)', input_address.strip())
        print(barikoi_search)
        if barikoi_search:
            return self.barikoi_office_search('barikoi')

        # remove hash, comma, qoutation marks from the address and add extra space after the address
        input_address = re.sub(r',', ' ', input_address)
        input_address = re.sub(r'#|"', ' ', input_address)
        input_address = input_address.lower()+"  "
        input_address = "  "+input_address.lower()
        input_address = re.sub(
            r'\s*flat\s*(no)*(:)*(-)*\s*[a-z]{1}\d{1}\s+', ' ', input_address)
        # remove the section inside the first brakets() as considered as a comments or hints of an address
        input_address = re.sub(r'\([^)]*\)', '', input_address)
        # insert space between 'no' and digits
        input_address = re.sub(r'(\d+)(no\s+)', r'\1 \2', input_address)
        input_address = re.sub(r'(\s+no)(\d+)', r'\1 \2', input_address)
        input_address = "  "+input_address
        # replace the short abbreviated keywords into full form with rep1 dictionary
        input_address = self.multiple_replace(self.rep1, input_address.lower())
        # Check Reverse pattern like 3 no house
        self.Check_Reverse_Key(input_address)
        # remove 5 digits value
        if re.search('\d{5}', input_address):
            temp_input_address = input_address.split()
            for i, t in enumerate(temp_input_address):
                if re.search('\d{5}', t):
                    temp_input_address[i] = ""
            input_address = ' '.join(str(e) for e in temp_input_address)
        '''
        decimal_find=re.search(r'\d(.)\d',input_address)
        if  not re.search(r'\d(.)\d',input_address):
            input_address=input_address.replace("."," ")
        '''
        # replace the following characters with space
        input_address = input_address.replace(";", " ")
        # input_address=input_address.replace("\r\n"," ")
        input_address = input_address.replace("\\n", " ")
        # input_address=input_address.replace("\t"," ")
        # input_address=input_address.replace("\\"," ")
        input_address = input_address.replace("=", " ")
        input_address = input_address.replace("-", " ")
        input_address = input_address.replace("–", " ")
        input_address = input_address.replace(":", " ")
        input_address = input_address.replace("#", " ")
        input_address = input_address.replace(" no ", " ")
        print("508-----------------"+input_address)
        # some address contains 'street' or 'address' keyword at the begining of the address. so remove them
        try:
            first_street = re.match(
                r'\W*(\w[^,. !?"]*)', input_address).groups()[0]
        except:
            first_street = ""
        if 'street' in first_street or 'street:' in first_street or first_street == 'street' or first_street == 'street:' or first_street == 'office:' or first_street == 'address:' or first_street == 'address':
            input_address = input_address.replace(first_street, " ")

        # remove the string like 'near xyz hospitals' etc
        input_address = re.sub(
            r'(behind|nearby|near|near by|near to|opposite|opposite of|beside)[^)]*(building|plaza|market|villa|cottage|mansion|vila|tower|place|complex|center|mall|monjil|manjil|building|headquarter|bhaban|mosque|masjid|mosjid|hospital|university|school|mandir|mondir|police station|park)', '', input_address)
        # delete flat no. or etc
        temp_input_address = input_address.split()
        if 'flat' in input_address:
            temp_input_address = input_address.split()
            for i, t in enumerate(temp_input_address):
                if i < len(temp_input_address)-1:
                    if t == 'flat' and any(char.isdigit() for char in temp_input_address[i+1]):
                        temp_input_address.remove(temp_input_address[i])
                        temp_input_address.remove(temp_input_address[i])
                        break
            input_address = ' '.join(str(e) for e in temp_input_address)

        # remove postal codes
        input_address = re.sub(
            r'(post code|post|zip code|postal code|postcode|zipcode|postalcode|dhaka)(\s*)(-|:)*(\s*)(\d{4})(\s*)', '', input_address)
        # remove apt, room level no etc
        # flat floor stroing
        flat = None
        flat = re.search(
            r'((\s+)(apt|apartment|floor|room|flat|level|flr|suite|suit)(\s+(no)*[.]*(:)*\s*(-)*\s*)(([0-9]+|\d+)((th|rd|st|nd))))(\s*)|(\s*)((\s*)(([0-9]+|\d+)(th|rd|st|nd))(\s*(:)*\s*(-)*\s+)(apt|apartment|floor|flat|level|room|flr|suite|suit))(\s*)|(((\s+)(apt|apartment|floor|flat|level|room|flr|suite|suit)(\s*(:)*\s*(-)*\s*)(\d+[a-z]{1}\s+)))(\s*)|(\s+)(((apt|apartment|floor|flat|level|room|flr|suite|suit)(no)*(\s*)(([0-9]+|\d+))(th|rd|st|nd)))(\s*)',  input_address)
        if flat:
            print("got flat")
            print(flat)
        input_address = re.sub(
            r'((\s+)(apt|apartment|floor|room|flat|level|flr|suite|suit)(\s+(no)*[.]*(:)*\s*(-)*\s*)(([0-9]+|\d+)((th|rd|st|nd))))(\s*)|(\s*)((\s*)(([0-9]+|\d+)(th|rd|st|nd))(\s*(:)*\s*(-)*\s+)(apt|apartment|floor|flat|level|room|flr|suite|suit))(\s*)|(((\s+)(apt|apartment|floor|flat|level|room|flr|suite|suit)(\s*(:)*\s*(-)*\s*)(\d+[a-z]{1}\s+)))(\s*)|(\s+)(((apt|apartment|floor|flat|level|room|flr|suite|suit)(no)*(\s*)(([0-9]+|\d+))(th|rd|st|nd)))(\s*)', '  ', input_address)
        input_address = re.sub(
            r'(\s+[1-9]+|\d+)(th|rd|st|nd)\s+', ' ', input_address)
        input_address = input_address.replace(',', ' ')
        # remove the number greater than 3000
        all_num_list = re.findall(r'\d+', input_address)
        if len(all_num_list) > 0:
            max_num_in_string = max(map(int, all_num_list))
            if max_num_in_string > 3000:
                max_num_in_string = str(max_num_in_string)
                input_address = input_address.replace(max_num_in_string, '')
        # HBRS updated as (hbrs)rrrr and cut so that it can't change into house road block sector since these hbrs as a value not key
        cut_hbrs = re.search(
            r'(house(\s+)(-|/|:)*(\s*))((h|b|r|s)(\s+))', input_address)
        check_hbrs = 0
        if(cut_hbrs):
            check_hbrs = 1
            cut_hbrs = cut_hbrs.group(5)
            input_address = re.sub(
                r'(house(\s+)(-|/|:)*(\s*))((h|b|r|s)(\s+))', r'\1rrrr ', input_address)

        input_address = re.sub(
            '(h|b|r|s)((\s*)(plaza|market|villa|cottage|mansion|vila|tower|place|complex|center|centremall|monjil|manjil|building|headquarter))', r'\1. \2', input_address)
        block_h = re.search('block(\s*)(no)*(:)*(-)*(\s*)(h )', input_address)
        if block_h:
            self.matched[self.blockkey] = 'h'
            input_address = re.sub(
                'block(\s*)(no)*(:)*(-)*(\s*)(h )', ' ', input_address)

        block_b = re.search('block(\s*)(no)*(:)*(-)*(\s*)(b )', input_address)
        if block_b:
            self.matched[self.blockkey] = 'b'
            input_address = re.sub(
                'block(\s*)(no)*(:)*(-)*(\s*)(b )', ' ', input_address)

        block_r = re.search('block(\s*)(no)*(:)*(-)*(\s*)(r )', input_address)
        if block_r:
            self.matched[self.blockkey] = 'r'
            input_address = re.sub(
                'block(\s*)(no)*(:)*(-)*(\s*)(r )', ' ', input_address)

        block_s = re.search('block(\s*)(no)*(:)*(-)*(\s*)(s )', input_address)
        if block_s:
            self.matched[self.blockkey] = 's'
            input_address = re.sub(
                'block(\s*)(no)*(:)*(-)*(\s*)(s )', ' ', input_address)

        b_block = re.search('\s+b(\s*)(:)*(-)*(\s*)block', input_address)
        if b_block:
            self.matched[self.blockkey] = 'b'
            input_address = re.sub(
                '\s+b(\s*)(:)*(-)*(\s*)block', ' ', input_address)
        print(input_address + ".....................................610")

        h_block = re.search('\s+h(\s*)(:)*(-)*(\s*)block', input_address)
        if h_block:
            # print("treu...........")
            self.matched[self.blockkey] = 'h'
            input_address = re.sub(
                '\s+h(\s*)(:)*(-)*(\s*)block', ' ', input_address)
        # insert extra hyphen(-) between digits and aphabetic strings
        # insert a '-' between letters and number
        input_address = re.sub(r'([a-zA-Z]+)(\d+)', r'\1-\2', input_address)
        # insert a '-' between letters and number
        input_address = re.sub(r'(\d+)([a-zA-Z]+)', r'\1-\2', input_address)
        # pre-processing...........................................................

        # input_address = re.sub( r'h\s+tower','h* tower', input_address)
        print('////////////////////')
        # print("574-----------------"+input_address)
        # remove dots if string has no domain name like xyz.com
        print(input_address)
        if (re.search('.com|.xyz|.net|.co|.inc|.org|.bd.com|.edu|\d+\.\d+', input_address) == None):
            input_address = input_address.replace(".", "  ")
            print(input_address)
            print('##############################')
        input_address = "  "+input_address
        # replace the short abbreviated keywords into full form with rep2 dictionary
        expand = self.multiple_replace(self.rep2, input_address.lower())
        expand = self.multiple_replace(self.area_dict, expand.lower())
        # print("579-----------------"+input_address)
        # unknown char remove
        expand = re.sub(r'#|"', ' ', expand)
        # replace rrrr with cut_hbrs which contains h or b r or s
        if(check_hbrs == 1):
            expand = expand.replace('rrrr', cut_hbrs.strip())
        input_address = expand

        # regex to correct spell of area and subarea
        sec_input_address = input_address
        input_address = re.sub(
            'sh*id+h*es+h*\s*w*(o+|a+)r(i|y)', 'siddheshwari', input_address)
        input_address = re.sub(
            'n(i|e)k(u+|o+|)n(j|g|z)h*(a|o)*', 'nikunja', input_address)
        subarea_list = self.dbinit.get_subarea()
        for j, subarea in enumerate(subarea_list):
            try:
                input_address = re.sub(subarea[7].strip().lower(
                ), subarea[0].strip().lower(), input_address)
                input_address = re.sub(subarea[8].strip().lower(
                ), subarea[1].strip().lower(), input_address)
            except Exception as e:
                print(e)
                pass

        # can be changed
        if 'block' in input_address and 'sector' in input_address:
            input_address = input_address.replace('sector', 'section')
        print(input_address+"  "+sec_input_address)

        input_address = re.sub(r'([a-zA-Z])(\d)', r'\1*\2', input_address)
        print('INPUT ADDRESS............')
        print(input_address)
        print(input_address)
        x = input_address.split("*")
        input_address = " "

        # spell_checker
        # print('before spellcheck '+expand)

        spell_check = SpellCheck('area-list.txt')
        for i in x:
            i = i.strip()
            if len(i) > 5:
                spell_check.check(i)
                i = str(spell_check.correct())
            input_address += i
        print('after spellcheck '+input_address)

        # replace string with 'mirpur dohs' if conains such as 'dohs mirpur'
        input_address = re.sub('dohs\s*(,)*\s*mirpur',
                               'mirpur dohs', input_address)
        input_address = re.sub('dohs\s*(,)*\s*mohakhali',
                               'mohakhali dohs', input_address)
        input_address = re.sub('dohs\s*(,)*\s*baridhara',
                               'baridhara dohs', input_address)
        input_address = re.sub('dohs\s*(,)*\s*banani',
                               'banani dohs', input_address)
        expand = input_address
        self.clone_input_address = input_address

        expand = expand.lower()+"  "
        # expand=re.sub(r'((\s*)(floor|flat|level)(\s*(:)*\s*(-)*\s*)([0-9]+((th|rd|st|nd)))) | ((\s*)([0-9]+(th|rd|st|nd))(\s*(:)*\s*(-)*\s*)(floor|flat|level)(\s*))  | ((floor|flat|level)[0-9]+(th|rd|st|nd)*[a-z]+) ', ' ', expand)
        # addresscomponents = word_tokenize(expand)
        # insert space between english road name like greenroad to green road to fix 'abroad' problem
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
        if re.search('sector\s+\d+\s+mirpur', temp_str_address):
            temp_str_address = temp_str_address.replace('sector', 'section')
        if 'road' not in temp_str_address:
            temp_str_address = self.check_dhanmondi_road(temp_str_address)
        addresscomponents = temp_str_address.split()
        for i, comp in enumerate(addresscomponents):
            comp = comp.strip()
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
            self.cleanAddressStr = self.cleanAddressStr.replace(
                "sector", "section")
        if 'uttara' in self.cleanAddressStr and 'section' in self.cleanAddressStr:
            self.cleanAddressStr = self.cleanAddressStr.replace(
                "section", "sector")

        # self.tempArray = word_tokenize(self.cleanAddressStr)

            # self.cleanAddressStr="mrpr s2"

        # Parsing..............................
        for i, comp in enumerate(self.tempArray):
            comp = comp.strip()
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
            if (self.check_block(comp, i)):
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
            if (self.check_district(comp, i)):
                if (self.matched[self.areakey] == None or self.matched[self.areakey] == ''):
                    self.matched_array.append(self.matched[self.districtkey])

                continue
            if (self.check_sub_district(comp, i)):
                if (self.matched[self.areakey] == None or self.matched[self.areakey] == ''):
                    self.matched_array.append(
                        self.matched[self.sub_districtkey])
                continue
            if (self.check_union(comp, i)):
                if (self.matched[self.areakey] == None or self.matched[self.areakey] == ''):
                    self.matched_array.append(self.matched[self.unionkey])
                continue

        try:
            self.matched[self.roadkey] = self.matched[self.roadkey].replace(
                '-', '/')
        except Exception as e:
            print(e)
            pass
        print('******************************')
        print(self.get_multiple_area)
        print('******************************')
        # if self.matched[self.roadkey]!='' or self.matched[self.roadkey]!=None:
        #     self.matched[self.roadkey]=self.matched[self.roadkey].replace('-','/')
        getsubarea = list(set(self.get_multiple_subarea))
        subarea_min = ''
        subarea_high = ''
        max_H = -1
        min_H = 5
        if len(getsubarea) >= 2:
            for j, subarea in enumerate(self.subarea_list_pattern):

                if max_H < subarea['pattern'].count('H') and subarea['subarea'].strip() not in self.get_multiple_area:
                    max_H = subarea['pattern'].count('H')
                    subarea_high = subarea['subarea']
                if min_H > subarea['pattern'].count('H') and subarea['subarea'].strip() not in self.get_multiple_area:
                    min_H = subarea['pattern'].count('H')
                    subarea_min = subarea['subarea']

            self.matched[self.subareakey] = subarea_high
            for j, subarea in enumerate(self.subarea_list_pattern):
                if (subarea['subarea'].strip() == subarea_high.strip()) and (((subarea['pattern'][0]) == 'H' and self.matched[self.housekey] == None) or ((subarea['pattern'][0]) == 'H' and self.matched[self.housekey] == '') or ((subarea['pattern'][1]) == 'H' and self.matched[self.roadkey] == None) or ((subarea['pattern'][1]) == 'H' and self.matched[self.roadkey] == '') or ((subarea['pattern'][2]) == 'H' and self.matched[self.blockkey] == None) or ((subarea['pattern'][2]) == 'H' and self.matched[self.blockkey] == '') or ((subarea['pattern'][3]) == 'H' and self.matched[self.ssareakey] == None) or ((subarea['pattern'][3]) == 'H' and self.matched[self.ssareakey] == '')):
                    self.matched[self.subareakey] = subarea_min
                    break

        # if len(getsubarea)>=2:
        #     for subarea in getsubarea:
        #         if subarea not in self.get_multiple_area:
        #             self.matched[self.subareakey]=subarea.lower()

        # subarea_list = self.dbinit.get_subarea()

        getarea = list(set(self.get_multiple_area))
        avail_area = getarea
        if len(getarea) >= 2:
            chk = 0
            for area in getarea:
                subarea_list = self.dbinit.get_subarea()
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
                    if subarea[0].lower() == area and subarea[1].lower() == self.matched[self.subareakey] and area in self.tempArray:
                        self.matched[self.areakey] = area.lower()
                        chk = 1
                        break
                    if subarea[0].lower() == area and subarea[1].lower() == self.matched[self.subareakey] and chk == 0:
                        # area=area.rstrip(',')
                        self.matched[self.areakey] = area.lower()
                        break
        amgs_area = 0
        if len(getarea) >= 2:
            for area in getarea:
                try:
                    if area in self.matched[self.roadkey] or area in self.matched[self.buildingkey]:
                        avail_area.remove(area)
                        # print('removing...')
                except Exception as e:
                    print(e)
                    pass

        print('******************************')
        print(avail_area)
        print(getsubarea)
        print('******************************')
        if len(avail_area) >= 2 and len(getsubarea) < 2 and self.matched[self.areakey] not in self.cleanAddressStr:
            self.ambiguous_area = True

        # if self.reverse_pattern['road']!=self.matched[self.roadkey]:
        #     self.matched[self.roadkey]=self.reverse_pattern['road']
        if self.reverse_house_pattern == True and self.reverse_pattern['house'] != self.matched[self.housekey]:
            self.matched[self.housekey] = self.reverse_pattern['house']
        if self.reverse_road_pattern == True and self.reverse_pattern['road'] != self.matched[self.roadkey]:
            self.matched[self.roadkey] = self.reverse_pattern['road']
        if self.reverse_goli_pattern == True and self.reverse_pattern['goli'] != self.matched[self.roadkey]:
            self.matched[self.roadkey] = self.reverse_pattern['goli']
        if self.reverse_lane_pattern == True and self.reverse_pattern['lane'] != self.matched[self.roadkey]:
            self.matched[self.roadkey] = self.reverse_pattern['lane']
        if self.reverse_block_pattern == True and self.reverse_pattern['block'] != self.matched[self.blockkey]:
            self.matched[self.blockkey] = self.reverse_pattern['block']
        if self.reverse_sector_pattern == True and self.reverse_pattern['sector'] != self.matched[self.subareakey]:
            if self.matched[self.areakey] == 'mirpur':
                self.reverse_pattern['sector'] = self.reverse_pattern['sector'].replace(
                    'sector', 'section')
                self.matched[self.subareakey] = self.reverse_pattern['sector']
            elif self.matched[self.areakey] == 'uttara':
                self.matched[self.subareakey] = self.reverse_pattern['sector']

        print('------------------------------------------=====================================')
        # print(self.subarea_list_pattern)
        # print(self.get_multiple_area)
        # print(self.get_multiple_subarea)
        s_pattern = []
        if len(self.subarea_list_pattern) > 0:
            for patterns in self.subarea_list_pattern:
                if patterns['subarea'] == self.matched[self.subareakey]:
                    s_pattern = patterns['pattern']
                    self.matched[self.subarea_pattern] = s_pattern
                    break
        # if area has no block remove it though given by address
        # areas_with_block = ['mirpur', 'basundhara', 'banani', 'banasree',
        #                     'aftabnagar', 'khilgaon', 'mohammadpur', 'niketon', 'turag', 'baridhara','lalmatia']
        # if (self.matched[self.areakey] != "" and self.matched[self.areakey] != None and self.matched[self.areakey] not in areas_with_block):
        #     self.matched[self.blockkey] = None
        try:
            if self.matched[self.subarea_pattern][2] != 'H' and self.matched[self.subarea_pattern][2] != 'M':
                self.matched[self.blockkey] = None
        except Exception as e:
            print(e)
            pass
        parsed_addr = {

            'area': self.matched[self.areakey],
            'parsed_house': self.matched[self.housekey],
            'parsed_building_name': self.matched[self.buildingkey],
            'parsed_road': self.matched[self.roadkey],
            'parsed_block': self.matched[self.blockkey],
            'parsed_super_subarea': self.matched[self.ssareakey],
            'parsed_subarea': self.matched[self.subareakey],
            'parsed_area': self.matched[self.areakey],
            'parsed_district': self.matched[self.districtkey],
            'parsed_sub_district': self.matched[self.sub_districtkey],
            'parsed_union': self.matched[self.unionkey],
            'pattern': s_pattern,
        }
        if (self.matched[self.housekey] == None or self.matched[self.housekey] == "") and (self.matched[self.roadkey] == None or self.matched[self.roadkey] == "") and (self.matched[self.blockkey] == None or self.matched[self.blockkey] == ""):
            # print('no addr comp exist')
            ob = {}
            data = self.get_geo_data(
                saveTortnAddr, thana_param, district_param)
            # print(data)
            # fin_addr = self.search_addr_bkoi(data, saveTortnAddr)
            fin_addr = self.matcher_addr_bkoi(data, saveTortnAddr)
            # print(fin_addr)
            self.name_search = fin_addr
            ob['geocoded'] = self.name_search
            ob['input_address'] = saveTortnAddr
            ob['address'] = saveTortnAddr
            ob['parsed_address'] = parsed_addr
            print(ob)
            try:
                ob['confidence_score_percentage'] = int(
                    ob['geocoded']['score'] // ob['geocoded']['match_freq'])
                if ob['confidence_score_percentage'] == 100:
                    ob['confidence_score_percentage'] = 98
                if ob['confidence_score_percentage'] == 0:
                    import similarity
                    score = similarity.bkoi_address_matcher(
                        ob['input_address'], ob['geocoded']['new_address'], ob['input_address'], ob['geocoded']['new_address'])['match percentage']
                    ob['confidence_score_percentage'] = (int(
                        score.strip("%").strip()) // 2)+2
                obT = ReverseTransformer()
                bnAddress = obT.english_to_bangla(ob['address'])
                ob['address_bn'] = bnAddress['address_bn']
                ob['status'] = 'incomplete'
                del ob['geocoded']['score']
                del ob['geocoded']['match_freq']
                del ob['geocoded']['matching_diff']
                del ob['geocoded']['match_fuzzy']
                return ob
            except Exception as e:
                print(e)
                pass

        final_address = self.bind_address()
        self.fixed_addr = final_address

        obj = {

            'status': self.check_address_status(),
            'address': final_address.strip(),
            'geocoded': self.search_addr_bkoi2(final_address, thana_param, district_param),

        }

        unique_area_flag = 0
        unique_area_pattern = ["m(i+|e+)r\s*p(u+|o+)r\s*d[.]*\s*o[.]*\s*h[.]*\s*s", "ka+(j|z)(e+|i+)\s*pa+ra+", "sh*e+(o|w)o*ra+\s*pa+ra+", "ka+(f|ph)r(o+|u+)l", "(i+|e+)bra+h(i+|e+)m\s*p(u+|o+)r", "m(a|u|o)n(i|e+)\s*p(u+|o+)r", "a+gh*a+rgh*a+o*n*", "m(o+a+)gh*ba+(j|z|g)(a+|e+)r", "k(a+|o+)(s|ch)(o+|u+)\s*kh*e+t", "ba+d+a+", "(z|j)(i+|e+)ga+\s*t(a+|o+)la", "(z|j)a+f(a+|o+)*ra+\s*ba+d",
                               "ra+(i*|y*)e*r\s*ba+(z|j|g)(a|e)+r", "b(a+|o+)r(a+|o+|u+)\s*ba+gh*", "sh*(e|a|i)r\s*(e|a)\s*b(a|e)nga*la\s*n(a+|o+)g(a+|o+)re*", "sh*(ya+|a+y|e)mo+l(i+|e+|y)", "k(a+|o+)l+y*a+n\s*p(o+|u+)r", "p(i+|e+)re+r+\s*ba+gh*", "paic*k\s*pa+ra+", "k(o+|u+)r(e+|i+)l+", "(v|bh)a+ta+ra+", "(j|z|g)oa*r\s*sh*a+ha+ra+", "ka+la+\s*(ch|s)a+n*d*\s*p(o+|u+)r", "n(a+|o+)r*d+a+", "gh*o+ra+n"]
        for unique_area in unique_area_pattern:
            if re.search(unique_area.strip(), self.matched[self.areakey].strip().strip(',').strip()) or re.search(unique_area.strip(), self.matched[self.subareakey].strip().strip(',').strip()):
                obj['geocoded'] = self.search_addr_bkoi2_unique(
                    final_address, thana_param, district_param)
                print("considered as unique holding")
                unique_area_flag = 1
                break
        try:
            print('927 ................')
            print('1150')

            # print(self.Check_Confidence_Score(
            # obj['address'], obj['geocoded']['Address']))
            obj['confidence_score_percentage'] = self.Check_Confidence_Score2(
                obj['address'], obj['geocoded']['Address'])
        except Exception as e:
            print('930 ................')
            print(e)
            obj['confidence_score_percentage'] = 2
        if unique_area_flag == 1:
            obj['confidence_score_percentage'] = self.confScore
        obj['input_address'] = saveTortnAddr
        if obj['confidence_score_percentage'] == 100:
            obj['confidence_score_percentage'] = 98
        # try:
        #     obj['latitude'] = obj['geocoded']['latitude']
        #     obj['longitude'] = obj['geocoded']['longitude']
        #     obj['pType'] = obj['geocoded']['pType']
        # except Exception as e:
        #     obj['latitude'] = ''
        #     obj['longitude'] = ''
        #     obj['pType'] = ''
        #     pass

        # del obj['geocoded']

        obj['parsed_address'] = parsed_addr
        obj['address'] = (self.extraHomeKeys.strip().strip(
            ',')+', ' + obj['address']).strip().strip(',').strip()

        # for bangla address
        obT = ReverseTransformer()
        try:

            bnAddress = obT.english_to_bangla(obj['address'])
            obj['address_bn'] = bnAddress['address_bn']
        except Exception as e:
            obj['address_bn'] = obj['address']
        try:
            obj['matched_keys'] = self.GeoTrueFor
        except Exception as e:
            print(e)
            pass
        # try:
        #     if obj['status'] == "incomplete" and obj['confidence_score_percentage'] > 50 or self.ambiguous_area == True:
        #         obj['confidence_score_percentage'] = 20
        # except Exception as e:
        #     print(e)
        #     pass

        self.__init__()

        return obj

    def Check_Confidence_Score2(self, fixedaddr, geoaddr):
        score = 0
        print(self.distance)
        if self.matched[self.subareakey] != None and self.matched[self.subareakey] != '':
            # if self.matched[self.subarea_pattern] == ['H', 'H', 'H', 'L', 'H']:
            if self.matched[self.subarea_pattern][0].strip() == 'H' and self.matched[self.subarea_pattern][1].strip() == 'H' and self.matched[self.subarea_pattern][2].strip() == 'H' and self.matched[self.subarea_pattern][4].strip() == 'H':
                if self.GeoTrueFor['subareakey'] == 1:
                    score += 48
                    if self.GeoTrueFor['blockkey'] == 1:
                        score += 20
                        if self.GeoTrueFor['roadkey'] == 1:
                            score += 18
                            if self.distance >= 0 and self.distance <= 9:
                                score += 14
                            elif self.distance >= 10 and self.distance <= 20:
                                score += 7
                            else:
                                score += 0
                        elif self.GeoTrueFor['roadkey'] == 2 or self.GeoTrueFor['roadkey'] == 3:
                            score += 8
                            if self.distance >= 0 and self.distance <= 9:
                                score += 3
                            elif self.distance >= 10 and self.distance <= 20:
                                score += 2
                            else:
                                score += 0
                        else:
                            score += 0
                            if self.distance >= 0 and self.distance <= 9:
                                score += 2
                            elif self.distance >= 10 and self.distance <= 20:
                                score += 1
                            else:
                                score += 0
                    elif self.GeoTrueFor['blockkey'] != 1:
                        score += 0
                        if self.GeoTrueFor['roadkey'] == 1:
                            score += 2
                            if self.distance >= 0 and self.distance <= 9:
                                score += 2
                            elif self.distance >= 10 and self.distance <= 20:
                                score += 1
                            else:
                                score += 0
                        elif self.GeoTrueFor['roadkey'] == 2 or self.GeoTrueFor['roadkey'] == 3:
                            score += 1
                            if self.distance >= 0 and self.distance <= 9:
                                score += 1
                            elif self.distance >= 10 and self.distance <= 20:
                                score += 1
                            else:
                                score += 0
                        else:
                            score += 0
                            if self.distance >= 0 and self.distance <= 9:
                                score += 1
                            elif self.distance >= 10 and self.distance <= 20:
                                score += 1
                            else:
                                score += 0
                else:
                    score += 0
            # elif self.matched[self.subarea_pattern] == ['H', 'H', 'L', 'L', 'H']:
            elif self.matched[self.subarea_pattern][0].strip() == 'H' and self.matched[self.subarea_pattern][1].strip() == 'H' and self.matched[self.subarea_pattern][4].strip() == 'H':
                if self.GeoTrueFor['subareakey'] == 1:
                    score += 48
                    if self.GeoTrueFor['roadkey'] == 1:
                        score += 38
                        if self.distance >= 0 and self.distance <= 9:
                            score += 14
                        elif self.distance >= 10 and self.distance <= 20:
                            score += 7
                        else:
                            score += 0
                    elif self.GeoTrueFor['roadkey'] == 2 or self.GeoTrueFor['roadkey'] == 3:
                        score += 8
                        if self.distance >= 0 and self.distance <= 9:
                            score += 3
                        elif self.distance >= 10 and self.distance <= 20:
                            score += 2
                        else:
                            score += 0
                    else:
                        score += 0
                        if self.distance >= 0 and self.distance <= 9:
                            score += 2
                        elif self.distance >= 10 and self.distance <= 20:
                            score += 1
                        else:
                            score += 0
                else:
                    score += 0
            # elif self.matched[self.subarea_pattern] == ['H', 'L', 'L', 'L', 'H']:
            elif self.matched[self.subarea_pattern][0].strip() == 'H' and self.matched[self.subarea_pattern][4].strip() == 'H':
                if self.GeoTrueFor['subareakey'] == 1:
                    score += 55
                    if self.distance >= 0 and self.distance <= 6:
                        score += 45
                    elif self.distance >= 7 and self.distance <= 12:
                        score += 23
                    else:
                        score += 0
                else:
                    score += 0
            else:
                score = similarity.bkoi_address_matcher(
                    fixedaddr, geoaddr, fixedaddr, geoaddr)['match percentage']
                score = int(score.strip("%").strip()) // 2
        if score == 0:
            score = similarity.bkoi_address_matcher(
                fixedaddr, geoaddr, fixedaddr, geoaddr)['match percentage']
            return int(score.strip("%").strip())//2
        # self.confScore=round(score)
        score = round(score)
        print('Score---> ' + str(score))
        self.confScore = score
        return score

    def Check_Confidence_Score(self, fixedaddr, geoaddr):
        p = 1
        score = 0
        print(self.matched[self.subarea_pattern])
        print(self.GeoTrueFor)
        if len(self.matched[self.subarea_pattern]) > 0 and len(self.GeoTrueFor) > 0:
            print(self.matched[self.subarea_pattern][4])
            print(self.GeoTrueFor['subareakey'])
            if self.matched[self.subarea_pattern][4].strip() == 'H' and self.GeoTrueFor['subareakey'] == 1:
                score += 50
                if self.matched[self.subarea_pattern][2] == 'H' and self.GeoTrueFor['blockkey'] == 1:
                    score += 30
                    if self.matched[self.subarea_pattern][1] == 'H' and self.GeoTrueFor['roadkey'] == 1:
                        score += 10
                    if self.matched[self.subarea_pattern][1] == 'H' and self.GeoTrueFor['roadkey'] == 2:
                        score += 8
                        if any(map(str.isdigit, self.matched[self.roadkey])):
                            score -= 8
                    if self.matched[self.subarea_pattern][1] == 'H' and self.GeoTrueFor['roadkey'] == 3:
                        score += 4
                    if self.matched[self.subarea_pattern][1] != 'H':
                        score += 10
                        self.GeoTrueFor['roadkey'] = 1
                    if self.matched[self.subarea_pattern][1] == 'H' and self.GeoTrueFor['roadkey'] == 0:
                        self.GeoTrueFor['roadkey'] = 5
                    if self.matched[self.housekey] != "":
                        score += 10-(self.GeoTrueFor['roadkey']*2)
                elif self.matched[self.subarea_pattern][2] == 'H' and self.GeoTrueFor['blockkey'] == 0:
                    score += 0
                    if self.matched[self.subarea_pattern][1] == 'H' and self.GeoTrueFor['roadkey'] == 1:
                        score += 10//2
                    if self.matched[self.subarea_pattern][1] == 'H' and self.GeoTrueFor['roadkey'] == 2:
                        score += 8 // 2
                        if any(map(str.isdigit, self.matched[self.roadkey])):
                            score -= 4
                    if self.matched[self.subarea_pattern][1] == 'H' and self.GeoTrueFor['roadkey'] == 3:
                        score += 4//2
                    if self.matched[self.subarea_pattern][1] != 'H':
                        score += 10//2
                    if self.matched[self.subarea_pattern][1] == 'H' and self.GeoTrueFor['roadkey'] == 0:
                        self.GeoTrueFor['roadkey'] = 5
                    if self.matched[self.housekey] != "":
                        score += 10-(self.GeoTrueFor['roadkey']*2)
                    else:
                        score += 10 - \
                            (self.GeoTrueFor['roadkey']) * \
                            (self.GeoTrueFor['roadkey'])
                elif self.matched[self.subarea_pattern][2] != 'H':
                    score += 30
                    if self.matched[self.subarea_pattern][1] == 'H' and self.GeoTrueFor['roadkey'] == 1:
                        score += 10
                    if self.matched[self.subarea_pattern][1] == 'H' and self.GeoTrueFor['roadkey'] == 2:
                        score += 8
                    if self.matched[self.subarea_pattern][1] == 'H' and self.GeoTrueFor['roadkey'] == 3:
                        score += 4
                    if self.matched[self.subarea_pattern][1] == 'H' and self.GeoTrueFor['roadkey'] == 0:
                        self.GeoTrueFor['roadkey'] = 5
                    if self.matched[self.subarea_pattern][1] != 'H':
                        score += 10
                        self.GeoTrueFor['roadkey'] = 1
                    if self.matched[self.housekey] != "":
                        score += 10-(self.GeoTrueFor['roadkey']*2)

                else:
                    score = score-(self.matched[self.subarea_pattern].count('H')-1)*(
                        self.matched[self.subarea_pattern].count('H')-1)
        if self.matched[self.areakey] == "" and self.matched[self.areakey] == None:
            score = 20
        # print(str(score)+"%")
        if score == 0:
            score = similarity.bkoi_address_matcher(
                fixedaddr, geoaddr, fixedaddr, geoaddr)['match percentage']
            return int(score.strip("%").strip())//2
        # self.confScore=round(score)
        score = round(score)
        return score-3

    def Check_Reverse_Key(self, s):
        house_key = ''
        road_key = ''
        block_key = ''
        sector_key = ''
        goli_key = ''
        # s='oaishf ka/4    no house las, 4 number   road block no 5'
        pattern_house = re.search(
            '(ka)*[a-z]*\d*/*[a-z]*(ka)*\d+\s+(no|number)\s*[.]*\s+house\s+', s)
        pattern_road = re.search(
            '(ka)*[a-z]*\d*/*[a-z]*(ka)*\d+\s+(no|number)\s*[.]*\s+road\s+', s)
        pattern_goli = re.search(
            '(ka)*[a-z]*\d*/*[a-z]*(ka)*\d+\s+(no|number)\s*[.]*\s+goli\s+', s)
        pattern_lane = re.search(
            '(ka)*[a-z]*\d*/*[a-z]*(ka)*\d+\s+(no|number)\s*[.]*\s+lane\s+', s)
        pattern_block = re.search(
            '(ka)*[a-z]*\d*/*[a-z]*(ka)*\d+\s+(no|number)\s*[.]*\s+block\s+', s)
        pattern_sector = re.search(
            '(ka)*[a-z]*\d*/*[a-z]*(ka)*\d+\s+(no|number)\s*[.]*\s+sector\s+', s)
        pattern_road_feet = re.search('\s+\d+\s*(feet|(ft[.]*|foot)\s+)', s)
        if pattern_road_feet:
            road_feet = re.search("\d+", pattern_road_feet.group())
            # print(road_feet.group())
            self.reverse_road_pattern = True
            self.reverse_pattern['road'] = str(road_feet.group())+" feet road"
        if pattern_house:
            house_key = pattern_house.group().split()[0]
            print("house "+house_key)
            self.reverse_house_pattern = True
            self.reverse_pattern['house'] = house_key
        if pattern_road:
            road_key = pattern_road.group().split()[0]
            self.reverse_road_pattern = True
            print("road "+road_key)
            self.reverse_pattern['road'] = "road "+road_key
        if pattern_goli:
            goli_key = pattern_goli.group()
            self.reverse_goli_pattern = True
            print("goli "+goli_key)
            self.reverse_pattern['goli'] = goli_key
        if pattern_lane:
            lane_key = pattern_lane.group().split()[0]
            self.reverse_lane_pattern = True
            print("lane "+lane_key)
            self.reverse_pattern['lane'] = "lane "+lane_key
        if pattern_block:
            block_key = pattern_block.group().split()[0]
            self.reverse_block_pattern = True
            print("block "+block_key)
            self.reverse_pattern['block'] = block_key
        if pattern_sector:
            sector_key = pattern_sector.group().split()[0]
            self.reverse_sector_pattern = True
            print("sector "+sector_key)
            self.reverse_pattern['sector'] = "sector "+sector_key
        return None

    def matcher_addr_bkoi(self, data, qstring):
        similar_addr = []
        mp = MiniParser()
        temp_qstring = qstring.split(' ')
        isAreapoint = 0
        match_address_max = {}
        match_counter_max = -1
        match_obj_max = {}
        numOfmatches = 0
        fuzzy_matches = 0
        geocoded_addr_name_len = 0
        p = 0
        q = 0
        cnt = []
        if self.matched[self.subareakey] == None:
            self.matched[self.subareakey] = ''
        if self.matched[self.areakey] == None:
            self.matched[self.areakey] = ''
        if (self.matched[self.areakey] != '' and self.matched[self.areakey] != None) or (self.matched[self.subareakey] != '' and self.matched[self.subareakey] != None):
            print('this...........area sec')
            check_first = 0
            for i in data:
                match_counter = 0
                fuzzy_match_counter = 0
                geocoded_area = i['area']
                geocoded_area = geocoded_area.strip().lower()
                # geocoded_address_with_area=i['address']+", "+geocoded_area
                geocoded_address_with_area = i['new_address']
                geocoded_addr_comp = mp.parse(
                    geocoded_address_with_area.lower(), i['pType'])
                # print(geocoded_addr_comp)
                # print(geocoded_area)
                geocoded_holding = geocoded_addr_comp['holding'].strip()
                geocoded_holding = re.sub(
                    r'\([^)]*\)', '', geocoded_holding).strip()
                geocoded_subarea = geocoded_addr_comp['subarea'].strip()
                # print('***************** Geo ** ************')
                # print(geocoded_holding)
                # print(geocoded_area)
                # print(geocoded_subarea)
                # print('***************** parsed ** ************')
                # print(self.matched[self.areakey])
                # print(self.matched[self.subareakey])
                # if (geocoded_holding != None or geocoded_holding != '') and geocoded_holding in qstring:
                #     numOfmatches_exact += 1
                #     exact_matched.append(i)
                #     print(qstring)
                #     print(i['new_address'])
                #     exact_check = 1
                #     continue
                # if exact_matched == 1:
                #     continue
                if (geocoded_holding != None or geocoded_holding != '') and ((self.matched[self.areakey] != '' and self.matched[self.areakey] in geocoded_area) or (self.matched[self.areakey] != '' and geocoded_area in self.matched[self.areakey]) or (self.matched[self.subareakey] != '' and self.matched[self.subareakey] in geocoded_subarea) or (self.matched[self.subareakey] != '' and geocoded_subarea in self.matched[self.subareakey]) or (self.matched[self.subareakey] != '' and geocoded_area in self.matched[self.subareakey]) or (self.matched[self.areakey] != '' and geocoded_subarea in self.matched[self.areakey])):
                    qstring = qstring.replace(
                        self.matched[self.areakey], "").strip()
                    if qstring == geocoded_holding:
                        match_counter += len(qstring.strip().split(' '))
                        p = 1
                    for comp in geocoded_holding.split(' '):

                        if comp != '' and (comp in qstring) and p == 0:
                            match_counter += 1
                        elif comp != '' and any(fuzz.ratio(comp, st) >= 80 and st[0] == comp[0] and len(comp) >= 5 for st in temp_qstring) and p == 0:
                            match_counter += 0.5
                            fuzzy_match_counter += 1
                            # print(match_counter)
                    cnt.append(match_counter)
                    if match_counter_max < match_counter:
                        match_counter_max = match_counter
                        match_address_max = i['new_address'].lower()
                        geocoded_addr_name_len = len(
                            geocoded_holding.split(' '))
                        match_obj_max = i
                        p = 1
                    if match_counter_max == match_counter:
                        print(i['new_address'])
                        similar_addr.append(geocoded_holding)

                elif (geocoded_holding != None or geocoded_holding.strip() != ''):
                    if qstring == geocoded_holding:
                        match_counter += len(qstring.strip().split(' '))
                        p = 1
                    elif len(qstring.strip().split(' ')) == 1 and qstring in geocoded_holding:
                        match_counter += 1
                        p = 1
                    for comp in geocoded_holding.split(' '):
                        if p == 0 and comp != '' and (comp in qstring):
                            match_counter += 1
                            # print(match_counter)
                        elif p == 0 and comp != '' and (any(fuzz.ratio(comp, st) >= 80 and st[0] == comp[0] for st in temp_qstring)):
                            match_counter += 0.5
                            fuzzy_match_counter += 1
                    cnt.append(match_counter)
                    if match_counter_max < match_counter:
                        match_counter_max = match_counter
                        match_address_max = i['new_address'].lower()
                        geocoded_addr_name_len = len(
                            geocoded_holding.split(' '))
                        fuzzy_matches = fuzzy_match_counter
                        match_obj_max = i

                        p = 1
                    if match_counter_max == match_counter:
                        # print(i['new_address'])
                        similar_addr.append(geocoded_holding)
        else:
            cnt = []
            for i in data:
                match_counter = 0
                fuzzy_match_counter = 0
                geocoded_area = i['area']
                geocoded_area = geocoded_area.strip().lower()
                # geocoded_address_with_area=i['address']+", "+geocoded_area
                geocoded_address_with_area = i['new_address']
                geocoded_addr_comp = mp.parse(
                    geocoded_address_with_area.lower(), i['pType'])
                # print(geocoded_addr_comp)
                # print(geocoded_area)
                geocoded_holding = geocoded_addr_comp['holding'].strip(
                ).lower()
                geocoded_holding = re.sub(
                    r'\([^)]*\)', '', geocoded_holding).strip()
                geocoded_subarea = geocoded_addr_comp['subarea'].strip(
                ).lower()
                # print('***************** Geo ** ************')
                # print(geocoded_holding)
                # print(geocoded_area)
                # print(geocoded_subarea)
                # print('***************** parsed ** ************')
                # print(self.matched[self.areakey])
                # print(self.matched[self.subareakey])
                print('********************')
                print(geocoded_address_with_area)
                print(geocoded_holding)
                # print(qstring)
                print('********************')
                if (geocoded_holding != None or geocoded_holding.strip() != ''):
                    if qstring == geocoded_holding:
                        match_counter += len(qstring.strip().split(' '))
                        p = 1
                    elif len(qstring.strip().split(' ')) == 1 and qstring in geocoded_holding:
                        match_counter += 1
                        p = 1

                    for comp in geocoded_holding.split(' '):
                        if p == 0 and comp != '' and (comp in qstring):
                            match_counter += 1
                            # print(match_counter)
                        elif p == 0 and comp != '' and (any(fuzz.ratio(comp, st) >= 80 and st[0] == comp[0] for st in temp_qstring)):
                            match_counter += 0.5
                            fuzzy_match_counter += 1
                    cnt.append(match_counter)
                    if match_counter_max < match_counter:
                        match_counter_max = match_counter
                        match_address_max = i['new_address'].lower()
                        geocoded_addr_name_len = len(
                            geocoded_holding.split(' '))
                        fuzzy_matches = fuzzy_match_counter
                        match_obj_max = i

                        p = 1
                    if match_counter_max == match_counter:
                        # print(i['new_address'])
                        similar_addr.append(geocoded_holding)
        # for addr in similar_addr:
        #     print(self.lcs(qstring, addr, len(qstring), len(addr)))
        print('same addr: ')
        print(cnt)
        largest = max(cnt)
        match_obj_max['match_freq'] = cnt.count(largest)
        match_obj_max['matching_diff'] = abs(
            geocoded_addr_name_len - match_counter_max)
        match_obj_max['match_fuzzy'] = fuzzy_matches
        print(match_obj_max['match_fuzzy'])
        match_obj_max['score'] = (
            100*match_counter_max)//geocoded_addr_name_len

        # if len(cnt)>0 and (i==largest or i==0 for i in cnt)
        # if match_obj_max['match_freq'] == 1:
        #     match_obj_max['score'] = 100
        # print(match_obj_max['score'])
        # print(match_obj_max['match_freq'])
        return match_obj_max

    def barikoi_office_search(self, qstring):
        url = "http://elastic.barikoi.com/api/search/autocomplete/exact"
        r = requests.post(url, params={'q': qstring})
        data = r.json()
        final_addr = data[0]
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
        obT = ReverseTransformer()
        obj = {
            "input_address": qstring,
            "address": qstring,
            "address_bn": obT.english_to_bangla(qstring)['address_bn'],
            "confidence_score_percentage": 98,
            "status": "complete"
        }
        obj['geocoded'] = prop_filter
        return obj

    def search_addr_bkoi(self, data, qstring):
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
            i['new_address'] = i['new_address'].lower()
            geo_addr_comp = i['new_address'].split(',')
            i['new_address'] = i['new_address'].strip()
            i['new_address'] = i['new_address'].strip(',')
            if geocoded_area.strip().lower() in qstring or self.matched[self.subareakey] in i['new_address'] or self.matched[self.areakey] in i['new_address']:
                # print("704..................")
                for j, addr_comp in enumerate(geo_addr_comp):
                    # print(addr_comp)
                    if any(match.strip() in addr_comp.strip().lower() for match in qstring.split(',')) or (addr_comp.strip().lower() in qstring and addr_comp.strip().lower() != ''):
                        match_counter = match_counter + 1
                        # print(match_counter)
                if match_counter_max < match_counter:
                    match_counter_max = match_counter
                    match_address_max = i['new_address'].lower()
                    match_obj_max = i
                # print(match_counter_max)
                # print(match_address_max)

            else:
                # print("714..................")
                for j, addr_comp in enumerate(geo_addr_comp):
                    if addr_comp.strip().lower() in qstring:
                        match_counter = match_counter + 1
                if match_counter_max < match_counter:
                    match_counter_max = match_counter
                    match_address_max = i['new_address'].lower()
                    match_obj_max = i

        return match_obj_max

        # result=fuzz.ratio(qstring.lower(), i['Address'].lower())

    def search_addr_bkoi2(self, qstring, thana_param, district_param):
        obj = MiniParser()
        # print(self.matched)
        # print('.....at search..........')
        # print(qstring)
        url = "http://elastic.barikoi.com/api/search/autocomplete/exact"
        # r = requests.post(url, params={'q': qstring, 'thana': thana_param, 'district' : district_param})
        if(thana_param == "yes" and district_param != 'yes'):
            r = requests.post(url, params={'q': qstring, 'thana': thana_param})
        elif(thana_param != "yes" and district_param == 'yes'):
            r = requests.post(
                url, params={'q': qstring, 'district': district_param})
        elif(thana_param == 'yes' and district_param == 'yes'):
            r = requests.post(
                url, params={'q': qstring, 'thana': thana_param, 'district': district_param})
        elif(thana_param != "yes" and district_param != 'yes'):
            r = requests.post(url, params={'q': qstring})

        try:
            datas = r.json()
            # print("got it")
            data = datas
            self.get_geo_obj = data
            pass
        except Exception as e:
            print("Failed to get data...................")
            return {}

        geocoded_addr_comp = ""
        geocoded_holding = None
        geocoded_floor = None
        geocoded_block = ""
        geocoded_subarea = ""
        geocoded_area = ""
        final_addr = ""
        maximum = -1
        maximum_exact = -1
        maximum_exact_b = -1
        holding_dict_exact = {}
        holding_dict_in = {}
        holding_dict_fuzzy = {}
        holding_dict_no_road = {}
        geocoded_address_with_area = ""
        similarity = 0
        mp = MiniParser()
        matched_road_flag = 0
        without_road_maximum = 0
        exact_addr = ''
        gotHoldings = []
        TrueFor = {'housekey': 0, 'roadkey': 0,
                   'blockkey': 0, 'ssareakey': 0, 'subareakey': 0, }
        matched_house_key = self.matched[self.housekey]
        if any(char.isdigit() for char in self.matched[self.housekey]):
            self.matched[self.housekey] = re.findall(
                '\d+', self.matched[self.housekey])[0]
        print('H O U S E Number..........')
        print(self.matched[self.housekey])
        count = 0
        for i in data:
            geocoded_area = i['area']
            geocoded_area = geocoded_area.strip().lower()
            # geocoded_address_with_area=i['address']+", "+geocoded_area
            geocoded_address_with_area = i['new_address']
            geocoded_addr_comp = mp.parse(
                geocoded_address_with_area.lower(), i['pType'])
            # print(geocoded_addr_comp)
            # print(geocoded_area)
            geocoded_holding = geocoded_addr_comp['holding'].strip()
            geocoded_house = geocoded_addr_comp['house'].strip()
            geocoded_floor = geocoded_addr_comp['floor'].strip()
            geocoded_road = geocoded_addr_comp['road'].strip()
            geocoded_block = geocoded_addr_comp['block'].strip()
            geocoded_subarea = geocoded_addr_comp['subarea'].strip()
            # print(geocoded_addr_comp['multiple_subarea'])
            if len(geocoded_addr_comp['multiple_subarea']) >= 2:
                for sarea in geocoded_addr_comp['multiple_subarea']:
                    # print(sarea)
                    if sarea.strip() != geocoded_area.strip() and sarea in geocoded_address_with_area.lower():
                        geocoded_subarea = sarea.strip()
            print(
                '=============================================================================')
            #print('Geocoded Subarea '+geocoded_subarea)
            print(geocoded_address_with_area)
            print(geocoded_area+'    ' +
                  self.matched[self.areakey].strip().strip(',').strip())
            print(geocoded_subarea+'    ' +
                  self.matched[self.subareakey].strip().strip(',').strip())
            holding = ''
            holding = geocoded_house
            if any(char.isdigit() for char in geocoded_house):
                geocoded_house = re.findall('\d+', geocoded_house)[0]
            if (geocoded_area.strip() == self.matched[self.areakey].strip().strip(',').strip() or geocoded_area.strip() == self.matched[self.subareakey].strip().strip(',').strip() or geocoded_subarea.strip() == self.matched[self.areakey].strip().strip(',').strip()) and (geocoded_subarea.lower().strip() == self.matched[self.subareakey].strip().strip(',').strip() or any(self.matched[self.subareakey].strip().strip(',').strip() == subareas.strip().strip(',').strip() for subareas in geocoded_addr_comp['multiple_subarea'])) and self.matched[self.subareakey].strip().strip(',').strip() != '':
                print('when subarea provided................................. ' +
                      self.matched[self.subareakey].strip().strip(',').strip()+' vs '+geocoded_subarea)
                if self.matched[self.blockkey] != "":
                    if self.matched[self.blockkey].strip().strip(',').strip() == geocoded_block:
                        print('when block provided....... '+self.matched[self.blockkey].strip().strip(
                            ',').strip()+' vs '+geocoded_block)
                        if self.matched[self.roadkey].strip().strip(',').strip() == geocoded_road and self.matched[self.roadkey].strip().strip(',').strip() != '':
                            print('when road provided.............. '+self.matched[self.roadkey].strip(
                            ).strip(',').strip()+' vs '+geocoded_road)
                            matched_road_flag = 1
                            similarity = fuzz.ratio(
                                self.matched[self.housekey].strip().strip(',').strip(), geocoded_house)
                            gotHoldings.append(holding)
                            if similarity > maximum_exact_b:
                                final_addr = i
                                exact_addr = i
                                maximum_exact_b = similarity
                                TrueFor['subareakey'] = 1
                                TrueFor['blockkey'] = 1
                                TrueFor['roadkey'] = 1
                                TrueFor['housekey'] = 1
                            holding_dict_exact[holding] = i
                        elif (self.matched[self.roadkey].strip().strip(',').strip() in geocoded_road or geocoded_road in self.matched[self.roadkey].strip().strip(',').strip()) and self.matched[self.roadkey].strip().strip(',').strip() != "" and matched_road_flag == 0 and geocoded_road != "":
                            print('when road not exact.........'+self.matched[self.roadkey].strip().strip(
                                ',').strip()+' vs ' + geocoded_road)
                            similarity = fuzz.ratio(
                                self.matched[self.housekey].strip().strip(',').strip(), geocoded_house)
                            gotHoldings.append(holding)
                            if similarity > maximum:
                                final_addr = i
                                maximum = similarity
                                TrueFor['subareakey'] = 1
                                TrueFor['blockkey'] = 1
                                TrueFor['roadkey'] = 2
                                TrueFor['housekey'] = 1
                            holding_dict_in[holding] = i
                        elif (fuzz.ratio(self.matched[self.roadkey].strip().strip(',').strip(), geocoded_road) > 80) and self.matched[self.roadkey].strip().strip(',').strip() != "" and matched_road_flag == 0 and geocoded_road != "" and not self.hasNumbers(self.matched[self.roadkey].strip().strip(',').strip()):
                            print('road match in fuzzy')
                            similarity = fuzz.ratio(
                                self.matched[self.housekey].strip().strip(',').strip(), geocoded_house)
                            gotHoldings.append(holding)
                            if similarity > maximum:
                                final_addr = i
                                maximum = similarity
                                TrueFor['subareakey'] = 1
                                TrueFor['blockkey'] = 1
                                TrueFor['roadkey'] = 3
                                TrueFor['housekey'] = 1
                            holding_dict_fuzzy[holding] = i
                        elif self.matched[self.roadkey].strip().strip(',').strip() == "" and matched_road_flag == 0:
                            print('road empty')
                            similarity = fuzz.ratio(
                                self.matched[self.housekey].strip().strip(',').strip(), geocoded_house)
                            gotHoldings.append(holding)
                            if similarity > without_road_maximum:
                                final_addr = i
                                without_road_maximum = similarity
                                TrueFor['subareakey'] = 1
                                TrueFor['blockkey'] = 1
                                TrueFor['roadkey'] = 0
                                TrueFor['housekey'] = 1
                            holding_dict_no_road[holding] = i
                if self.matched[self.blockkey] == "":
                    print('when block is empty .............. ' +
                          self.matched[self.blockkey].strip().strip(',').strip()+' vs '+geocoded_block)
                    if self.matched[self.roadkey].strip().strip(',').strip() == geocoded_road and self.matched[self.roadkey].strip().strip(',').strip() != '':
                        print('when road provided ............. '+self.matched[self.roadkey].strip(
                        ).strip(',').strip()+' vs ' + geocoded_road)
                        matched_road_flag = 1
                        similarity_exact = fuzz.ratio(
                            self.matched[self.housekey].strip().strip(',').strip(), geocoded_house)
                        gotHoldings.append(holding)
                        if similarity_exact > maximum_exact:
                            final_addr = i
                            exact_addr = i
                            maximum_exact = similarity_exact

                            TrueFor['subareakey'] = 1
                            TrueFor['blockkey'] = 0
                            TrueFor['roadkey'] = 1
                            TrueFor['housekey'] = 1
                        holding_dict_exact[holding] = i
                    elif (self.matched[self.roadkey].strip().strip(',').strip() in geocoded_road or geocoded_road in self.matched[self.roadkey].strip().strip(',').strip()) and self.matched[self.roadkey].strip().strip(',').strip() != "" and matched_road_flag == 0 and geocoded_road != "":
                        print('when road not exact.............. ' +
                              self.matched[self.roadkey].strip().strip(',').strip()+' vs ' + geocoded_road)
                        similarity = fuzz.ratio(
                            self.matched[self.housekey].strip().strip(',').strip(), geocoded_house)
                        gotHoldings.append(holding)
                        if similarity > maximum:
                            final_addr = i
                            maximum = similarity
                            # print("803...............")
                            # print(geocoded_road)
                            # print(self.matched[self.roadkey].strip().strip(',').strip())
                            TrueFor['subareakey'] = 1
                            TrueFor['blockkey'] = 0
                            TrueFor['roadkey'] = 2
                            TrueFor['housekey'] = 1
                        holding_dict_in[holding] = i
                    elif (fuzz.ratio(self.matched[self.roadkey].strip().strip(',').strip(), geocoded_road) > 80) and self.matched[self.roadkey].strip().strip(',').strip() != "" and matched_road_flag == 0 and geocoded_road != ""and not self.hasNumbers(self.matched[self.roadkey].strip().strip(',').strip()):
                        print('road match in fuzzy............'+self.matched[self.roadkey].strip(
                        ).strip(',').strip()+' vs ' + geocoded_road)
                        similarity = fuzz.ratio(
                            self.matched[self.housekey].strip().strip(',').strip(), geocoded_house)
                        gotHoldings.append(holding)
                        if similarity > maximum:
                            final_addr = i
                            maximum = similarity
                            TrueFor['subareakey'] = 1
                            TrueFor['blockkey'] = 0
                            TrueFor['roadkey'] = 3
                            TrueFor['housekey'] = 1
                        holding_dict_fuzzy[holding] = i
                    elif self.matched[self.roadkey].strip().strip(',').strip() == "" and matched_road_flag == 0:
                        print('road empty')
                        similarity = fuzz.ratio(
                            self.matched[self.housekey].strip().strip(',').strip(), geocoded_house)
                        gotHoldings.append(holding)
                        print("from 1183")
                        count += 1
                        print(count)
                        if similarity > without_road_maximum:
                            final_addr = i
                            without_road_maximum = similarity
                            TrueFor['subareakey'] = 1
                            TrueFor['blockkey'] = 0
                            TrueFor['roadkey'] = 0
                            TrueFor['housekey'] = 1
                        holding_dict_no_road[holding] = i

            elif (geocoded_area.strip() == self.matched[self.areakey].strip().strip(',').strip() and self.matched[self.subareakey].strip().strip(',').strip() == ''):
                print('subarea missing.....................')
                if self.matched[self.blockkey] != "":
                    if self.matched[self.blockkey].strip().strip(',').strip() == geocoded_block:
                        print("got block............ "+self.matched[self.blockkey].strip().strip(
                            ',').strip()+' vs '+geocoded_block)
                        if self.matched[self.roadkey].strip().strip(',').strip() == geocoded_road:
                            print("got road.................... " + self.matched[self.roadkey].strip(
                            ).strip(',').strip()+' vs ' + geocoded_road)
                            matched_road_flag = 1
                            similarity = fuzz.ratio(
                                self.matched[self.housekey].strip().strip(',').strip(), geocoded_house)
                            gotHoldings.append(holding)
                            if similarity > maximum_exact_b:
                                final_addr = i
                                exact_addr = i
                                maximum_exact_b = similarity
                                TrueFor['subareakey'] = 1
                                TrueFor['blockkey'] = 1
                                TrueFor['roadkey'] = 1
                                TrueFor['housekey'] = 1
                            holding_dict_exact[holding] = i
                        elif (self.matched[self.roadkey].strip().strip(',').strip() in geocoded_road or geocoded_road in self.matched[self.roadkey].strip().strip(',').strip()) and geocoded_road != "" and matched_road_flag == 0:
                            print('didnt got road exact............' + self.matched[self.roadkey].strip(
                            ).strip(',').strip()+' vs ' + geocoded_road)
                            similarity = fuzz.ratio(
                                self.matched[self.housekey].strip().strip(',').strip(), geocoded_house)
                            gotHoldings.append(holding)
                            if similarity > maximum:
                                final_addr = i
                                maximum = similarity
                                TrueFor['subareakey'] = 1
                                TrueFor['blockkey'] = 1
                                TrueFor['roadkey'] = 2
                                TrueFor['housekey'] = 1
                            holding_dict_in[holding] = i
                        elif (fuzz.ratio(self.matched[self.roadkey].strip().strip(',').strip(), geocoded_road) > 80) and geocoded_road != "" and matched_road_flag == 0 and not self.hasNumbers(self.matched[self.roadkey].strip().strip(',').strip()):
                            print('road match in fuzzy............'+self.matched[self.roadkey].strip(
                            ).strip(',').strip()+' vs ' + geocoded_road)
                            similarity = fuzz.ratio(
                                self.matched[self.housekey].strip().strip(',').strip(), geocoded_house)
                            gotHoldings.append(holding)
                            if similarity > maximum:
                                final_addr = i
                                maximum = similarity
                                TrueFor['subareakey'] = 1
                                TrueFor['blockkey'] = 1
                                TrueFor['roadkey'] = 3
                                TrueFor['housekey'] = 1
                            holding_dict_fuzzy[holding] = i
                        elif self.matched[self.roadkey].strip().strip(',').strip() == "" and matched_road_flag == 0:
                            print('road empty')
                            similarity = fuzz.ratio(
                                self.matched[self.housekey].strip().strip(',').strip(), geocoded_house)
                            gotHoldings.append(holding)
                            if similarity > without_road_maximum:
                                final_addr = i
                                without_road_maximum = similarity
                                TrueFor['subareakey'] = 1
                                TrueFor['blockkey'] = 1
                                TrueFor['roadkey'] = 0
                                TrueFor['housekey'] = 1
                            holding_dict_no_road[holding] = i
                if self.matched[self.blockkey] == "":
                    print("when block is empty.......... " +
                          self.matched[self.blockkey].strip().strip(',').strip()+' vs '+geocoded_block)
                    print(geocoded_road)
                    if self.matched[self.roadkey].strip().strip(',').strip() == geocoded_road:
                        print('got road............' + self.matched[self.roadkey].strip().strip(
                            ',').strip()+' vs ' + geocoded_road)
                        matched_road_flag = 1
                        similarity_exact = fuzz.ratio(
                            self.matched[self.housekey].strip().strip(',').strip(), geocoded_house)
                        gotHoldings.append(holding)
                        if similarity_exact > maximum_exact:
                            final_addr = i
                            exact_addr = i
                            maximum_exact = similarity_exact
                            TrueFor['subareakey'] = 1
                            TrueFor['blockkey'] = 0
                            TrueFor['roadkey'] = 1
                            TrueFor['housekey'] = 1
                        holding_dict_exact[holding] = i
                        # print("797...............")
                    elif (self.matched[self.roadkey].strip().strip(',').strip() in geocoded_road or geocoded_road in self.matched[self.roadkey].strip().strip(',').strip()) and geocoded_road != "" and matched_road_flag == 0:
                        print('didnt got road exact................ ' +
                              self.matched[self.roadkey].strip().strip(',').strip()+' vs ' + geocoded_road)
                        similarity = fuzz.ratio(
                            self.matched[self.housekey].strip().strip(',').strip(), geocoded_house)
                        gotHoldings.append(holding)
                        if similarity > maximum:
                            final_addr = i
                            maximum = similarity
                            # print("803...............")
                            # print(geocoded_road)
                            # print(self.matched[self.roadkey].strip().strip(',').strip())
                            TrueFor['subareakey'] = 1
                            TrueFor['blockkey'] = 0
                            TrueFor['roadkey'] = 2
                            TrueFor['housekey'] = 1
                        holding_dict_in[holding] = i

                    elif (fuzz.ratio(self.matched[self.roadkey].strip().strip(',').strip(), geocoded_road) > 80) and geocoded_road != "" and self.matched[self.roadkey].strip().strip(',').strip() != "" and matched_road_flag == 0 and not self.hasNumbers(self.matched[self.roadkey].strip().strip(',').strip()):
                        print('road match in fuzzy............'+self.matched[self.roadkey].strip(
                        ).strip(',').strip()+' vs ' + geocoded_road)
                        similarity = fuzz.ratio(
                            self.matched[self.housekey].strip().strip(',').strip(), geocoded_house)
                        gotHoldings.append(holding)
                        if similarity > maximum:
                            final_addr = i
                            maximum = similarity
                            TrueFor['subareakey'] = 1
                            TrueFor['blockkey'] = 0
                            TrueFor['roadkey'] = 3
                            TrueFor['housekey'] = 1
                        holding_dict_fuzzy[holding] = i
                    elif self.matched[self.roadkey].strip().strip(',').strip() == "" and matched_road_flag == 0:
                        print('road empty')
                        similarity = fuzz.ratio(
                            self.matched[self.housekey].strip().strip(',').strip(), geocoded_house)
                        gotHoldings.append(holding)
                        if similarity > without_road_maximum:
                            final_addr = i
                            without_road_maximum = similarity
                            TrueFor['subareakey'] = 1
                            TrueFor['blockkey'] = 0
                            TrueFor['roadkey'] = 0
                            TrueFor['housekey'] = 1
                        holding_dict_no_road[holding] = i
        distance = 1000
        exact_addr = 0
        in_addr = 0
        fuzzy_addr = 0
        no_road_addr = 0
        search_addr = [{}, 1000]
        if matched_house_key.strip().strip(',').strip() != '' and matched_house_key.strip().strip(',').strip() != None and len(holding_dict_exact) > 0:
            search_addr = self.bkoi_search_holding(
                matched_house_key.strip().strip(',').strip(), holding_dict_exact)
            print("search .....")
            print(search_addr)
            ChangedAddr = ''
            if len(search_addr[0]) != 0:
                final_addr = search_addr[0]
                distance = search_addr[1]
                if distance < 6 and distance >= 1:
                    try:
                        ChangedAddr = final_addr['new_address'].lower().split(
                            mp.parse(final_addr['new_address'].lower().strip(), 'residential')['house'])[1]
                    except Exception as e:
                        print(e)
                        ChangedAddr = ''
                    if ChangedAddr != '' and ChangedAddr != None:
                        final_addr['new_address'] = str('house ' +
                                                        self.matched[self.housekey])+str(ChangedAddr)
                print('changing....')
                print(ChangedAddr)
                exact_addr = 1
                if distance < 6 and distance >= 1:
                    # TrueFor['subareakey'] = 1
                    # TrueFor['blockkey'] = 1
                    TrueFor['roadkey'] = 1
                    TrueFor['housekey'] = 1
                if distance >= 6:
                    # TrueFor['subareakey'] = 1
                    # TrueFor['blockkey'] = 1
                    TrueFor['roadkey'] = 3
                    TrueFor['housekey'] = 1
                # print('exactttttttttttttttttttttttttttttttttttttttttttttttt')
        if matched_house_key.strip().strip(',').strip() != '' and matched_house_key.strip().strip(',').strip() != None and len(holding_dict_in) > 0 and exact_addr == 0:
            search_addr = self.bkoi_search_holding(
                matched_house_key.strip().strip(',').strip(), holding_dict_in)
            if len(search_addr[0]) != 0:
                final_addr = search_addr[0]
                distance = search_addr[1]
                in_addr = 1
                # TrueFor['subareakey'] = 1
                # TrueFor['blockkey'] = 1
                TrueFor['roadkey'] = 2
                TrueFor['housekey'] = 1
        if matched_house_key.strip().strip(',').strip() != '' and matched_house_key.strip().strip(',').strip() != None and len(holding_dict_fuzzy) > 0 and exact_addr == 0 and in_addr == 0:
            search_addr = self.bkoi_search_holding(
                matched_house_key.strip().strip(',').strip(), holding_dict_fuzzy)
            if len(search_addr[0]) != 0:
                final_addr = search_addr[0]
                distance = search_addr[1]
                fuzzy_addr = 1
                # print('innnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn')
                # TrueFor['subareakey'] = 1
                # TrueFor['blockkey'] = 1
                TrueFor['roadkey'] = 3
                TrueFor['housekey'] = 1
        if matched_house_key.strip().strip(',').strip() != '' and matched_house_key.strip().strip(',').strip() != None and len(holding_dict_no_road) > 0 and exact_addr == 0 and in_addr == 0 and fuzzy_addr == 0:
            search_addr = self.bkoi_search_holding(
                matched_house_key.strip().strip(',').strip(), holding_dict_no_road)
            if len(search_addr[0]) != 0:
                final_addr = search_addr[0]
                distance = search_addr[1]
                self.distance = distance
                no_road_addr = 1
                # print('fuzyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy')
                # TrueFor['subareakey'] = 1
                # TrueFor['blockkey'] = 1
                TrueFor['roadkey'] = 0
                TrueFor['housekey'] = 1
        # print(final_addr)
        self.matched[self.housekey] = matched_house_key
        if self.matched[self.subareakey] == '' or self.matched[self.subareakey] == None:
            TrueFor['subareakey'] = 0
        if self.matched[self.blockkey] == '' or self.matched[self.blockkey] == None:
            TrueFor['blockkey'] = 0
        if self.matched[self.roadkey] == '' or self.matched[self.roadkey] == None:
            TrueFor['roadkey'] = 0
        if self.matched[self.housekey] == '' or self.matched[self.housekey] == None:
            TrueFor['housekey'] = 0
        self.GeoTrueFor = TrueFor
        if exact_addr == 0 and in_addr == 0 and fuzzy_addr == 0 and no_road_addr == 0:
            self.GeoTrueFor = TrueFor
            print(gotHoldings)
            print(len(gotHoldings))
            if matched_road_flag == 1:
                final_addr = exact_addr
                self.GeoTrueFor = TrueFor
        print('ppppppp')
        print(self.GeoTrueFor)
        print(distance)
        print(final_addr)
        self.distance = distance
        if final_addr == "" or final_addr == None or final_addr == 0:
            print("from prev 1")
            # print(self.matched)
            final_addr = self.search_addr_bkoi(data, qstring)
            try:
                if self.fixed_addr != '':
                    import similarity
                    score = similarity.bkoi_address_matcher(
                        self.fixed_addr, final_addr['new_address'], self.fixed_addr, final_addr['new_address'])['match percentage']
                    self.confScore = int(score.strip("%").strip()) // 2
            except Exception as e:
                print(e)
                pass

        thana_value = None
        try:
            thana_value = final_addr['thana']

        except Exception as e:
            thana_value = None

        district_value = None
        try:
            district_value = final_addr['district']

        except Exception as e:
            district_value = None
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
            return {}
        if thana_param == "yes":
            prop_filter['thana'] = thana_value

        if district_param == "yes":
            prop_filter['district'] = district_value

        return prop_filter
    # to search exact holding or the nearest one

    def bkoi_search_holding(self, house, house_dict):
        match = {}
        least = 1000
        if house in house_dict:
            match = house_dict[house]
            least = 0

        else:
            house = house.replace("-", "/")
            if house in house_dict:
                match = house_dict[house]
                least = 0

            else:
                digits = re.findall("\d+", house)
                digit = digits[0]
                for h in house_dict:
                    result = re.findall("\d+", h)
                    if len(result) > 0:
                        diff = abs(int(digit) - int(result[0]))
                        if diff < least:
                            least = diff
                            match = house_dict[h]

        # print(match)
        return [match, least]

    def search_addr_bkoi2_unique(self, qstring, thana_param, district_param):
        obj = MiniParser()
        # print(self.matched)
        # print('.....at search..........')
        # print(qstring)
        # url = "http://elastic.barikoi.com/api/search/autocomplete/exact"
        # # r = requests.post(url, params={'q': qstring, 'thana': thana_param, 'district' : district_param})
        # if(thana_param == "yes" and district_param != 'yes'):
        #     r = requests.post(url, params={'q': qstring, 'thana': thana_param})
        # elif(thana_param != "yes" and district_param == 'yes'):
        #     r = requests.post(
        #         url, params={'q': qstring, 'district': district_param})
        # elif(thana_param == 'yes' and district_param == 'yes'):
        #     r = requests.post(
        #         url, params={'q': qstring, 'thana': thana_param, 'district': district_param})
        # elif(thana_param != "yes" and district_param != 'yes'):
        #     r = requests.post(url, params={'q': qstring})

        # try:
        #     datas = r.json()
        #     # print("got it")
        #     data = datas
        #     pass
        # except Exception as e:
        #     print("Failed to get data...................")
        #     return {}
        if len(self.get_geo_obj) == 0:
            return {}
        datas = self.get_geo_obj
        data = datas

        unique_area_pattern = ["m(i+|e+)r\s*p(u+|o+)r\s*d[.]*\s*o[.]*\s*h[.]*\s*s", "ka+(j|z)(e+|i+)\s*pa+ra+", "sh*e+(o|w)o*ra+\s*pa+ra+", "ka+(f|ph)r(o+|u+)l", "(i+|e+)bra+h(i+|e+)m\s*p(u+|o+)r", "m(a|u|o)n(i|e+)\s*p(u+|o+)r", "a+gh*a+rgh*a+o*n*", "m(o+a+)gh*ba+(j|z|g)(a+|e+)r", "k(a+|o+)(s|ch)(o+|u+)\s*kh*e+t", "ba+d+a+", "(z|j)(i+|e+)ga+\s*t(a+|o+)la", "(z|j)a+f(a+|o+)*ra+\s*ba+d",
                               "ra+(i*|y*)e*r\s*ba+(z|j|g)(a|e)+r", "b(a+|o+)r(a+|o+|u+)\s*ba+gh*", "sh*(e|a|i)r\s*(e|a)\s*b(a|e)nga*la\s*n(a+|o+)g(a+|o+)re*", "sh*(ya+|a+y|e)mo+l(i+|e+|y)", "k(a+|o+)l+y*a+n\s*p(o+|u+)r", "p(i+|e+)re+r+\s*ba+gh*", "paic*k\s*pa+ra+", "k(o+|u+)r(e+|i+)l+", "(v|bh)a+ta+ra+", "(j|z|g)oa*r\s*sh*a+ha+ra+", "ka+la+\s*(ch|s)a+n*d*\s*p(o+|u+)r", "n(a+|o+)r*d+a+", "gh*o+ra+n"]
        geocoded_addr_comp = ""
        geocoded_holding = None
        geocoded_floor = None
        geocoded_block = ""
        geocoded_subarea = ""
        geocoded_area = ""
        final_addr = ""
        maximum = -1
        maximum_exact = -1
        maximum_exact_b = -1
        geocoded_address_with_area = ""
        similarity = 0
        mp = MiniParser()
        matched_road_flag = 0
        without_road_maximum = 0
        exact_addr = ''
        gotHoldings = []
        holding_dict = {}
        TrueFor = {'housekey': 0, 'roadkey': 0,
                   'blockkey': 0, 'ssareakey': 0, 'subareakey': 0, }
        matched_house_key = self.matched[self.housekey]
        if any(char.isdigit() for char in self.matched[self.housekey]):
            self.matched[self.housekey] = re.findall(
                '\d+', self.matched[self.housekey])[0]
        print('H O U S E Number..........')
        print(self.matched[self.housekey])
        count = 0
        for i in data:
            geocoded_area = i['area']
            geocoded_area = geocoded_area.strip().lower()
            # geocoded_address_with_area=i['address']+", "+geocoded_area
            geocoded_address_with_area = i['new_address']
            geocoded_addr_comp = mp.parse(
                geocoded_address_with_area.lower(), i['pType'])

            # print(geocoded_area)
            geocoded_holding = geocoded_addr_comp['holding'].strip()
            geocoded_house = geocoded_addr_comp['house'].strip()
            geocoded_floor = geocoded_addr_comp['floor'].strip()
            geocoded_road = geocoded_addr_comp['road'].strip()
            geocoded_block = geocoded_addr_comp['block'].strip()
            geocoded_subarea = geocoded_addr_comp['subarea'].strip()
            # print(geocoded_addr_comp['multiple_subarea'])
            if len(geocoded_addr_comp['multiple_subarea']) >= 2:
                for sarea in geocoded_addr_comp['multiple_subarea']:
                    # print(sarea)
                    if sarea.strip() != geocoded_area.strip() and sarea in geocoded_address_with_area.lower():
                        geocoded_subarea = sarea.strip()
            print(
                '=============================================================================')
            print(geocoded_addr_comp)
            print(geocoded_address_with_area)
            print(geocoded_area+'  vsa  ' +
                  self.matched[self.areakey].strip().strip(',').strip())
            print(geocoded_subarea+'  vss  ' +
                  self.matched[self.subareakey].strip().strip(',').strip())
            holding = ''
            holding = geocoded_house
            if any(char.isdigit() for char in geocoded_house):
                geocoded_house = re.findall('\d+', geocoded_house)[0]
            # if (geocoded_area.strip()==self.matched[self.areakey].strip().strip(',').strip() or geocoded_area.strip()==self.matched[self.subareakey].strip().strip(',').strip()  or geocoded_subarea.strip()==self.matched[self.areakey].strip().strip(',').strip()  ) and (geocoded_subarea.lower().strip()== self.matched[self.subareakey].strip().strip(',').strip() or any(self.matched[self.subareakey].strip().strip(',').strip()== subareas.strip().strip(',').strip() for subareas in  geocoded_addr_comp['multiple_subarea'] )) and self.matched[self.subareakey].strip().strip(',').strip()!='':
            if (((geocoded_area.strip() == self.matched[self.areakey].strip().strip(',').strip() and geocoded_subarea.strip() == self.matched[self.subareakey].strip().strip(',').strip()) or geocoded_area.strip() in self.matched[self.subareakey].strip().strip(',').strip() or geocoded_subarea.strip() in self.matched[self.areakey].strip().strip(',').strip()) or (geocoded_subarea.lower().strip() in self.matched[self.subareakey].strip().strip(',').strip() or any(self.matched[self.subareakey].strip().strip(',').strip() in subareas.strip().strip(',').strip() for subareas in geocoded_addr_comp['multiple_subarea']))) and (self.matched[self.subareakey].strip().strip(',').strip() != ''and self.matched[self.subareakey].strip().strip(',').strip() != None and geocoded_area.strip().lower() != '' and geocoded_area != None and geocoded_subarea.strip().lower() != "" and geocoded_subarea != None) and ((re.search(unique_area_p.strip(), self.matched[self.areakey].strip().strip(',').strip()) or re.search(unique_area_p.strip(), self.matched[self.subareakey].strip().strip(',').strip()) for unique_area_p in unique_area_pattern)):
                print(self.matched[self.subareakey].strip().strip(',').strip())
                similarity = fuzz.ratio(
                    self.matched[self.housekey].strip().strip(',').strip(), geocoded_house)
                print(self.matched[self.housekey].strip().strip(
                    ',').strip() + "  and  "+geocoded_house)
                gotHoldings.append(holding)
                print("holding matched result")
                print(similarity)
                if similarity > maximum_exact_b:
                    final_addr = i
                    exact_addr = i
                    maximum_exact_b = similarity
                    TrueFor['subareakey'] = 1
                    TrueFor['blockkey'] = 1
                    TrueFor['roadkey'] = 1
                    TrueFor['housekey'] = 1
                holding_dict[holding] = i

            elif (geocoded_area.strip() == self.matched[self.areakey].strip().strip(',').strip() and self.matched[self.subareakey].strip().strip(',').strip() == ''):
                similarity = fuzz.ratio(
                    self.matched[self.housekey].strip().strip(',').strip(), geocoded_house)
                gotHoldings.append(holding)

                if similarity > maximum_exact_b:
                    final_addr = i
                    exact_addr = i
                    maximum_exact_b = similarity
                    TrueFor['subareakey'] = 1
                    TrueFor['blockkey'] = 1
                    TrueFor['roadkey'] = 1
                    TrueFor['housekey'] = 1
                    TrueFor['housekey'] = 1
                holding_dict[holding] = i
        # holding compare
        distance = 1000
        search_addr = [{}, 1000]
        if matched_house_key.strip().strip(',').strip() != '' and matched_house_key.strip().strip(',').strip() != None and len(holding_dict) > 0:
            search_addr = self.bkoi_search_holding(
                matched_house_key.strip().strip(',').strip(), holding_dict)
            #print("search .....")
            # print(search_addr)
            ChangedAddr = ''
            if len(search_addr[0]) != 0:
                final_addr = search_addr[0]
                distance = search_addr[1]
                print(distance)
                if distance < 6 and distance >= 0:
                    self.confScore = 95
                    if distance < 6 and distance >= 1:
                        try:
                            ChangedAddr = final_addr['new_address'].lower().split(
                                mp.parse(final_addr['new_address'].lower().strip(), 'residential')['house'])[1]
                        except Exception as e:
                            print(e)
                            ChangedAddr = ''
                        if ChangedAddr != '' and ChangedAddr != None:
                            final_addr['new_address'] = str('house ' +
                                                            self.matched[self.housekey])+str(ChangedAddr)
                    print('changing....')
                elif distance < 11 and distance > 5:
                    self.confScore = 80
                elif distance < 21 and distance > 10:
                    self.confScore = 50
                else:
                    self.confScore = 15

        if final_addr == "" or final_addr == None or final_addr == 0:
            print("from prev 1")
            print('2316......')
            # print(self.matched)
            final_addr = self.search_addr_bkoi(data, qstring)
        self.matched[self.housekey] = matched_house_key
        thana_value = None
        try:
            thana_value = final_addr['thana']

        except Exception as e:
            thana_value = None

        district_value = None
        try:
            district_value = final_addr['district']

        except Exception as e:
            district_value = None
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
            if self.fixed_addr != '':
                import similarity
                score = similarity.bkoi_address_matcher(
                    self.fixed_addr, final_addr['new_address'], self.fixed_addr, final_addr['new_address'])['match percentage']
                self.confScore = int(score.strip("%").strip())//2
        except Exception as e:
            print(e)
            return {}
        if thana_param == "yes":
            prop_filter['thana'] = thana_value

        if district_param == "yes":
            prop_filter['district'] = district_value

        return prop_filter

    def get_geo_data(self, qstring, thana_param, district_param):

        url = "http://elastic.barikoi.com/api/search/autocomplete/exact"
        # r = requests.post(url, params={'q': qstring, 'thana': thana_param, 'district' : district_param})
        if(thana_param == "yes" and district_param != 'yes'):
            r = requests.post(url, params={'q': qstring, 'thana': thana_param})
        elif(thana_param != "yes" and district_param == 'yes'):
            r = requests.post(
                url, params={'q': qstring, 'district': district_param})
        elif(thana_param == 'yes' and district_param == 'yes'):
            r = requests.post(
                url, params={'q': qstring, 'thana': thana_param, 'district': district_param})
        elif(thana_param != "yes" and district_param != 'yes'):
            r = requests.post(url, params={'q': qstring})

        try:
            data = r.json()
            return data
        except Exception as e:
            print("Failed to get data...................")
            return {}

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
            self.matched[self.housekey] = self.matched[self.housekey].strip(
                '-')
            if any(char.isdigit() for char in self.matched[self.housekey]):
                self.matched[self.housekey] = "house " + \
                    self.matched[self.housekey]+", "
            else:
                self.matched[self.housekey] = ''
        except Exception as e:
            self.matched[self.housekey] = ''

        try:
            self.matched[self.roadkey] = self.matched[self.roadkey]+", "
        except Exception as e:
            self.matched[self.roadkey] = ''
        try:
            self.matched[self.blockkey] = "block " + \
                self.matched[self.blockkey]+", "
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
            if (self.matched[self.areakey] == None or self.matched[self.areakey] == ''):
                self.matched[self.unionkey] = self.matched[self.unionkey]+", "
            else:
                self.matched[self.unionkey] = ''
        except Exception as e:
            self.matched[self.unionkey] = ''

        try:
            if (self.matched[self.areakey] == None or self.matched[self.areakey] == ''):
                self.matched[self.sub_districtkey] = self.matched[self.sub_districtkey]+", "
            else:
                self.matched[self.sub_districtkey] = ''
        except Exception as e:
            self.matched[self.sub_districtkey] = ''

        try:
            if (self.matched[self.areakey] == None or self.matched[self.areakey] == ''):
                self.matched[self.districtkey] = self.matched[self.districtkey]+","
            else:
                self.matched[self.districtkey] = ''
        except Exception as e:
            self.matched[self.districtkey] = ''
        # print(self.matched)
        # print('887-------------------------------------'+ self.matched[self.buildingkey].strip().replace(',','').strip()+'-----------'+self.matched[self.roadkey].strip(','))
        # if self.matched[self.roadkey].strip().replace('road','').replace(',','').strip() in self.matched[self.buildingkey] and self.matched[self.buildingkey]!= '' and self.matched[self.roadkey]!='':
        #     self.matched[self.buildingkey]=self.matched[self.buildingkey].replace(self.matched[self.roadkey].strip().replace('road','').replace(',','').strip(),'')
        # print(self.matched[self.subareakey].strip().replace(',','').strip())

        if (self.matched[self.buildingkey].lstrip(' ,').rstrip(' , ') in self.matched[self.roadkey].lstrip(' ,').rstrip(' , ') and self.matched[self.buildingkey].lstrip(' ,').rstrip(' , ') != '' and self.matched[self.roadkey].lstrip(' ,').rstrip(' , ') != '') or(self.matched[self.subareakey].lstrip(' ,').rstrip(' , ') == self.matched[self.buildingkey].lstrip(' ,').rstrip(' , ') and self.matched[self.subareakey].lstrip(' ,').rstrip(' , ') != '' and self.matched[self.buildingkey].lstrip(' ,').rstrip(' , ') != ''):
            # print('977 =------------ ')
            self.matched[self.buildingkey] = ''
            # print("905-------------------------")
        # self.matched[self.buildingkey]=self.matched[self.buildingkey].strip()
        if self.matched[self.subareakey] == self.matched[self.areakey]:
            # print('982......same AS')
            print(self.matched)
            full_address = self.matched[self.buildingkey] + self.matched[self.housekey] + self.matched[self.roadkey] + self.matched[self.blockkey] + \
                self.matched[self.areakey] + self.matched[self.unionkey] + \
                self.matched[self.sub_districtkey] + \
                self.matched[self.districtkey]
        else:
            full_address = self.matched[self.buildingkey] + self.matched[self.housekey] + self.matched[self.roadkey] + self.matched[self.blockkey] + \
                self.matched[self.subareakey] + self.matched[self.areakey] + self.matched[self.unionkey] + \
                self.matched[self.sub_districtkey] + \
                self.matched[self.districtkey]

        full_address = full_address.lstrip(' ,')
        full_address = full_address.rstrip(' ,')
        # print("990--------------------")
        # print(self.matched)
        # print(self.get_multiple_area)
        # print(self.get_multiple_subarea)
        # print(len(self.matched_array))
        if len(self.matched_array) < 1:
            # print("913...........................")
            full_address = self.clone_input_address.lstrip().rstrip()
        # print('......................................1090')
        # print(self.tempArray)
        # print(self.matched)

        return full_address


# Flask App.................................
