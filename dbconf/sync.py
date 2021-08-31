import mysql.connector
import sqlite3
def getdb():
    mydb = mysql.connector.connect(host='db.barikoi.com',user='barikoiadmin',passwd='Amitayef5.7',database='ethikana',raise_on_warnings=True)
    return mydb

def load_thana_main():
    mydb=getdb()
    querycursor = mydb.cursor(buffered=True)
    querycursor.execute("SELECT DISTINCT thana,adm2_en from thanas;")
    gotAddress = querycursor.fetchall()
    print(len(gotAddress))
    return gotAddress
def load_thana_local():
    conn = sqlite3.connect('dbconf/outfile.db')  
    c = conn.cursor()
    c.execute('''
    SELECT DISTINCT `Barikoi subdistrict`, `district`
    FROM dsu_shopup_mapping
    ''')
    result = c.fetchall()
    print(len(result))
    return result

thana_list_main=load_thana_main()
thana_list_local=load_thana_local()
c=0
for thana_l in thana_list_main:
    check=0
    for thana_m in thana_list_local:
        if thana_l[0]==thana_m[0] and thana_l[0]==thana_m[0]:
            check=1
            break
    if check==0:
        print(thana_l)
        c+=1
print(c)