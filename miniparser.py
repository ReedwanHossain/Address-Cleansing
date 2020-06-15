import re
import csv
from dbconf.initdb import DBINIT
dbinit = DBINIT()
dbinit.load_subarea()
subarealist = []
arealist = []
subareas = dbinit.get_subarea()
for i, subarea in enumerate(subareas):
    subarealist.append(subarea[1].lower().strip())
    arealist.append(subarea[0].lower().strip())
roadkeywords = ['road', 'ave', 'lane', 'sarani', 'sharani', 'soroni', 'shoroni', 'rd#', 'sarak', 'sharak',
                'shorok', 'sharani', 'highway', 'path', 'poth', 'chowrasta', 'sarak', 'rasta', 'sorok', 'goli', 'street', 'line']


class MiniParser(object):
    def __init__(self):
        self.name = ""
        self.holding = ""
        self.housekey = ""
        self.floorkey = ""
        self.roadkey = ""
        self.blockkey = ""
        self.ssarea = ""
        self.subareakey = ""
        self.multiple_subarea = []

    def parse(self, parsed_aadr, ptype):
        multiple_name = []
        idx = 0
        multiple_road = []
        ptype = ptype.lower().strip()
        parsed_aadr = parsed_aadr.lower().lstrip(',').rstrip(',')
        parsed_aadr = parsed_aadr.split(',')
        # print(parsed_aadr)
        for i in range(len(parsed_aadr)):
            token = parsed_aadr[i]
            token = token.strip()
            #print("token" + token + "token")
            if token == "":
                continue
            if not re.match('house\s+\d+', token) and 'flat' not in token and 'level' not in token and not any(s in token for s in roadkeywords) and 'floor' not in token and 'block' not in token and (self.holding == "" or self.name == "") and not any(token.lower().strip() == subarea.lower().strip() for subarea in subarealist) and self.housekey == "" and not any(token.lower().strip() == subarea.lower().strip() for subarea in subarealist) and not any(token.lower().strip() == area.lower().strip() for area in arealist) and token.split()[0] != 'house':
                if 'residential' in ptype:
                    self.holding = token
                    multiple_name.append(token)
                else:
                    self.name = token
                    multiple_name.append(token)
            elif 'house' in token:
                self.housekey = token
            elif any(s in token for s in roadkeywords):
                self.roadkey = token
                multiple_road.append(token)
            elif 'block' in token:
                self.blockkey = token
            elif 'flat' in token or 'floor' in token or 'level' in token:
                self.floorkey = token
            elif ('block' not in token and not any(s in token for s in roadkeywords) and 'house' not in token and 'floor' not in token and 'level' not in token and token.strip().lower() != 'dhaka' and 'flat' not in token) and any(token.lower().strip() == subarea.lower().strip() for subarea in subarealist):
                self.subareakey = token
                self.multiple_subarea.append(token.strip())
                try:
                    if not re.match('house\s+\d+', parsed_aadr[i-1]) and 'flat' not in parsed_aadr[i-1] and 'level' not in parsed_aadr[i-1] and not any(s in parsed_aadr[i-1] for s in roadkeywords) and 'floor' not in parsed_aadr[i-1] and 'block' not in parsed_aadr[i-1] and (self.holding == "" or self.name == "") and not any(parsed_aadr[i-1].lower().strip() == subarea.lower().strip() for subarea in subarealist) and self.housekey != "" and parsed_aadr[i-1].split()[0] != 'house':
                        self.ssarea = parsed_aadr[i - 1].strip()
                except Exception as e:
                    print(e)
                    pass

            #print(str(idx)+" "+token)
            print(i)
            idx += 1
        if len(multiple_name) > 1 and ptype != 'residential':
            self.name = multiple_name[0]
            self.holding = multiple_name[1]
        if self.subareakey == "":
            token = parsed_aadr[len(parsed_aadr)-1].strip()
            if (not any(s in token for s in roadkeywords) and 'house' not in token and 'floor' not in token and token.strip().lower() != 'dhaka' and 'level' not in token and 'flat' not in token and 'block' not in token):
                self.subareakey = token
                self.multiple_subarea.append(token.strip())

        if self.ssarea == "":
            self.ssarea = self.blockkey
        temp_roadkey = ""
        if len(multiple_road) > 1:
            for i in multiple_road:
                temp_roadkey = temp_roadkey+", "+i
            self.roadkey = temp_roadkey.strip(',').strip()
        obj = {
            'holding': self.name,
            'house': self.housekey,
            'floor': self.floorkey,
            'road': self.roadkey,
            'block': self.blockkey,
            'ssarea': self.ssarea,
            'subarea': self.subareakey,
            'multiple_subarea': self.multiple_subarea,
        }
        self.name = ""
        self.holding = ""
        self.housekey = ""
        self.floorkey = ""
        self.roadkey = ""
        self.blockkey = ""
        self.ssarea = ""
        self.subareakey = ""
        self.multiple_subarea = []
        return obj
