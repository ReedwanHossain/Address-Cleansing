# import modules.......................
import re
import nltk
import csv
from nltk.tokenize import sent_tokenize, word_tokenize

with open('./chaldal.csv','rt')as f:
    test_data = csv.reader(f)
    for t, td in enumerate(test_data):
        input_address = td[0]
        # input_address = raw_input('Enter Address: ')
        print 'input address'
        print input_address+"\n"



        # initializaion............................
        namekey = 'name'
        housekey = 'House'
        roadkey = 'road'
        ssareakey = 'supersubarea'
        subareakey = 'subarea'
        areakey = 'area'
        house_nokey = 'house_no'
        road_idkey = 'road_id'
        area_idkey = 'area_id'
        subarea_idkey = 'subarea_id'
        supersubarea_idkey = 'supersubarea_id'
        # flags.......................
        area_flag = False
        area_pos = 0
        subarea_flag = False
        subarea_pos = 0
        matched = {}

        prefix_dict = ['', 'east', 'west', 'north', 'south', 'middle', 'purba', 'poschim', 'uttar', 'dakshin', 'moddho']

        address_component = ['', 'house', 'road', 'block', 'section', 'sector', 'avenue']

        # pre-processing.......................

        def multiple_replace(dict, text):
          # Create a regular expression  from the dictionary keys
          regex = re.compile("(%s)" % "|".join(map(re.escape, dict.keys())))
          # For each match, look-up corresponding value in dictionary
          return regex.sub(lambda mo: dict[mo.string[mo.start():mo.end()]], text) 

        rep2 = {
                    "rd#": " road ", "rd-": " road  ", "rd:": " road  ", "h#": " house ", "h-": " house ", "h:": " house ",
                    "bl-":" block ","bl#":" block ", "bl:":" block ", 'sec-': ' section ','sec#': ' section ', 'sec:': ' section ',
                    'house': ' house ', 'house:': ' house ', 'road': ' road ', 'road:': ' road ', 'block-': ' block ', 'block:': ' block ', 'section': ' section ','section:': ' section ',
                    'ave-': ' avenue ', 'ave:': ' avenue ', 'ave#': ' avenue ','ave:': ' avenue '
                } 
        area_dict = {"mirpur": " mirpur ", "uttara": " uttara ", "banani": " banani ", "mohammadpur": " mohammadpur ", "gulshan": " gulshan ", "baridhara": " baridhara ",} # define desired replacements here
        expand = multiple_replace(rep2, input_address.lower())
        expand = multiple_replace(area_dict, expand.lower())
        print "Tokenize"
        print word_tokenize(expand)
        print('\n')
        addresscomponents = word_tokenize(expand)



        tempArray = []
        for i, comp in enumerate(addresscomponents):
                comp=comp.strip()
                if comp == "," or comp == "":
                    continue
               
                temp = comp.lstrip('[0:!@#$-]')
                temp = temp.rstrip('[:!@#$-]')
                temp = temp.strip(" ");
                if(temp != ""):
                    tempArray.append(temp)
                # print comp.rstrip('[!@#$-]')
        print "final pre-processing "
        print(tempArray)
        cleanAddressStr = ' '.join(tempArray)
        print "\n"

        tempObjArray = []
        for i, comp in enumerate(tempArray):
            obj = {
                'id' : i,
                'name' : comp,
                'is_visited' : False,
            }
            tempObjArray.append(obj)
       

        def check_area(token, idx):
            area_token = multiple_replace(area_dict, token.lower())
            area_token = word_tokenize(area_token)
            with open('./area-list.csv','rt')as f:
              area_list = csv.reader(f)
              for j, area in enumerate(area_list):

                    if (area_token[0].lower().strip() == area[0].lower()):
                        matched[areakey] = area[0].lower()
                        global area_pos, area_flag
                        area_flag = True 
                        area_pos = idx
                        for i, comp in enumerate(tempArray):
                            tempObjArray[i]['is_visited'] = True
                            check_sub_area(comp, i)
                            continue

                        return True



        def check_sub_area(token, idx):
            if area_flag== True:
                # todo
                global area_pos
                area = matched[areakey].lower()
                if (idx-area_pos == 1 and any(char.isdigit() for char in tempArray[idx])):
                    
                    if(area.lower() == 'mirpur'):
                        token = 'section '+ tempArray[idx]

                    elif(area.lower() == 'uttara'):
                        token = 'sector '+ tempArray[idx]
                    
                    with open('./subarea-list.csv','rt')as f:
                        subarea_list = csv.reader(f)
                        for j, subarea in enumerate(subarea_list):
                            if (area.lower() == subarea[0].lower() and token.lower() == subarea[1].lower()):
                                matched[subareakey] = token.lower()
                                subarea_flag = True
                                return True

                if(abs(idx-area_pos) > 1 or abs(idx-area_pos) == 1 and not any(char.isdigit() for char in tempArray[idx])):
                    global cleanAddressStr
                    token = token.lstrip('[0:!@#$-]')
                    token = token.rstrip('[:!@#$-]')
                    prefix_flag = False
                    # if idx != tempArray.count:   
                    # for k, prefix in enumerate(prefix_dict):
                    #     pre_token = prefix + ' ' + token
                    #     if pre_token in cleanAddressStr:
                    #         token = pre_token.lstrip()
                    #         token = token.rstrip()
                    #         prefix_flag = True       

                    if (token.lower() =='section' or token.lower() =='sector' and token.lower() in cleanAddressStr.lower()):
                            matched[subareakey] = token +' '+ tempArray[idx+1]
                            subarea_flag = True
                            return True

                    with open('./subarea-list.csv','rt')as f:
                        subarea_list = csv.reader(f)
                        for j, subarea in enumerate(subarea_list):
                            if (area.lower() == subarea[0].lower() and (token.lower() in subarea[1].lower() and subarea[1].lower() in cleanAddressStr.lower())):
                                print '............: '+subarea[1]
                                matched[subareakey] = subarea[1].lower()
                                subarea_flag = True
                        





        # def check_holding(token, idx):
        #     if (any(char.isdigit() for char in token)):
        #         if idx == 0:
        #             matched[housekey] = token
        #             return True

        #         elif (addresscomponents[idx+1].lower() == 'house' or addresscomponents[idx-1].lower() == 'house'):
        #             matched[housekey] = token
        #             return True


        # Parsing..............................
        for i, comp in enumerate(tempArray):
                comp=comp.strip()
                # print(comp)
                if (check_area(comp, i)):
                    continue

                if (check_sub_area(comp, i)):
                    print('subarea')
                    continue
        print('Parse Result')
        print(matched)





# old parser..............................
def isroad(road):
    road=road.lower()
    return 'road' in road or 'ave' in road or 'lane' in road or 'sarani' in road or 'soroni' in road or 'rd' in road or 'rd#' in road or 'sarak' in road or 'sharak' in road or 'sharani' in road or 'highway' in road or 'path' in road or 'chowrasta' in road or 'sorok' in road or 'goli' in road

def ishouse(house):
    house=house.lower()
    return 'house' in house and any(char.isdigit() for char in house) or 'h#' in house and any(char.isdigit() for char in house)


def isBuilding(market):
    return true
                

def isShop(floor):
    return true
        

op = {}

d={}

def parseAddress(address , d):
    # addresscomponents = address.split(',')
    for i, comp in enumerate(addresscomponents):
        comp=comp.strip()
        if (i == 0):
            if (not ishouse(comp) and not isroad(comp)):
                d[namekey] = comp
            elif (ishouse(comp)):
                d[housekey] = comp
            elif (isroad(comp)):
                d[roadkey] = comp
        else:
            if ishouse(comp) and housekey not in d:
                d[housekey] = comp
            elif isroad(comp):
                d[roadkey] = comp
            elif len(addresscomponents) > i + 1:
                d[ssareakey] = comp
            else:
                d[subareakey] = comp

            
          
            # op[addresskey] = d[addresskey]

            if (namekey in d):
                op[namekey] = d[namekey]
            if (housekey in d):
                parsedhouse=d[housekey].rsplit(" ", 1)
                if len(parsedhouse)>1:
                    op[house_nokey] = parsedhouse[1]
                else :
                    op[house_nokey] = housekey
            if (roadkey in d):
                op[roadkey]=d[roadkey]
            if (ssareakey in d):
                op[ssareakey]=d[ssareakey]
            if (subareakey in d):
                op[subareakey]=d[subareakey]
            if (areakey in d):
                op[areakey]=d[areakey]

    print(d);


def reptParse(address):
    addresscomponents = address.split(',')
    for i, comp in enumerate(addresscomponents):
        comp=comp.strip()
        d = {}
        print(comp)
        parseAddress(comp, d)

        
def customParse(address):
    addresscomponents = address.split(',')
    for i, comp in enumerate(addresscomponents):
        comp=comp.strip()
        d = {}
        print(comp)
        
        


def filterConAddress(address):
    # addresscomponents = address.split(',')
    address=address.lower()
    address = address.strip()

    if(address.find('besides') > 0):
        result = address.find('besides')
        print(result)
        str1 = address[:result]
        print(str1)

    if(address.find('near') > 0):
        result2 = address.find('near')
        print(result2)
        str1 = address[:result2]
        print(str1)