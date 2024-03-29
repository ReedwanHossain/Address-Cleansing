import csv
import sys
from dbconf.initdb import DBINIT
dbinit = DBINIT()
dbinit.load_bv()
dbinit.load_bl()
dbinit.load_jbl()
dbinit.load_ebl()


vowel_list = []
font_list = []
jukto_borno_list = []
digit_lists = [u'\u09E6', u'\u09E7', u'\u09E8', u'\u09E9',
               u'\u09EA', u'\u09EB', u'\u09EC', u'\u09ED', u'\u09EE', u'\u09EF']
sorborno_list = [u'\u0987', u'\u0988', u'\u0989',
                 u'\u098A', u'\u098F', u'\u0990', u'\u0993', u'\u0994']

bangla_letter_list = dbinit.get_bl()

for k, letter in enumerate(bangla_letter_list):
    # letter[0]=letter[0].strip()
    font_list.append(letter[0].strip())


vowels = dbinit.get_bv()
for i, vowel in enumerate(vowels):
    # print(vowel[0])
    # vowel[0]=vowel[0].strip()
    vowel_list.append(vowel.strip())
# print(vowel_list)
# jb=jukto borno
jbs = dbinit.get_jbl()
for i, jb in enumerate(jbs):
    # print(jb[0])
    # jb[0]=jb[0].strip()
    jukto_borno_list.append(jb[0].strip())
# print(jukto_borno_list)


def keyword_makelist(keyword):
    s = list(keyword)
    index = 0
    mylist = []
    # print(s)
    for i in range(len(s)):
        # print(i+1)
        #print(" ----> "+s[i])
        if i == len(s):
            break
        if s[i] == u'\u09CD':

            # print(i)
            mylist[index-1] = mylist[index-1]+s[i]+s[i+1]
            # s[i+1]=""
            # i=i+2
            del s[i+1]
            i = i+1
        else:
            mylist.append(s[i])
            index += 1
        # print(index)
        # print(mylist)
    return mylist


def bangla_rupantor(text):
    key_list = dbinit.get_bl()
    for j, keyword in enumerate(key_list):
        text = text.replace(keyword[0].strip(), keyword[1].strip())

    text = text.replace('`', '')
    text = text.replace(u'\u09CD', '')

    return text.lower()


def main(input_text):
    st = ""
    #input_text=raw_input("Enter : ")

    try:
        input_text = input_text.replace('হ্', 'হ')
    except Exception as e:
        print(e)
        pass
    # chandrobindu (u'\u0981') remove
    input_text = input_text.replace(u'\u0981', '')
    input_text = input_text.replace(u'\u0983', ':')
    input_text = input_text.replace(u'\u0964', '')
    input_text = input_text.replace(u'\u09AC\u09BC', u'\u09B0')
    input_text = input_text.replace(u'\u09AF\u09BC', u'\u09DF')
    input_text = input_text.replace(u'\u09A1\u09BC', u'\u09B0')
    input_text = input_text.replace(u'\u09A2\u09BC', u'\u09B0')
    text = keyword_makelist(input_text)
    count = 1
    # print(text)
    for w in range(len(text)):
        result = bangla_rupantor(text[w])
        # print(text[w])
        if w < len(text)-1:
            if (text[w+1] not in vowel_list and text[w] not in vowel_list) and text[w] not in digit_lists and text[w] in font_list and text[w] not in sorborno_list:
                st += result+'o'
                if w < len(text)-2 and len(text) > 3:
                    if (text[w+2] in vowel_list and st[-1] == 'o' and w > 0) and text[w] not in jukto_borno_list:
                        st = st[:-1]
            else:
                st += result
        if w == len(text)-1:
            st += result
            if text[w] in jukto_borno_list:
                st += 'o'
                break
        # print(text[w])
    return st
