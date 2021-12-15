from dbconf.initdb import DBINIT
dbinit = DBINIT()
dbinit.load_area_with_regex()
dbinit.load_area()
dbinit.load_subarea()
dbinit.load_dsu()

print('data loaded')
area_regex=dbinit.get_area_with_regex()
area=dbinit.get_area()
subarea=dbinit.get_subarea()
dsu=dbinit.get_dsu()

def get_area_with_regex():
    return area_regex
def get_area():
    return area
def get_subarea():
    return subarea
def get_dsu():
    return dsu

