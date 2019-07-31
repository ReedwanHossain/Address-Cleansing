# import modules.......................
import re
import nltk
import csv
from nltk.tokenize import sent_tokenize, word_tokenize

dict_data = []
with open('./rapido.csv','rt')as f:
    test_data = csv.reader(f)
    for t, td in enumerate(test_data):
        input_address = td[0]
        # input_address = raw_input('Enter Address: ')
        input_address = " "+input_address
        print input_address+"\n"
        input_address = re.sub( r'([a-zA-Z])(\d)', r'\1-\2', input_address ) #insert a '-' between letters and number
        addresskey = 'address'
        namekey = 'name'
        housekey = 'house'
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
        #init value...................
        matched[housekey] = None
        matched[roadkey] = None
        matched[ssareakey] = None
        matched[subareakey] = None
        matched[areakey] = None

        matched[addresskey] = input_address
        matched_array = []

        prefix_dict = ['', 'east', 'west', 'north', 'south', 'middle', 'purba', 'poschim', 'uttar', 'dakshin', 'moddho', 'dokkhin', 'dakkhin']

        address_component = ['', 'house', 'plot', 'road', 'block', 'section', 'sector', 'avenue']

        # pre-processing...........................................................
        def multiple_replace(dict, text):
          # Create a regular expression  from the dictionary keys
          regex = re.compile("(%s)" % "|".join(map(re.escape, dict.keys())))
          # For each match, look-up corresponding value in dictionary
          return regex.sub(lambda mo: dict[mo.string[mo.start():mo.end()]], text) 

        rep2 = {
                    "rd#": " road ", "rd-": " road  ", "rd:": " road  ", "r:": " road ", "r#": " road ", " r-": " road ", " ,r-": " road ", "h#": " house ", "h-": " house ", "h:": " house ",
                    "bl-":" block ","bl#":" block ", "bl:":" block ", "b-":" block ","b:":" block ", "b#":" block ", 'sec-': ' section ','sec#': ' section ', 'sec:': ' section ', 's-': ' sector ', 's#': ' sector ', 's:': ' sector ',
                    'house': ' house ', 'house:': ' house ', 'road': ' road ', 'road:': ' road ', 'block-': ' block ', 'block:': ' block ', 'section': ' section ','section:': ' section ', 'sector': ' sector ','sector:': ' sector ',
                    'house no': ' house ', 'houseno:': ' house ', 'road no': ' road ', 'road no': ' road ', 'block no': ' block ', 'blockno': ' block ', 'section no': ' section ','sectionno': ' section ', 'sector no': ' sector ','sector': ' sector ',
                    'ave-': ' avenue ', 'ave:': ' avenue ', 'ave#': ' avenue ','ave:': ' avenue ', 'avenue:': ' avenue ', 'avenue-': ' avenue ', 'avenue#': ' avenue ', 'no :': '', 'no:': '', 'no -': '', 'no-': '', 'no =': '', 'no=': '', 'no.': '',
                } 
        area_dict = {"mirpur": " mirpur ", "uttara": " uttara ", "banani": " banani ", "mohammadpur": " mohammadpur ", "gulshan": " gulshan ", "baridhara": " baridhara ", "mdpur":"mohammadpur"} # define desired replacements here
        expand = multiple_replace(rep2, input_address.lower())
        expand = multiple_replace(area_dict, expand.lower())
        addresscomponents = word_tokenize(expand)


        tempArray = []
        for i, comp in enumerate(addresscomponents):
                comp=comp.strip()
                if comp == "," or comp == "":
                    continue
               
                temp = comp.lstrip('[0:!@#$-=+.]')
                temp = temp.rstrip('[:!@#$-]=+.')
                temp = temp.strip(" ");
                if(temp != ""):
                    tempArray.append(temp)
                # print comp.rstrip('[!@#$-]')
        print "final pre-processing "
        cleanAddressStr = ' '.join(tempArray)
        cleanAddressStr = re.sub(r" ?\([^)]+\)", "", cleanAddressStr)
        print cleanAddressStr
        tempArray = word_tokenize(cleanAddressStr)
        print tempArray
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

                    if (area_token[0].lower() == area[0].lower() and area_token[0].lower() in cleanAddressStr.lower()):
                        matched[areakey] = area[0].lower()
                        # matched_array.append(area[0].lower())
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
                    elif token == 'block' and area.lower() == 'bashundhara' or area.lower() == 'banani' or area.lower() == 'khilgaon' or area.lower() == 'banasree' or area.lower() == 'baridhara' or area.lower() == 'lalmatia':
                        if idx != len(tempArray)-1:
                            token = token+" "+tempArray[idx+1]
                    with open('./subarea-list.csv','rt')as f:
                        subarea_list = csv.reader(f)
                        for j, subarea in enumerate(subarea_list):
                            if (area.lower() == subarea[0].lower() and token.lower() == subarea[1].lower()):
                                matched[subareakey] = token.lower()
                                # matched_array.append(token.lower())
                                subarea_flag = True
                                return True

                elif(abs(idx-area_pos) > 1 or abs(idx-area_pos) == 1 and not any(char.isdigit() for char in tempArray[idx])):
                    global cleanAddressStr
                    token = token.lstrip('[0:!@#$-=+.]')
                    token = token.rstrip('[:!@#$-=+.]')
                    prefix_flag = False      

                    if (token.lower() =='section' or token.lower() =='sector' and token.lower() in cleanAddressStr.lower()):
                            matched[subareakey] = token +' '+ tempArray[idx+1]
                            if (area.lower()=='mirpur'):
                                matched[subareakey] = 'section' +' '+ tempArray[idx+1]
                            elif(area.lower()=='uttara'):
                                matched[subareakey] = 'sector' +' '+ tempArray[idx+1]
                            # matched_array.append(matched[subareakey])
                            subarea_flag = True
                            return True

                    with open('./subarea-list.csv','rt')as f:
                        subarea_list = csv.reader(f)
                        for j, subarea in enumerate(subarea_list):
                            if (area.lower() == subarea[0].lower() and (token.lower() in subarea[1].lower() and subarea[1].lower() in cleanAddressStr.lower())):
                                matched[subareakey] = subarea[1].lower()
                                # matched_array.append(matched[subareakey])
                                subarea_flag = True
            

            elif area_flag == False:
                with open('./subarea-list.csv','rt')as f:
                    subarea_list = csv.reader(f)
                    for j, subarea in enumerate(subarea_list):
                        if (token.lower() in subarea[1].lower() and subarea[1].lower() in cleanAddressStr.lower()):
                            matched[subareakey] = subarea[1].lower()
                            matched[areakey] = subarea[0].lower()
                            # matched_array.append(matched[areakey])
                            # matched_array.append(matched[subareakey])
                            subarea_flag = True
                            return True        


        def check_super_sub_area(token, idx):
            if ('block' in cleanAddressStr and 'mirpur' in cleanAddressStr.lower() and token == 'block'):
                if idx != len(tempArray)-1:
                    matched[ssareakey] = token+" "+tempArray[idx+1]
                    return True


        def check_holding(token, idx):
            if (any(char.isdigit() for char in token)):
                if idx == 0:
                    matched[housekey] = token
                    # matched_array.append(token)
                    return True

            elif ((token.lower() == 'house' or token.lower() == 'plot') and idx < len(tempArray)-1):
                if (any(char.isdigit() for char in tempArray[idx+1])):
                    matched[housekey] = tempArray[idx+1]
                    # matched_array.append(tempArray[idx+1])
                    return True



        def check_road(road, idx):

            if 'road' in road or 'ave' in road or 'lane' in road or 'sarani' in road or 'soroni' in road or 'rd' in road or 'rd#' in road or 'sarak' in road or 'sharak' in road or 'shorok' in road or 'sharani' in road or 'highway' in road or 'path' in road or 'poth' in road or 'chowrasta' in road or 'rasta' in road or 'sorok' in road or 'goli' in road or 'street' in road:

                if idx != len(tempArray)-1:
                    if (any(char.isdigit() for char in tempArray[idx+1])):
                        if(matched[roadkey]==None):
                                matched[roadkey] = road+" "+tempArray[idx+1]
                                return True
                        matched[roadkey] = matched[roadkey] +", "+road+" " +tempArray[idx+1]
                        return True
                if idx != 0:
                    if (not any(char.isdigit() for char in tempArray[idx-1])):
                        i = idx-1
                        road_str =  ''
                        if (not matched[areakey] == None and tempArray[i] == matched[areakey]):
                            matched[roadkey] = matched[areakey] +" "+ road
                            return True

                        while i>=0:
                            if not i==0 and tempArray[i-1] in address_component or tempArray[i-1] in matched_array:
                                if not any(char.isdigit() for char in tempArray[i]):
                                    road_str = tempArray[i]+ " " + road_str
                                    break
                                break
                            road_str = tempArray[i] +" "+ road_str
                            i=i-1
                        if(matched[roadkey]==None):
                            matched[roadkey] = road_str + road
                            return True
                        matched[roadkey] = matched[roadkey] +", "+road_str + road
                        # matched_array.append(matched[roadkey])
                        return True

        # Parsing..............................
        for i, comp in enumerate(tempArray):
                comp=comp.strip()
                # print(comp)
                if (check_area(comp, i)):
                    matched_array.append(matched[areakey])
                    pass
                if (check_sub_area(comp, i)):
                    matched_array.append(matched[subareakey])
                    pass
                if (check_super_sub_area(comp, i)):
                    matched_array.append(matched[ssareakey])
                    pass
                if (check_holding(comp, i)):
                    matched_array.append(matched[housekey])
                    pass
                if (check_road(comp, i)):
                    matched_array.append(matched[roadkey])
                    pass


        print('Parse Result')
        print matched
        print ('................................................................................')
        dict_data.append(matched)


csv_columns = ['address', 'area','subarea','supersubarea', 'house', 'road']
csv_file = "output.csv"
try:
    with open(csv_file, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for data in dict_data:
            writer.writerow(data)
except IOError:
    print("I/O error") 


# old parser..............................
def isroad(road):
    road=road.lower()
    return 'road' in road or 'ave' in road or 'lane' in road or 'sarani' in road or 'soroni' in road or 'rd' in road or 'rd#' in road or 'sarak' in road or 'sharak' in road or 'shorok' in road or 'sharani' in road or 'highway' in road or 'path' in road or 'chowrasta' in road or 'sorok' in road or 'goli' in road

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