import csv
import sys
reload(sys)
sys.setdefaultencoding('utf8')
vowel_list=[]
with open('./bangla_vowel.csv','rt') as fv:
	vowels= csv.reader(fv)
	for i, vowel in enumerate(vowels):
		#print(vowel[0])
		vowel_list.append(vowel[0])
#print(vowel_list)
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
    return text.lower()


while(True):
	text=raw_input("Enter : ")
	text=text.decode('utf-8')
	for w in text:
		print(w)
	print(bangla_rupantor(text))