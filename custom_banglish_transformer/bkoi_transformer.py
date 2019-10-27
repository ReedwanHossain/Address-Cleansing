import csv
import re
from banglish_translator import *
import sys
reload(sys)
sys.setdefaultencoding('utf8')
#import bangla
house_fonts=[]
with open('./bangla_english_fonts.csv','r')as fbe:
    #print("got it")
    house_name_fonts = csv.reader(fbe)
    for f, fonts in enumerate(house_name_fonts):
    	house_fonts.append(fonts)
	    #word=word.replace(fonts[1],fonts[0])
#print(house_fonts)
def bangla_to_english(address):
    address=address.replace('.',' ')
    address=address.replace(u'\u0964',' ')
    address=address.replace(u'\u0028',u' \u0028 ')
    address=address.replace(u'\u0029',u' \u0029 ')

    with open('./digits.csv','rt')as df:
        digits=csv.reader(df)
        for i, digit in enumerate(digits):
            address=address.replace(digit[1],digit[0])
    address=re.sub(r'(,|#|-|:|/)',r' \1 ',address)
    #print(address)
    address=re.sub(r'(\d+)',r' \1',address)
    #print(address)
    eng_address=''
    address=address.split()
    #print(address)
    for word in address:
        getmylist=0
        #word=word.decode('utf-8')
        word=word.strip()
        '''
        if re.search(r'/',word):
        	print("got it /")
        	for key in house_fonts:
        		if re.search(r'key[1]',word):
        			print("got it")

        		word=word.replace(key[1],key[0])
        	p=1
        '''
        with open('./keyword_maplist.csv','r')as f:
            data_list = csv.reader(f)
            for j, keyword in enumerate(data_list):
                #keyword[0]=keyword[0].decode('utf-8') #english
                #keyword[1]=keyword[1].decode('utf-8') #bangla
                keyword[1]=keyword[1].strip()
                if word==keyword[1]:
                    #print("matched")  
                    #eng_address.append(keyword[0])
                    eng_address=eng_address+' '+keyword[0]
                    getmylist=1
                    #print(keyword[1]+'   paise')
                    break
        if getmylist==0:
            custom_address=main(word)
            custom_address=custom_address.replace('`','')
            eng_address=eng_address+' '+custom_address

                # elif keyword[1] in word:
                #     eng_address=eng_address+' '+keyword[0]

    eng_address=eng_address.strip()
    eng_address=eng_address.lower()
    eng_address=eng_address.replace(' - ','-')
    eng_address=eng_address.replace(' / ','/')
    eng_address=eng_address.replace(' : ',':')
    eng_address=eng_address.replace(' # ','#')
    #eng_address=eng_address.replace(' , ',',')
    return eng_address
'''
myaddress=raw_input("Enter a address : ")
obj=Transformer()
#obj.bangla_to_english(myaddress)
print(str(obj.bangla_to_english(myaddress)))
'''
