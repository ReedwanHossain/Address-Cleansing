import re
def preprocess_string(input_address):
    input_address = re.sub('dohs\s*(,)*\s*mirpur','mirpur dohs', input_address)
    input_address = input_address.replace('(',' ')
    input_address = input_address.replace(')',' ')
    input_address = input_address.replace('/',' ')
    input_address = re.sub('([0-9]|1[0-9]|2[0-9]|3[0-9])\s*\s+(tola|tala)+\s*',' ', input_address)
    input_address = re.sub('cantonment\s*(,)*\s*dhaka','dhaka cantonment', input_address)
    input_address = re.sub('r/a',' residential area', input_address)
    input_address = re.sub('(-|_|~)',' ', input_address)
    input_address = re.sub('( no | number | num)',' ', input_address)
    input_address = re.sub('dohs\s*(,)*\s*mohakhali','mohakhali dohs', input_address)
    input_address = re.sub('dohs\s*(,)*\s*baridhara','baridhara dohs', input_address)
    input_address = re.sub('dohs\s*(,)*\s*(banani|bonani)','banani dohs', input_address)
    input_address = re.sub('(mirpur)\s*(15|14|13|12|11|10|9|8|7|6|5|4|3|2|1)\s+',r'section \2 \1 ',input_address+' ')
    input_address = re.sub('(uttara|uttora)\s*([1-9]|1[1-8])\s+',r'sector \2 \1 ',input_address+' ')
    input_address = re.sub('([1-9]|1[1-8])\s+(sector|sactor)',r' \2 \1 ',input_address+' ')
    input_address = re.sub('([1-9]|1[1-8])\s+(section|saction)',r' \2 \1 ',input_address+' ')
    input_address = re.sub('(dhanmondi|danmondi)\s*([1-9]|1[1-9]|2[1-9]|3[1-9])\s+',r'road \2 \1 ',input_address+' ')
    input_address=input_address.replace('.',' ')
    return input_address

if __name__ == "__main__":
    n=input('enter: ')
    print(preprocess_string(n))