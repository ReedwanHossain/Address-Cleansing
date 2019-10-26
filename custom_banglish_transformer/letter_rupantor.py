import csv
import sys
from bkoi_transformer import bangla_to_english
reload(sys)
sys.setdefaultencoding('utf8')
while True:

    n=raw_input("Enter a adress or string : ")
    print(bangla_to_english(n))

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
