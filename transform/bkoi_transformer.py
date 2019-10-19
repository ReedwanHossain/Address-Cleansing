import csv
import re
import sys
from pyavrophonetic import avro
reload(sys)
sys.setdefaultencoding('utf8')
#import bangla
class Transformer(object):
    """docstring for Transformer"""
    def __init__(self):
        super(Transformer, self).__init__()
        

    def bangla_to_english(self, address):
        #address=address.decode('utf-8')
        
        
        with open('./transform/digits.csv','rt')as df:
            digits=csv.reader(df)
            for i, digit in enumerate(digits):
                address=address.replace(digit[1],digit[0])
        address=re.sub(r'(,|#|-|:)',r' \1 ',address)
        #print(address)
        address=re.sub(r'(\d+)',r' \1',address)
        #print(address)
        eng_address=''
        address=address.split()
        for word in address:
            getmylist=0
            #word=word.decode('utf-8')
            word=word.strip()

            # if re.match(r'\d+|#|-|:',word):
            #     eng_address=eng_address+' '+word
            with open('./transform/keyword_maplist.csv','r')as f:
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
                avro_address=avro.parse(word)
                avro_address=avro_address.replace('`','')
                eng_address=eng_address+' '+avro_address

                    # elif keyword[1] in word:
                    #     eng_address=eng_address+' '+keyword[0]

        eng_address=eng_address.strip()
        eng_address=eng_address.lower()
        return eng_address
        
    
    # myaddress=raw_input("Enter a address : ")
    # transformed_address = str(bangla_to_english(myaddress))
    # print(transformed_address)
    # return  transformed_address
    '''
    with open('./bangla_address.csv','r')as f:
        with open("output.csv", "w") as fp:
            wr = csv.writer(fp)
        #data_list = csv.reader(f)
            for j, keyword in enumerate(csv.reader(f)):
                mylist=[]
                bangla_address=keyword[0]
                try:
                #print(str(bangla_to_english(keyword[0])))
                    final_address=str(bangla_to_english(bangla_address))
                    final_address=final_address.lower()
                except:
                #print('address error')
                    final_address='address error'
                mylist.append(bangla_address)
                mylist.append(final_address)

                wr.writerow(mylist)
        fp.close()
    print("Completed")

    '''
