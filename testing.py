import unittest


from bkoi_parser import Address 
parse = Address()
class TestAddress(unittest.TestCase):
    def test_input_address(self):
        self.assertEqual(parse.parse_address('h2 r-5 block no G sec 2 mirpur')['address'], 'house 2, road 5, block g, section 2, mirpur')
        self.assertEqual(parse.parse_address('h9 namapara khilkhet')['address'], 'house 9, namapara, khilkhet')
        self.assertEqual(parse.parse_address('h010 namapara manikdi')['address'], 'house 10, namapara, manikdi')
        self.assertEqual(parse.parse_address('h -98 khilkhet namapara manikdi')['address'], 'house 98, namapara, khilkhet')
        self.assertEqual(parse.parse_address('h:99 manikdi namapara khilkhet')['address'], 'house 99, namapara, manikdi')
        self.assertEqual(parse.parse_address('h:99 manikdi namapara khilkhet')['address'], 'house 99, namapara, manikdi')
        self.assertEqual(parse.parse_address('house gp cha 2,  , mohakhali')['address'], 'house gp-cha-2, mohakhali')
        self.assertEqual(parse.parse_address('h12 pallabi kaful')['address'], 'house 12, pallabi, mirpur')


if __name__ == '__main__':
    unittest.main()