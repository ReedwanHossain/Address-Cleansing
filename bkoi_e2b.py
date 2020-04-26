import csv
import re
import sys
import requests
#reload(sys)
# try:
#     import imp
#     imp.reload(sys)
#     sys.setdefaultencoding('utf8')
# except:
#     import importlib
#     importlib.reload(sys)
#import bangla

class ReverseTransformer(object):
    """docstring for Transformer"""
    def __init__(self):
        super(ReverseTransformer, self).__init__()
        

    def english_to_bangla(self, input_address):
        final_address=""
        input_address=input_address.split(',')
        for addr_component in input_address:
            address=addr_component
            address=re.sub(r'(#|-|:|/)',r' \1 ',address)
            #print(address)
            address=re.sub(r'(\d+)',r' \1',address)
            address=address.replace('0',u'\u09E6')
            address=address.replace('1',u'\u09E7')
            address=address.replace('2',u'\u09E8')
            address=address.replace('3',u'\u09E9')
            address=address.replace('4',u'\u09EA')
            address=address.replace('5',u'\u09EB')
            address=address.replace('6',u'\u09EC')
            address=address.replace('7',u'\u09ED')
            address=address.replace('8',u'\u09EE')
            address=address.replace('9',u'\u09EF')

            #print(address)
            bangla_address=''
            address=address.split()
            #print(address)
            for word in address:
                #print(word)
                getmylist=0
                #word=word.decode('utf-8')
                word=word.strip()
                with open('./keyword_maplist.csv','r')as f:
                    data_list = csv.reader(f)
                    for j, keyword in enumerate(data_list):
                        #keyword[0]=keyword[0].decode('utf-8') #english
                        #keyword[1]=keyword[1].decode('utf-8') #bangla
                        keyword[0]=keyword[0].strip()
                        keyword[0]=keyword[0].lower()
                        word=word.lower()
                        if word=='/' or word=='-':
                            bangla_address=bangla_address+' '+word
                            getmylist=1
                            break
                        if word==keyword[0]:
                            #print("matched")  
                            #bangla_address.append(keyword[0])
                            bangla_address=bangla_address+' '+keyword[1]
                            getmylist=1
                            #print(keyword[1]+'   paise')
                            break

                if getmylist==0:
                    response = requests.get("https://www.google.com/inputtools/request?text="+word+"&ime=transliteration_en_bn&num=1&cp=0&cs=0&ie=utf-8&oe=utf-8&app=jsapi&uv=e%3A%E0%A6%8F-0-1%3A%3B0%3B0")
                    print(response.status_code)
                    dictionary=response.json()
                    try:
                        #print(dictionary[1][0][1][0])
                        custom_address= dictionary[1][0][1][0]
                    except:
                        print("address error")
                        custom_address= ""
                    bangla_address=bangla_address+' '+custom_address

            bangla_address=bangla_address.strip()
            bangla_address=bangla_address.lower()
            bangla_address=bangla_address.replace(' - ','-')
            bangla_address=bangla_address.replace('. ','.')
            bangla_address=bangla_address.replace(' / ','/')

            final_address=final_address+bangla_address+", "
        final_address=final_address.rstrip()
        final_address=final_address.rstrip(',')
        #print(final_address)
        return final_address


'''
    try:
        address=raw_input("Enter a address : ")
    except:
        address=input("Enter a address : ")
'''

'''
obj=ReverseTransformer()
#print(obj.english_to_bangla(address))

import PySimpleGUI as sg

layout = [[sg.Text('Bangla:'), sg.Text('', size=(15,1), key='-OUTPUT-')],
          [sg.Input(key='-IN-')],
          [sg.Button('Transform'), sg.Button('Exit')]]

window = sg.Window('Barikoi Transformer', layout)

while True:  # Event Loop
    event, values = window.Read()
    print(event, values)
    if event is None or event == 'Exit':
        break
    if event == 'Transform':
        # Update the "output" text element to be the value of "input" element
        print(values)
        window['-OUTPUT-'].Update(obj.english_to_bangla(values['-IN-']))

        # A shortened version of this update can be written without the ".Update"
        # window['-OUTPUT-'](values['-IN-'])     
        # In older code you'll find it written using FindElement or Element
        # window.FindElement('-OUTPUT-').Update(values['-IN-'])

window.Close()
'''