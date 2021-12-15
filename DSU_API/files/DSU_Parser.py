#import all needed modules and tools for making algorithm 
import re
import enchant
from difflib import SequenceMatcher
from numpy.core.shape_base import block
import pandas as pd
import csv
from pandas.io.parsers import TextParser
import preprocessor
import word_preprocessing
import json
import synonym
import time
#its for import csv file read 

#Tree Format json for district and road
with open('DSU_API/files/sample.json') as f:
  DSU= json.load(f)

Type=list(pd.read_csv("DSU_API/files/ptypeplace.csv")['PlaceType'])
data=pd.read_csv("DSU_API/files/district_regex.csv")
temp_div=data['division'].tolist()
district=data['district'].tolist()

def similar(a,b):
  return SequenceMatcher(None, a, b).ratio()



# Main Algorithm to change character position for getting accuracy and making similar word for matching
def result(s1,s2):
  string1=s1.lower()
  string2=s2.lower()
  # Word preprocessing which means change word with similar spelling like bh = v gaon=gao etc
  string1=word_preprocessing.word_preprocessor(string1)
  string2=word_preprocessing.word_preprocessor(string2)
  
  # get len of string 1 and string 2 and take it as a list
  len1=len(string1)
  len2=len(string2)
  strlist1=list(string1)
  strlist2=list(string2)
  n=0
  if len1<=len2:
    n=len1
  else:
    n=len2
  # The main part is here to exchange character if both character are same position and their sound is same 
  for i in range(0,n):
    if string1[i]=='j' and string2[i]=='z' or (string1[i]=='z' and string2[i]=='j'):
      strlist2[i]=strlist1[i]
    if string1[i]=='i' and string2[i]=='y' or (string1[i]=='y' and string2[i]=='i'):
      strlist2[i]=strlist1[i]
    if string1[i]=='a' and string2[i]=='o' or (string1[i]=='o' and string2[i]=='a'):
      strlist2[i]=strlist1[i]
    if string1[i]=='o' and string2[i]=='u' or (string1[i]=='u' and string2[i]=='o'):
      strlist2[i]=strlist1[i]
    if string1[i]=='e' and string2[i]=='i' or (string1[i]=='i' and string2[i]=='e'):
      strlist2[i]=strlist1[i]
    if ((string1[i]=='a' and string2[i]=='e') or (string1[i]=='e' and string2[i]=='a')) and (i==n-2 or i==1): 
      strlist2[i]=strlist1[i]
    if string1[i]=='k' and string2[i]=='q' or (string1[i]=='q' and string2[i]=='k'):
      strlist2[i]=strlist1[i]
    if string1[i]=='o' and string2[i]=='w' or (string1[i]=='w' and string2[i]=='o'):
      strlist2[i]=strlist1[i]
  
  # join character and make string after preprocessing string and character by the above algorithm.
  str1 = ''.join(strlist1)
  str2=''.join(strlist2)

  # getting the accuracy of 2 string after changing their property 
  n=similar(str1,str2)
  #print(str1,' ',str2)
  if n>=0.94 and n<=1.0 and 'daka' not in str1:
    return True
  if (n>=0.90 and n<=1.0) and len(str1)>=14:
    return True
  # if ('road' in str1 or 'lane' in str1 or 'line' in str1 or 'high way' in str1) and len(str1)>=14:
  #   if n>=0.87 and n<=1.0:
  #     return True
  elif n==1.0 and 'daka' not in str1:
    return True
  #if n==1:
    #return True
  else:
    return False

# Another Important algoritm to make String similarrity and space count and space join matching 
def finalresult(str1,str2):
    str1=str1.lower()
    str2=str2.lower()
    space_count=0
    str1join=str1
    space_count=str1.count(' ') #space count how many space has in input string that means knowledge based string 

    # Address String preprocessing which means clean address without any cotation mark or somthing like this 
    str2_preprocess=preprocessor.preprocessing(str2)

    # made lower str2 means address string after preprocess 
    str2_preprocess=str2_preprocess.lower()
    str2_split=str2_preprocess.split() # split address string by space 

    # if string 1 has space then removed space for checking address in or not in as a without sace in address 
    str1join=str1.replace(' ','') 
    str1join=str1join.lower()
    str1_lower=str1.lower()
    fnresult=False # initial return result False  
    j=0
    flag=0
    # direct input string is in user input address then return result is True
    
    if str1 in str2_split or str1join in str2_split: 
        fnresult=True
    else:
      for element in str2_split:
        if similar(str1join,element)>=0.70:
          if result(str1join,element)==True:
            flag=1
            break 
        if flag==1:
          break 
      if flag==1:
        fnresult=True
      else:
          # This loop will continue length of address - input string space count 
          for i in range(0,len(str2_split)-space_count):
              # join how many space is in input string 
              res=' '.join(str2_split[j:(j+space_count+1)])
              res1=res
              # Here we Have consider join addresse split string 2 position like begun bari not beg un bari 
              try:
                res1=str2_split[i]+str2_split[i+1]
                res2=str2_split[i]
              except Exception as e:
                pass
              try:
                  if str1.lower()==res or str1join==res:
                      fnresult=True
                      break
                  #call similar function to get accuracy and matching string status 
                  #if block section mirpur sector gulsan like this word then need not to check similarity algorithm 
                  elif (similar(str1.lower(),res)>=0.60 or similar(str1.lower(),res1)>=0.60): 
                    if result(str1,res)==True or result(str1,res1)==True:
                      fnresult=True
                      break
    
              except Exception as e:
                  pass
              j=j+1
    return fnresult

def Identifier1(input_address):
  input_address=preprocessor.preprocessing(input_address)
  input_address=input_address.lower()
  input_address=synonym.preprocess_string(input_address)
  result_list=[]
  tem_list=[]
  c_district=[]
  # dictionary district sub district and super subdistrict access and checking 
  for district_key,district_info in DSU.items():
    
    district="None"
    #checking district is in or not in address
    if ' '+district_key.lower()+' ' in input_address:
      #print('in')
      district=district_key
      c_district.append(district_key)
      #input_address=input_address.replace(district_key,'')
    if district=='None':
      try:
        if re.search('\s+'+district_info['District_regex']+'\s+',' '+input_address+' '):
          district=district_key
          c_district.append(district_key)
      except:
        pass
      
      
    if district=='None':
      if finalresult(district_key,input_address)==True:
        #print('my')
        district=district_key
        c_district.append(district_key)
    
    if district!='None':
      
      for subdistrict_key,subdistrict_info in district_info['Sub District'].items():
        cntsup=0
        subdistrict="None"
        Union="None"
        result_dictionary={}
        temp_result={}
        find=0
        if ' '+subdistrict_key.lower()+' ' in ' '+input_address+' ':
          subdistrict=subdistrict_key
          #print('subdistrict in')
          find=1
        if subdistrict=='None':
          try:
            #subdistrict_info['subdistrict_regex']=subdistrict_info['subdistrict_regex'].strip('\s+')  
            if re.search('\s+'+subdistrict_info['Subdistrict_regex']+'\s+',' '+input_address+' '):
              #print('subdistrict_regex')
              subdistrict=subdistrict_key
              find=1
          except:
            pass
        if subdistrict=='None':
          if finalresult(subdistrict_key,input_address)==True:
            #print('my')
            subdistrict=subdistrict_key
            find=1
        x=subdistrict_info['Union'] #here x is the list of super subdistrict ander district 
        for o in x:
          if find==1:
            if finalresult(o,input_address)==True:
              Union=o
              cntsup=1
              break
          if find==0: #and ('Section' not in o and 'Section' not in subdistrict_key) and ('Block' not in o and 'Block' not in subdistrict_key) :
            if finalresult(o,input_address)==True:
              Union=o
              subdistrict=subdistrict_key
              break
              
        if district!="None" and (subdistrict!="None" and len(subdistrict)!=0):
          result_dictionary["District"]=district
          result_dictionary["Subdistrict"]=subdistrict
          result_dictionary["Union"]=Union
          
        if cntsup==1 and len(subdistrict)!=0:
          temp_result["District"]=district
          temp_result["Subdistrict"]=subdistrict
          temp_result["Union"]=Union
          
        if len(temp_result)!=0:
          tem_list.append(temp_result)
        if len(result_dictionary)!=0 and len(tem_list)==0:
          result_list.append(result_dictionary)
  if len(tem_list)!=0:
    return tem_list
  if len(result_list)==0 and len(c_district)!=0:
    Result_list=[]
    c_district=set(c_district)
    c_district=list(c_district)
    for y in c_district:
      din={}
      find=True
      for type in Type:
        if y.lower()+' '+type.lower() in input_address:
          find=False
          break
        elif finalresult(y.lower()+' '+type.lower(),input_address)==True:
          find=False
          break
      
      if find==True:
        #print(y)
        din["District"]=y
        din["Subdistrict"]='None'
        din["Union"]='None'
        Result_list.append(din)
    return Result_list
  else:
    return result_list

def Identifier2(input_address):
  input_address=preprocessor.preprocessing(input_address)
  input_address=input_address.lower()
  input_address=synonym.preprocess_string(input_address)
  #input_address=input_address.replace(" tola "," ")
  Result_list=[]
  c_district=[]
  cnt=0
  # dictionary area sub area and super subdistrict access and checking 
  for district,area_info in DSU.items(): 
    result_dictionary={}
    find_union="None"
    find_subdistrict="None"
    r="None"
    re="None"
    #br=0
    if ' '+district.lower()+' ' in input_address:
      re=district
      c_district.append(re)
    if re=='None':
      try:
        #area_info['area_regex']=area_info['area_regex'].strip('\s+')
        if re.search('\s+'+area_info['District_regex']+'\s+',' '+input_address+' '):
          #print('area_regex')
          re=district
          c_district.append(district)
      except:
        pass
    
    if re=='None':
      if finalresult(district,input_address)==True:
          re=district
          c_district.append(re)
    #after getting area check subdistrict under that area
    temp=0
    br=0
    
    for subdistrict,subdistrict_info in area_info['Sub District'].items():
        cnt=0
        if ' '+subdistrict.lower()+' ' in ' '+input_address+' ':
          if temp<=len(subdistrict):
            find_subdistrict=subdistrict
            temp=len(subdistrict)
            cnt=1
            #print('1')
            br=1
        
        if find_subdistrict=='None' or cnt==0:
          
          try:
          
            #subdistrict_info['subdistrict_regex']=subdistrict_info['subdistrict_regex'].strip('\s+')
            #print(subdistrict_info['\s+'+'subdistrict_regex']+'\s+','-->',' '+input_address+' ')
            if re.search('\s+'+subdistrict_info['Subdistrict_regex']+'\s+',' '+input_address+' '):
              if temp<=len(subdistrict):
                find_subdistrict=subdistrict
                temp=len(subdistrict)
                #print('1')
                cnt=1
                br=1
          except:
            pass
        if find_subdistrict=='None' or cnt==0:
        
          sub=subdistrict.replace(" ","")
          find=0
          if (finalresult(subdistrict,input_address)==True or finalresult(sub,input_address)==True):
              if temp<=len(subdistrict):
                find_subdistrict=subdistrict
                temp=len(subdistrict)
                #print('1')
                br=1
        # checking super subdistrict under area 
        #print(find_subdistrict)
        x=subdistrict_info['Union']#here x is the list of super subdistrict ander area 
        if br==1:
            for o in x:
                mub=o.replace(" ","")
                if finalresult(o,input_address)==True or finalresult(mub,input_address)==True:
                    find_union=o
                    r=subdistrict
                    break
                  # if find_union!='':
                  #   break
      # if br==1:
      #     break
    #its for store result in dictionary which will given as output 
    if find_union!="None" or (find_subdistrict!="None" and len(find_subdistrict)!=0):
        result_dictionary["District"]=district
        result_dictionary["Subdistrict"]=find_subdistrict
        result_dictionary["Union"]=find_union
        Result_list.append(result_dictionary)
        cnt=cnt+1
    # if there have multiple answer for same sub area then it will not parsed 
    # if cnt>=2:
    #   break
  
  if len(Result_list)==0 and len(c_district)!=0:
    c_district=set(c_district)
    c_district=list(c_district)
    #c_district=", ".join(c_district)
    for y in c_district:
      din={} 
      din["District"]=y
      din["Subdistrict"]='None'
      din["Union"]='None'
      Result_list.append(din) 
  
  return Result_list

def Identifier(input_address):
  res=Identifier1(input_address)
  #print(res)
  parse={}
  not_parse={}
  if len(res)==0: 
      ans1=Identifier2(input_address)
      if len(ans1)>=2:
        temp_result=[] 
        for j in range(0,len(ans1)):
          find=True
          try:
            if ans1[j]['Subdistrict'] in district:
              find=False
          except Exception:
            pass 
          for x in Type:
            if (ans1[j]['Subdistrict']+' '+x).lower() in input_address.lower():
              find=False
              break
            elif finalresult((ans1[j]['Subdistrict']+' '+x),input_address)==True:
              find=False
              break

          if find==True: #ans1[j]['Area']+' Road' not in ans1[j]['Road']:
            temp_result.append(ans1[j])
        #print(temp_result)
        if len(temp_result)==0:
          temp_result.append(ans1[0])

        not_parse['Predicted Result']=temp_result
        return not_parse
      else:
        #print(ans1)
        parse['Parsed']=ans1
        return parse
  else:
      if len(res)>=2:
        temp_result=[]
        for j in range(0,len(res)):
          find=True
          try:
            if res[j]['District'] in temp_div:
              find=False
          except Exception:
            pass

          for x in Type:
            if (res[j]['District']+' '+x).lower() in input_address.lower() or (res[j]['Subdistrict']+' '+x).lower() in input_address.lower():
              find=False
              break
            elif finalresult((res[j]['Subdistrict']+' '+x),input_address)==True or finalresult((res[j]['District']+' '+x),input_address)==True:
              find=False
              break
          if find==True: #res[j]['Area']+' Road' not in res[j]['Road']:
            temp_result.append(res[j])
        #print(temp_result) 
        if len(temp_result)==0:
          temp_result.append(res[0])
        not_parse['Predicted Result']=temp_result
        return not_parse
      
      else:
        #print(res)
        parse["Parsed"]=res
        return parse

if __name__ == "__main__":
  while True:
    n=input('enter: ')
    start=time.time()
    print(Identifier(n))
    end=time.time()
    print(end-start)
  