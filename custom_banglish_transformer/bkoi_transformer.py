import csv
import re
from custom_banglish_transformer.banglish_translator import *
import sys
from dbconf.initdb import DBINIT
#import bangla


class Transformer(object):
    """docstring for Transformer"""

    def __init__(self):
        super(Transformer, self).__init__()
        self.dbinit = DBINIT()
        self.dbinit.load_digit()
        self.dbinit.load_keyword_map()

    def bangla_to_english(self, address):
        # if (re.sub('.com|.xyz|.net|.co|.inc|.org|.bd.com|.edu|.\u0995\u09AE', address) == None):
        #     address=address.replace('.','')
        address = address.replace('.\u0995\u09AE', ' .com')
        address = address.replace('.\u09A8\u09C7\u099F', ' .net')
        address = address.replace('.\u09AC\u09BF\u09A1\u09BF', ' .bd')
        address = address.replace('.\u0995\u09CB', ' .co')
        address = address.replace(u'\u0964', ' ')
        address = address.replace(u'\u0028', u' \u0028 ')
        address = address.replace(u'\u0029', u' \u0029 ')

        digits = self.dbinit.get_digit()
        for i, digit in enumerate(digits):
            address = address.replace(digit[1], digit[0])
        address = re.sub(r'(,|#|-|:|/|–)', r' \1 ', address)
        # print(address)
        address = re.sub(r'(\d+)', r' \1', address)
        # print(address)
        eng_address = ''
        address = address.split()
        # print(address)
        for word in address:
            getmylist = 0
            # word=word.decode('utf-8')
            word = word.strip()
            data_list = self.dbinit.get_keyword_map()
            for j, keyword in enumerate(data_list):
                # keyword[0]=keyword[0].decode('utf-8') #english
                # keyword[1]=keyword[1].decode('utf-8') #bangla
                if word == keyword[1].strip():
                    # print("matched")
                    # eng_address.append(keyword[0])
                    eng_address = eng_address+' '+keyword[0]
                    getmylist = 1
                    #print(keyword[1]+'   paise')
                    break
            if getmylist == 0:
                custom_address = main(word)
                custom_address = custom_address.replace('`', '')
                eng_address = eng_address+' '+custom_address

                # elif keyword[1] in word:
                #     eng_address=eng_address+' '+keyword[0]

        eng_address = eng_address.strip()
        eng_address = eng_address.lower()
        eng_address = eng_address.replace(' - ', '-')
        eng_address = eng_address.replace(' – ', '–')
        eng_address = eng_address.replace(' / ', '/')
        eng_address = eng_address.replace(' : ', ':')
        eng_address = eng_address.replace(' # ', '#')
        eng_address = re.sub(r'(\.) (\d+)', r'\1\2', eng_address)
        eng_address = re.sub(r'(\s+[a-z]) (\d+)', r'\1\2', eng_address)
        eng_address = eng_address.replace(u'\u09BC', '')
        eng_address = eng_address.replace(' .com', '.com')
        eng_address = eng_address.replace(' .net', '.net')
        eng_address = eng_address.replace(' .bd', ' .bd')
        eng_address = eng_address.replace(' .co', ' .co')
        # print(eng_address)
        return eng_address
