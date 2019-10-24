import csv
c=0
# with open('missing_juktoborno.csv', mode='w') as file:
#     file_writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
line=[]
with open('./complex.csv','rt') as f:
    key_list = csv.reader(f)
    for j, keyword in enumerate(key_list):
    	check=0
    	with open('./bangla_letter_list.csv','rt')as fl:
    		for i, bn in enumerate(csv.reader(fl)):
    			if(bn[0].strip()==keyword[0].strip()):
    				check=1
    				break
    	if(check==0):
    		print(keyword[0] + "  not found")
    		c+=1
    		#line.append(keyword)
				#file_writer.writerow(keyword)
			   

#print(line)

	    #keyword[0]=keyword[0].decode('utf-8')
	    #print(keyword[0])
