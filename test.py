import boto
botoconn = boto.connect_s3()
# substitute your bucket name here
from boto.s3.key import Key
# from boto.s3.bucket import Bucket
import hashlib
import sqlite3
import datetime

conn = sqlite3.connect('35found.db', check_same_thread = False)


c = conn.cursor()
c.execute("update post set publish_date = ? where id = 22;", (datetime.datetime.now(), ))
conn.commit()
rs = c.execute("select id, publish_date from post where publish_date <= datetime('now') ;").fetchall()

for (id, publish_date) in rs:
# 	try:
# 		print (publish_date)
# 		d = datetime.datetime.strptime(publish_date, '%m-%d-%y %H:%M:%S')
# 	except ValueError:
# 		print("publish_date failed to parse: ", publish_date)
# 		continue
# 	c.execute("update post set publish_date = ? where id = ?;", (d, id))
# 	print(id)
# 	print(d)
# 	print(publish_date)
# conn.commit()
	print (id, publish_date)

