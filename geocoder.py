
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