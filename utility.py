import boto
botoconn = boto.connect_s3()
from boto.s3.key import Key
import sqlite3

def get_unused_slides(conn):
	c = conn.cursor()
	c.execute("select slide_url from post;")

	published_slides = [x[0].replace('https://s3.amazonaws.com/35found/thumbnail/', '') 
		for x in c.fetchall()]

	b = botoconn.get_bucket('35found')
	keys = b.list(prefix="thumbnail/")

	x = [key.name.replace('thumbnail/', '') for key in keys 
		if key.name.replace('thumbnail/', '') not in published_slides ]

	return x