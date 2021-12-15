import re
import enchant

def replace_multiple(input_address):
    input_address=' '.join(input_address.split())
    inp_list=input_address.split()
    for part in inp_list:
        if not part.isnumeric():
            input_address=input_address.replace(part+' '+part,part)
    return input_address.strip()


def get_repl():
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
    return [rep1, rep2]


def multiple_replace(dict, text):
    # Create a regular expression  from the dictionary keys
    regex = re.compile("(%s)" % "|".join(map(re.escape, dict.keys())))
    # For each match, look-up corresponding value in dictionary
    return regex.sub(lambda mo: dict[mo.string[mo.start():mo.end()]], text)


def preprocessing(input_address):
    # save input addr to return
    saveTortnAddr = input_address
    # adding extra space before inputted address and convert it into lowercase
    input_address = " "+input_address
    input_address = input_address.lower()

    # remove hash, comma, qoutation marks from the address and add extra space after the address
    input_address = re.sub(r',', ' ', input_address)
    input_address = re.sub(r'#|"', ' ', input_address)
    input_address = input_address.lower()+"  "
    input_address = "  "+input_address.lower()
    input_address = re.sub(r'\s*flat\s*(no)*(:)*(-)*\s*[a-z]{1}\d{1}\s+', ' ', input_address)


    # remove the section inside the first brakets() as considered as a comments or hints of an address
    input_address = re.sub(r'\([^)]*\)', '', input_address)
    # insert space between 'no' and digits
    input_address = re.sub(r'(\d+)(no\s+)', r'\1 \2', input_address)
    input_address = re.sub(r'(\s+no)(\d+)', r'\1 \2', input_address)
    input_address = "  "+input_address
    # replace the short abbreviated keywords into full form with rep1 dictionary
    #input_address = multiple_replace(get_repl()[1], input_address.lower())
    
    # remove 5 digits value
    # if re.search('\d{5}', input_address):
    #     temp_input_address = input_address.split()
    #     for i, t in enumerate(temp_input_address):
    #         if re.search('\d{5}', t):
    #             temp_input_address[i] = ""
    #     input_address = ' '.join(str(e) for e in temp_input_address)
    '''
    decimal_find=re.search(r'\d(.)\d',input_address)
    if  not re.search(r'\d(.)\d',input_address):
        input_address=input_address.replace("."," ")
    '''
    #print(input_address)
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
    input_address = input_address.replace("+", " ")
    input_address = input_address.replace("$", " ")
    input_address = input_address.replace("]", " ")
    input_address = input_address.replace("[", " ")
    input_address = input_address.replace("{", " ")
    input_address = input_address.replace("}", " ")
    input_address = input_address.replace(" no ", " ")
    input_address = input_address.replace("|", " ")
    input_address = input_address.replace("!", " ")
    input_address = input_address.replace("?", " ")
    # some address contains 'street' or 'address' keyword at the begining of the address. so remove them
    # try:
    #     first_street = re.match(
    #         r'\W*(\w[^,. !?"]*)', input_address).groups()[0]
    # except:
    #     first_street = ""
    # if 'street' in first_street or 'street:' in first_street or first_street == 'street' or first_street == 'street:' or first_street == 'office:' or first_street == 'address:' or first_street == 'address':
    #     input_address = input_address.replace(first_street, " ")

    # remove the string like 'near xyz hospitals' etc
    # input_address = re.sub(
    #     r'(behind|nearby|near|near by|near to|opposite|opposite of|beside)[^)]*(building|plaza|market|villa|cottage|mansion|vila|tower|place|complex|center|mall|monjil|manjil|building|headquarter|bhaban|mosque|masjid|mosjid|hospital|university|school|mandir|mondir|police station|park)', '', input_address)
    # # delete flat no. or etc
    # temp_input_address = input_address.split()
    # if 'flat' in input_address:
    #     temp_input_address = input_address.split()
    #     for i, t in enumerate(temp_input_address):
    #         if i < len(temp_input_address)-1:
    #             if t == 'flat' and any(char.isdigit() for char in temp_input_address[i+1]):
    #                 temp_input_address.remove(temp_input_address[i])
    #                 temp_input_address.remove(temp_input_address[i])
    #                 break
    #     input_address = ' '.join(str(e) for e in temp_input_address)

    # remove postal codes
    # input_address = re.sub(
    #     r'(post code|post|zip code|postal code|postcode|zipcode|postalcode|dhaka)(\s*)(-|:)*(\s*)(\d{4})(\s*)', '', input_address)
    # remove apt, room level no etc
    # flat floor stroing
    flat = None
    flat = re.search(
        r'((\s+)(apt|apartment|floor|room|flat|level|flr|suite|suit)(\s+(no)*[.]*(:)*\s*(-)*\s*)(([0-9]+|\d+)((th|rd|st|nd))))(\s*)|(\s*)((\s*)(([0-9]+|\d+)(th|rd|st|nd))(\s*(:)*\s*(-)*\s+)(apt|apartment|floor|flat|level|room|flr|suite|suit))(\s*)|(((\s+)(apt|apartment|floor|flat|level|room|flr|suite|suit)(\s*(:)*\s*(-)*\s*)(\d+[a-z]{1}\s+)))(\s*)|(\s+)(((apt|apartment|floor|flat|level|room|flr|suite|suit)(no)*(\s*)(([0-9]+|\d+))(th|rd|st|nd)))(\s*)',  input_address)
   
    input_address = re.sub(
        r'((\s+)(apt|apartment|floor|room|flat|level|flr|suite|suit)(\s+(no)*[.]*(:)*\s*(-)*\s*)(([0-9]+|\d+)((th|rd|st|nd))))(\s*)|(\s*)((\s*)(([0-9]+|\d+)(th|rd|st|nd))(\s*(:)*\s*(-)*\s+)(apt|apartment|floor|flat|level|room|flr|suite|suit))(\s*)|(((\s+)(apt|apartment|floor|flat|level|room|flr|suite|suit)(\s*(:)*\s*(-)*\s*)(\d+[a-z]{1}\s+)))(\s*)|(\s+)(((apt|apartment|floor|flat|level|room|flr|suite|suit)(no)*(\s*)(([0-9]+|\d+))(th|rd|st|nd)))(\s*)', '  ', input_address)
    input_address = re.sub(
        r'(\s+[1-9]+|\d+)(th|rd|st|nd)\s+', ' ', input_address)
    input_address = input_address.replace(',', ' ')
    # remove the number greater than 5000
    all_num_list = re.findall(r'\d+', input_address)
    if len(all_num_list) > 0:
        max_num_in_string = max(map(int, all_num_list))
        if max_num_in_string > 5000:
            max_num_in_string = str(max_num_in_string)
            input_address = input_address.replace(max_num_in_string, '')

    # insert extra space between digits and aphabetic strings
    # insert a ' ' between letters and number
    input_address = re.sub(r'([a-zA-Z]+)(\d+)', r'\1 \2', input_address)
    # insert a '-' between letters and number
    input_address = re.sub(r'(\d+)([a-zA-Z]+)', r'\1 \2', input_address)

    # remove dots if string has no domain name like xyz.com
    if (re.search('.com|.xyz|.net|.co|.inc|.org|.bd.com|.edu|\d+\.\d+', input_address) == None):
        input_address = input_address.replace(".", " ")
    #print(input_address)
    input_address = input_address.replace('outside dhaka','')
    input_address = input_address.replace('inside dhaka','')
    input_address = input_address.replace('out of dhaka','')
    input_address = input_address.replace('  ', ' ')
    input_address=replace_multiple(input_address.strip())
    #print(input_address)
    return input_address


if __name__ == "__main__":
    while True:
        q = input('Enter address: ')
        print(preprocessing(q))
