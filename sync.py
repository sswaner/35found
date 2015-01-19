import os
import boto
c = boto.connect_s3()
# substitute your bucket name here
from boto.s3.key import Key
import hashlib
import sqlite3
import datetime
conn = sqlite3.connect('35found.db', check_same_thread = False)

def hashfile(afile, hasher, blocksize=65536):
	# SO 3431825
	buf = afile.read(blocksize)
	while len(buf) > 0:
		hasher.update(buf)
		buf = afile.read(blocksize)
	return hasher.hexdigest()

def put(file, name, bucket, subdir = None):
	b = c.get_bucket(bucket) 
	try:
		k = Key(b)
		if subdir:
			k.key = '{0}/{1}'.format(subdir, name)
		else:
			k.key = name
		k.set_contents_from_filename(filename=file, reduced_redundancy=True)
		k.set_canned_acl('public-read')
	except:
		raise
	return True

def sync_dir(path, bucket, subdir = None):
	c = conn.cursor()
	for each in os.listdir(path):
		name = os.path.join(path, each)
		if os.path.isdir(name) != True:
			digest = hashfile(open(name, 'rb'), hashlib.sha256())
			c.execute("SELECT digest from digest where file = ?;", (name, ))
			record = c.fetchone()
			if record:
				old_digest = record[0]
			else:
				old_digest = None
			if old_digest is not None:
				if digest != old_digest:
					print(name + " has changed!")
					# SYNC THE FILE, THEN UPDATE
					sync = put(name, each, bucket,  subdir)
					if sync:
						c.execute("UPDATE digest SET digest = ?, last_update = ? where file = ?",
							(digest, datetime.datetime.now(), name))
					else:
						print("sync failed on : " + name)
			else:
				print("New file found: " + name)
				c.execute("INSERT INTO digest VALUES (? , ?, ?);", 
					(name, digest, datetime.datetime.now()))
				sync = put(name, each, bucket,  subdir)
				if sync:
					c.execute("UPDATE digest SET digest = ?, last_update = ? where file = ?",
						(digest, datetime.datetime.now(), name))
				else:
					print("sync failed on : " + name)
			# print(name)
			# print(digest)
		else:
			print(each + "is a dir")
	conn.commit()
synclist = [("/Users/shawnswaner/35found/build/page",
			"www.35found.com", "/page"),
			("/Users/shawnswaner/35found/build/tags",
			"www.35found.com", "/tags"),
			("/Users/shawnswaner/35found/build",
			"www.35found.com", None),
			("/Users/shawnswaner/35found/build/static",
			"www.35found.com", "/static"),
			("/Users/shawnswaner/35found/build/static/js",
			"www.35found.com", "/static/js"),
			("/Users/shawnswaner/35found/build/static/css",
			"www.35found.com", "/static/css"),
			("/Users/shawnswaner/35found/resized",
			"35found", "/thumbnail")
			]
def sync():
	for path, bucket, directory in synclist:
		# sync_dir("/Users/shawnswaner/35found/build/page", "www.35found.com", "/page")
		sync_dir(path, bucket, directory)

if __name__ == '__main__':
	sync()