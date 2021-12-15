import unittest
import DSU_Parser

class TestStringMethods(unittest.TestCase):

    def test_similarity(self):
        self.assertEqual(DSU_Parser.similar('sojib','sojib'), 1)
    
    def test_result(self):
        first_string='matuuuuuuuuil'
        second_string='matooooel'

        self.assertEqual(DSU_Parser.result(first_string,second_string), True)

    def test_finalresult(self):
        first_string='haterjheel'
        second_string='hatir jheel'

        self.assertEqual(DSU_Parser.finalresult(first_string,second_string), True)

    def test_identifier1(self):
        input_string='shoriotpur kunderchor'
        #output=[{'Area': 'Mirpur', 'Subarea': 'Section 10', 'Super Subarea': 'None', 'Road': []}]
        output=[{'District': 'Shariatpur', 'Subdistrict': 'Zanjira', 'Union': 'Kunder Char'}]
        self.assertEqual(DSU_Parser.Identifier1(input_string), output)

    def test_identifier2(self):
        input_string='godagari'
        output=[{'District': 'Rajshahi', 'Subdistrict': 'Godagari', 'Union': 'Godagari'}]
        self.assertEqual(DSU_Parser.Identifier2(input_string), output)

    def test_identifier(self):
        input_string='dhaka cng pamp puthia'
        output={'Parsed': [{'District': 'Rajshahi', 'Subdistrict': 'Puthia', 'Union': 'Puthia'}]}
        self.assertEqual(DSU_Parser.Identifier(input_string), output)

    # def test_Api_parse(self):
    #     input_string='49/1A Baddanagar lane, Hazaribag, Dhaka 1205'
    #     response = self.main.post('/parse', headers={"addr": "Mirpur 10"})
    #     print(type(response))
        
    
if __name__ == '__main__':
    unittest.main()