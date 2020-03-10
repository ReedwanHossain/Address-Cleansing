import re
import csv
from dbconf.initdb import DBINIT
dbinit = DBINIT()
dbinit.load_subarea()
subarealist=[]
subareas = dbinit.get_subarea()
for i, subarea in enumerate(subareas):
    subarealist.append(subarea[1].lower().strip())
roadkeywords=['road' , 'ave' , 'lane' , 'sarani' , 'soroni' , 'rd#' , 'sarak' , 'sharak' , 'shorok' , 'sharani' , 'highway' , 'path' , 'poth' , 'chowrasta' , 'sarak' , 'rasta' , 'sorok' , 'goli' , 'street' , 'line']
class MiniParser(object):
    def __init__(self):
        self.roadkey=""
        self.blockkey=""
        self.housekey=""
        self.name=""
        self.floorkey=""
        self.subareakey=""
        self.multiple_subarea=[]
        self.dis_flag = True
    
    def parse(self, parsed_aadr):
        parsed_aadr=parsed_aadr.lower()
        parsed_aadr=parsed_aadr.split(',')
        parsed_aadr[0]=parsed_aadr[0].strip()
        
        try:
        	self.dis_flag = re.match('house\s+\d+',parsed_aadr[0]) and 'flat' not in parsed_aadr[0] and 'level' not in parsed_aadr[0] and 'floor' not in parsed_aadr[0] and parsed_aadr[0].split()[0]!='house' 
        except:
        	print(self.dis_flag)

        if not self.dis_flag:
            self.name=parsed_aadr[0]
            parsed_aadr.pop(0)
        for token in parsed_aadr:
            token=token.strip()
            if 'house' in token:
                token=token.strip()
                self.housekey=token.strip()
      
            elif any(s in token for s in roadkeywords):
                self.roadkey=token.strip()
            elif 'block' in token:
                self.blockkey=token.strip()
            elif 'flat' in token or 'floor' in token or 'level' in token:
                self.floorkey=token.strip()
      
            elif ('block' not in token and not any(s in token for s in roadkeywords) and 'house' not in token and 'floor' not in token and 'level' not in token and 'flat' not in token) and any(token == subarea for subarea in subarealist):
                self.subareakey=token.strip()
                self.multiple_subarea.append(token.strip())

        obj = {
            'house': self.housekey,
            'holding': self.name,
            'floor': self.floorkey,
            'road': self.roadkey,
            'block': self.blockkey,
            'subarea': self.subareakey,
            'multiple_subarea':self.multiple_subarea,
        }
        self.roadkey=""
        self.blockkey=""
        self.housekey=""
        self.name=""
        self.floorkey=""
        self.subareakey=""
        self.multiple_subarea=[]
        return obj

  