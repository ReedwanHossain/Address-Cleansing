import sqlite3
import json

class Operations(object):
	"""docstring for Operations"""
	def __init__(self):
		try:
			self.conn = sqlite3.connect('dbconf/TestDB.db')
			print("connected")
		except Exception as e:
			print(e)
			return None  
		
	def area_insert(self,area):
		area=area.strip().lower()
		c = self.conn.cursor()
		c.execute("SELECT * from AREA where  LOWER(`areaname`)='"+area+"'")
		check_result = c.fetchall()
		print(len(check_result))
		if len(check_result)>0:
			return "Already exist"
		else:
			try:
				c.execute(" INSERT INTO AREA(`areaname`) VALUES ('"+area+"')  ")
				self.conn.commit()
				print("successfully added")
				return "successfully added"
			except Exception as e:
				print(e)
				return "Error"

	def search_area(self,area):
		area=area.strip().lower()
		c = self.conn.cursor()
		c.execute("SELECT * from AREA where  LOWER(`areaname`) like ('"+area+"')")
		check_result = c.fetchall()
		area_dict_list = []
		for i,item in  enumerate(check_result):
			area_dict_list.append({'id':item[0],'areaname':item[1]})
		# check_result = [i for i in check_result]
		obj = {
			'area_list' : area_dict_list
		}
		return obj


	def delete_area(self,area_id):
		area_id=str(area_id)
		c = self.conn.cursor()
		c.execute("SELECT * from AREA where  `id`='"+area_id+"' ")
		check_result = c.fetchall()
		print(len(check_result))
		if len(check_result)<=0:
			return "Not Available"
		try:
			c.execute("DELETE from AREA where `id` = '"+area_id+"' ")
			self.conn.commit()
			return 'Area deleted'
		except Exception as e:
			print(e)
			return 'Error Occured'


	def area_update(self,area_id,area):
		area_id=str(area_id)
		area=area.strip().lower()
		c = self.conn.cursor()

		c.execute("SELECT * from AREA where `id`='"+area_id+"' ")
		check_result = c.fetchall()
		print('check check_result')
		print(check_result)
		if len(check_result)<=0:
			return "Not Available"
		else:
			try:
				c.execute("UPDATE AREA SET `areaname`='"+area+"' WHERE `id`='"+area_id+"' ")
				self.conn.commit()
				print("successfully updated")
				return "successfully updated"
			except Exception as e:
				print(e)
				return "Error"


	def subarea_insert(self,sa_area,sa_subarea,f_house,f_road,f_block,f_suparea,f_subarea):
		sa_area=sa_area.strip().lower()
		sa_subarea=sa_subarea.strip().lower()
		f_house=f_house.strip().lower()
		f_road=f_road.strip().lower()
		f_block=f_block.strip().lower()
		f_suparea=f_suparea.strip().lower()
		f_subarea=f_subarea.strip().lower()
		c = self.conn.cursor()
		c.execute("SELECT * from SUBAREA where  LOWER(`area`)='"+sa_area+"' and  lower(`subarea`)='"+sa_subarea+"'  ")
		check_result = c.fetchall()
		if len(check_result)>0:
			return "Already exist"
		else:
			try:
				c.execute(" INSERT INTO SUBAREA(`area`,`subarea`,`fhouse`,`froad`,`fblock`,`fsuparea`,`fsubarea`) VALUES ('"+sa_area+"','"+sa_subarea+"','"+f_house+"','"+f_road+"','"+f_block+"','"+f_suparea+"','"+f_subarea	+"' ) ")
				self.conn.commit()
				print("successfully added")
				return "successfully added"
			except Exception as e:
				print(e)
				return "Error"


	def search_subarea(self,subarea):
		subarea=subarea.strip().lower()
		c = self.conn.cursor()
		c.execute("SELECT * from SUBAREA where  LOWER(`area`) like ('"+subarea+"') or `subarea` like ('"+subarea+"')")
		check_result = c.fetchall()
		subarea_dict_list = []
		for i,item in  enumerate(check_result):
			subarea_dict_list.append({'id':item[0],'area':item[1],'subarea':item[2],'fhouse':item[3],'froad':item[4],'fblock':item[5],'fsuparea':item[6],'fsubarea':item[7]})
		# check_result = [i for i in check_result]
		obj = {
			'subarea_list' : subarea_dict_list
		}
		return obj


	def delete_subarea(self,subarea_id):
		subarea_id=str(subarea_id)
		c = self.conn.cursor()
		c.execute("SELECT * from SUBAREA where  `id`='"+subarea_id+"' ")
		check_result = c.fetchall()
		print(len(check_result))
		if len(check_result)<=0:
			return "Not Available"
		try:
			c.execute("DELETE from SUBAREA where `id` = '"+subarea_id+"' ")
			self.conn.commit()
			return 'Subarea deleted'
		except Exception as e:
			print(e)
			return 'Error Occured'


	def subarea_update(self,subarea_id,sa_area,sa_subarea,f_house,f_road,f_block,f_suparea,f_subarea):
		subarea_id=str(subarea_id)
		sa_area=sa_area.strip().lower()
		sa_subarea=sa_subarea.strip().lower()
		f_house=f_house.strip().lower()
		f_road=f_road.strip().lower()
		f_block=f_block.strip().lower()
		f_suparea=f_suparea.strip().lower()
		f_subarea=f_subarea.strip().lower()
		c = self.conn.cursor()
		print(subarea_id)
		c.execute("SELECT * from SUBAREA where `id`='"+subarea_id+"' ")
		check_result = c.fetchall()
		print('check check_result')
		print(check_result)
		if len(check_result)<=0:
			return "Not Available"
		else:
			try:
				c.execute("UPDATE SUBAREA SET `area`='"+sa_area+"',`subarea`='"+sa_subarea+"',`fhouse`='"+f_house+"',`froad`='"+f_road+"',`fblock`='"+f_block+"',`fsuparea`='"+f_suparea+"',`fsubarea`='"+f_subarea	+"' WHERE `id`='"+subarea_id+"' ")
				self.conn.commit()
				print("successfully updated")
				return "successfully updated"
			except Exception as e:
				print(e)
				return "Error"


	def dsu_insert(self,union,subdivision,division):
		union=union.strip().lower()
		subdivision=subdivision.strip().lower()
		division=division.strip().lower()
		c = self.conn.cursor()
		c.execute("SELECT * from DSU where  LOWER(`union`)='"+union+"' and  lower(`subdivision`)='"+subdivision+"' and  lower(`division`)='"+division+"' ")
		check_result = c.fetchall()
		if len(check_result)>0:
			return "Already exist"
		else:
			try:
				c.execute(" INSERT INTO DSU(`union`,`subdivision`,`division`) VALUES ('"+union+"','"+subdivision+"','"+division	+"' ) ")
				self.conn.commit()
				print("successfully added")
				return "successfully added"
			except Exception as e:
				print(e)
				return "Error"


	def dsu_update(self,dsu_id,union,subdivision,division):
		dsu_id=str(dsu_id)
		union=union.strip().lower()
		subdivision=subdivision.strip().lower()
		division=division.strip().lower()
		c = self.conn.cursor()
		c.execute("SELECT * from DSU where `id`='"+dsu_id+"' ")
		check_result = c.fetchall()
		if len(check_result)<=0:
			return "Not Available"
		else:
			try:
				c.execute("UPDATE DSU SET `union`='"+union+"',`subdivision`='"+subdivision+"',`division`='"+division+"' WHERE `id`='"+dsu_id+"' ")
				self.conn.commit()
				print("successfully updated")
				return "successfully updated"
			except Exception as e:
				print(e)
				return "Error"

	def search_dsu(self,dsu):
		dsu=dsu.strip().lower()
		c = self.conn.cursor()
		c.execute("SELECT * from DSU where  LOWER(`union`) like ('"+dsu+"') or `subdivision` like ('"+dsu+"') or `division` like ('"+dsu+"') ")
		check_result = c.fetchall()
		dsu_dict_list = []
		for i,item in  enumerate(check_result):
			dsu_dict_list.append({'id':item[0],'union':item[1],'subdivision':item[2],'division':item[3]})
		# check_result = [i for i in check_result]
		obj = {
			'dsu_list' : dsu_dict_list
		}
		return obj

	def delete_dsu(self,dsu_id):
		dsu_id=str(dsu_id)
		c = self.conn.cursor()
		c.execute("SELECT * from DSU where  `id`='"+dsu_id+"' ")
		check_result = c.fetchall()
		print(len(check_result))
		if len(check_result)<=0:
			return "Not Available"
		try:
			c.execute("DELETE from DSU where `id` = '"+dsu_id+"' ")
			self.conn.commit()
			return 'DSU deleted'
		except Exception as e:
			print(e)
			return 'Error Occured'

	def keyword_insert(self,en,bn,user_id):
		print(en)
		en=en.strip().lower()
		bn=bn.strip()
		c = self.conn.cursor()
		c.execute("SELECT * from KEYWORD_MAPLIST where  LOWER(`keyeng`)='"+en+"' and `keybn`='"+bn+"'  ")
		check_result = c.fetchall()
		print(len(check_result))
		if len(check_result)>0:
			return "Already exist"
		else:
			try:
				c.execute(" INSERT INTO KEYWORD_MAPLIST(`keyeng`,`keybn`,`corbang`,`blank`) VALUES ('"+en+"','"+bn+"','','"+user_id+"' ) ")
				self.conn.commit()
				print("successfully added")
				return "successfully added"
			except Exception as e:
				print(e)
				return "Error"


	def keyword_update(self,kw_id,en,bn,user_id):
		en=en.strip().lower()
		bn=bn.strip()
		c = self.conn.cursor()
		c.execute("SELECT * from KEYWORD_MAPLIST where  `id`='"+kw_id+"' ")
		check_result = c.fetchall()
		print(len(check_result))
		if len(check_result)<=0:
			return "Not Available"
		else:
			try:				
				c.execute("UPDATE KEYWORD_MAPLIST SET `keyeng`='"+en+"',`keybn`='"+bn+"',`blank`='"+user_id+"' WHERE `id`='"+kw_id+"' ")
				#c.execute(" INSERT INTO KEYWORD_MAPLIST(`keyeng`,`keybn`,`corbang`,`blank`) VALUES ('"+en+"','"+bn+"','','"+user_id+"' ) ")
				self.conn.commit()
				print("successfully updated")
				return "successfully updated"
			except Exception as e:
				print(e)
				return "Error"


	def search_keyword(self,en):
		en=en.strip().lower()
		c = self.conn.cursor()
		print(en)
		c.execute("SELECT * from KEYWORD_MAPLIST where  LOWER(`keyeng`) like ('"+en+"') or `keybn` like ('"+en+"')")
		check_result = c.fetchall()
		keyword_dict_list = []
		for i,item in  enumerate(check_result):
			keyword_dict_list.append({'id':item[0],'keyeng':item[1],'keybn':item[2],'corbang':item[3],'blank':item[4]})
		# check_result = [i for i in check_result]
		obj = {
			'keyword_list' : keyword_dict_list
		}
		return obj

	def delete_keyword(self,kw_id):
		kw_id=str(kw_id)
		c = self.conn.cursor()
		c.execute("SELECT * from KEYWORD_MAPLIST where  `id`='"+kw_id+"' ")
		check_result = c.fetchall()
		print(len(check_result))
		if len(check_result)<=0:
			return "Not Available"
		try:
			c.execute("DELETE from KEYWORD_MAPLIST where `id` = '"+kw_id+"' ")
			self.conn.commit()
			return 'Keyword deleted'
		except Exception as e:
			print(e)
			return 'Error Occured'