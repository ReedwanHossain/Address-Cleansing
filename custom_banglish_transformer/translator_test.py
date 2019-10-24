import csv
import sys
reload(sys)
sys.setdefaultencoding('utf8')
vowel_list=[]
jukto_borno_list=[]
with open('./bangla_vowel.csv','rt') as fv:
	vowels= csv.reader(fv)
	for i, vowel in enumerate(vowels):
		#print(vowel[0])
		vowel[0]=vowel[0].strip()
		vowel_list.append(vowel[0])
#print(vowel_list)
#jb=jukto borno
with open('./bangla_jukto_borno_list.csv','rt') as fjb:
	jbs= csv.reader(fjb)
	for i, jb in enumerate(jbs):
		#print(jb[0])
		jb[0]=jb[0].strip()
		jukto_borno_list.append(jb[0])
#print(jukto_borno_list)

def keyword_makelist(keyword):
	s=list(keyword)
	index=0
	mylist=[]
	#print(s)
	for i in range(len(s)):
	    #print(i+1)
	    #print(" ----> "+s[i])
	    if i==len(s):
	        break
	    if s[i]==u'\u09CD':
	        
	        #print(i)
	        mylist[index-1]=mylist[index-1]+s[i]+s[i+1]
	        #s[i+1]=""
	        #i=i+2
	        del s[i+1]
	        i=i+1
	    else:
	        mylist.append(s[i])
	        index+=1
	    #print(index)
	    #print(mylist)
	return mylist

def bangla_rupantor(text):
    with open('./bangla_letter_list.csv','rt') as f:
        key_list = csv.reader(f)
        for j, keyword in enumerate(key_list):
            keyword[0]=keyword[0].decode('utf-8') 
            keyword[1]=keyword[1].decode('utf-8')
            keyword[0]=keyword[0].strip()
            keyword[1]=keyword[1].strip()

            text=text.replace(keyword[0],keyword[1])

    text=text.replace('`','')
    text=text.replace(u'\u09CD','')

    return text.lower()


while(True):
	st=""
	input_text=raw_input("Enter : ")
	input_text=input_text.decode('utf-8')
	#chandrobindu (u'\u0981') remove
	input_text=input_text.replace(u'\u0981','')
	text=keyword_makelist(input_text)
	count=1
	#print(text)
	for w in range(len(text)):
	    result=bangla_rupantor(text[w])
	    #print(text[w])
	    if w<len(text)-1:
	    	if (text[w+1] not in vowel_list and text[w] not in vowel_list):
	    		st+=result+'o'
	    		#print(st)
	    		if w<len(text)-2 and len(text)>3 :
	    		    if (text[w+2] in vowel_list and st[-1]=='o' and w>0)  and text[w] not in jukto_borno_list:
	    		    	st = st[:-1]


	    	else:
	    		st+=result
	    if w==len(text)-1:
	    	st+=result
	    #print(text[w])
	print(st)