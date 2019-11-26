import unittest

import csv
from bkoi_parser import Address 
parse = Address()
class TestAddress(unittest.TestCase):
    def test_input_address(self):
        self.assertEqual(parse.parse_address('anything')['address'], 'anything')
        self.assertEqual(parse.parse_address('449B/2/A(1st Floor), Mokki Mosjid Goli, West Rampura,Dhaka-1219 ')['address'], 'house 449-b/2/a, mokki mosjid goli, west rampura, rampura')
        self.assertEqual(parse.parse_address('anything unnecessary')['address'], 'anything unnecessary')
        self.assertEqual(parse.parse_address('h2 r-5 block no G sec 2 mirpur')['address'], 'house 2, road 5, block g, section 2, mirpur')
        self.assertEqual(parse.parse_address('h9 namapara khilkhet')['address'], 'house 9, namapara, khilkhet')
        self.assertEqual(parse.parse_address('h010 namapara manikdi')['address'], 'house 10, namapara, manikdi')
        self.assertEqual(parse.parse_address('house gp cha 2,  , mohakhali')['address'], 'house gp-cha-2, mohakhali')
        self.assertEqual(parse.parse_address('h12 pallabi kaful')['address'], 'house 12, pallabi, mirpur')
        self.assertEqual(parse.parse_address('213/7(b),shapla housing, panir pamp er pashe,shamoli ,dhaka')['address'], 'house 213/7, shyamoli')
        self.assertEqual(parse.parse_address('House No. 5 (1st Floor), Road No. 9, Block- A, Nobodoy Housing Society, Mohammadpur, Dhaka -1207. Near Back West Side of Baitul Wahab Masjid of Road No. 6, Mohammadi Housing Society. ')['address'], 'house 5, road 9, road 6, block a, nobodoy housing, mohammadpur')
        self.assertEqual(parse.parse_address('mirpur 2  R -1,h- 3,B -d D cups coffee shop')['address'], 'house 3, road 1, block d, section 2, mirpur')
        self.assertEqual(parse.parse_address('67/2, GP Ja, Gajnabi Road 2, behind BRAC University (by a CNG Garage) Mohakhali Wirelessgate, Dhaka-1213')['address'], 'house 67/2-gp-ja, road 2, mohakhali wirelessgate, mohakhali')
        self.assertEqual(parse.parse_address('barikoi office b-F 32 mirpur')['address'], 'barikoi office, house 32, block f, mirpur')
    
    def test_geocoded_address(self):
    	#self.assertEqual(parse.parse_address('anything')['geocoded']['Address'], 'anything')
    	with open('./testfile.csv','rt') as f:
            addresses = csv.reader(f)
            for i , address in enumerate(addresses):
            	self.assertEqual(parse.parse_address(address[0])['geocoded']['Address'], address[1])


    	#self.assertEqual(parse.parse_address('h3 r4 mirpur 2')['geocoded']['Address'], 'House 3, Road 4, Block G, Section 2')
    	

    def test_unsolved_address(self):
        #self.assertNotEqual(parse.parse_address('449B/2/A(1st Floor), Mokki Mosjid Goli, West Rampura,Dhaka-1219 ')['address'], 'house 449-b/2/a, mokki mosjid goli, west rampura, rampura')
        self.assertNotEqual(parse.parse_address(' 60/1 haji abdul mojet lane, Laxmibazar, Dhaka')['address'], 'house 60/1, haji abdul mojet lane, luxmibazar')
        self.assertNotEqual(parse.parse_address(' Silicon Sunrise(Flat-3C), 385/A Free School Street, Hatirpool Pukurpar, Hatirpool')['address'], 'house 385/a, free school street, panthapath')
        self.assertNotEqual(parse.parse_address('House#807, Dag#845, Middle Badda, Bazar Road, Dhaka (2nd floor) At the side of EGARO SARANO gate')['address'], 'house 807, middle badda bazar road, middle badda, badda')
        self.assertNotEqual(parse.parse_address('13,shah ali bag.northern ahmed lodge.mirpur-1.')['address'], 'house 13, shah ali bagh, mirpur')
        self.assertNotEqual(parse.parse_address('House# 45 ,  Haider Garden , Mirpur road (near to the  Elephant road bridge)  , Sukonna tower er goli (or Basundhora goli) , Dhanmondi , Dhaka-1205')['address'], 'sukonna tower, house 45, mirpur road, dhanmondi')
        self.assertNotEqual(parse.parse_address('roof360 89 rokeya aveneu mrpur 11')['address'], 'roof360, house 89, rokeya avenue, section 11, mirpur')
        self.assertNotEqual(parse.parse_address('5/1 kallaynpur')['address'], 'House 5/1, Kallyanpur Main Road, Kallyanpur')

if __name__ == '__main__':
    unittest.main()