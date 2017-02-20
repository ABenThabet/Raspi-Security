import MySQLdb
import time
new_path='/var/www/final/visitors/person_5'
db = MySQLdb.connect(host="localhost", # your host, usually localhost
                     user="root", # your username
                      passwd="raspberry", # your password
                      db="raspberry") # name of the data base
	# you must create a Cursor object. It will let
	#  you execute all the queries you need
cur = db.cursor() 
cur.execute("INSERT INTO visitors (`name`, `nb_visits`, `last_visit`, `folder`, `pre`) VALUES ('---','1',%s,%s,'1')",((time.strftime("%Y/%m/%d"),new_path)))
db.commit()