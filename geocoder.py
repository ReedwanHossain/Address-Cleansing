from postal.parser import parse_address
print(parse_address('House 3, road 5, Sector 3 , Uttara'));
print(parse_address('House 3, road 5, Uttara 3, Dhaka-1230'));
print(parse_address('H 3, rd 5, Uttara 3'));
