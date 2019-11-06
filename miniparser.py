import re
roadkeywords=['road' , 'ave' , 'lane' , 'sarani' , 'soroni' , 'rd#' , 'sarak' , 'sharak' , 'shorok' , 'sharani' , 'highway' , 'path' , 'poth' , 'chowrasta' , 'sarak' , 'rasta' , 'sorok' , 'goli' , 'street' , 'line']
class MiniParser(object):
    def __init__(self):
        self.roadkey=""
        self.blockkey=""
        self.housekey=""
        self.name=""
        self.floorkey=""
        self.subareakey=""
    
    def parse(self, parsed_aadr):
    
      ge_addr='house 27/a, Road 5, Block F, Rupanagr, Mirpur'
      parsed_aadr=parsed_aadr.lower()
      parsed_aadr=parsed_aadr.split(',')
      parsed_aadr[0]=parsed_aadr[0].strip()
      if not re.match('house\s+\d+',parsed_aadr[0]) and 'flat' not in parsed_aadr[0] and 'level' not in parsed_aadr[0] and 'floor' not in parsed_aadr[0]:
        self.name=parsed_aadr[0]
        parsed_aadr.pop(0)
      for token in parsed_aadr:
        if 'house' in token:
          token=token.strip()
          self.housekey=token.strip()
      
        elif any(s in token for s in roadkeywords):
          self.roadkey=token.strip()
        elif 'block' in token:
          self.blockkey=token.strip()
        elif 'flat' in token or 'floor' in token or 'level' in token:
          self.floorkey=token.strip()
      
        elif 'block' not in token and not any(s in token for s in roadkeywords) and 'house' not in token and 'floor' not in token and 'level' not in token and 'flat' not in token:
          self.subareakey=token.strip()
      obj = {
        'house': self.housekey,
        'holding': self.name,
        'floor': self.floorkey,
        'road': self.roadkey,
        'block': self.blockkey,
        'Subarea': self.subareakey,
      }
      self.roadkey=""
      self.blockkey=""
      self.housekey=""
      self.name=""
      self.floorkey=""
      self.subareakey=""
      return obj

  