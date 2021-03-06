from flask import Flask, Response, request, session, g, redirect, url_for, abort, render_template, flash
import sqlite3
import utility
from collections import namedtuple
import datetime
from datetime import timedelta
import random

conn = sqlite3.connect('35found.db', detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread = False)

app = Flask(__name__)
app.config.from_object(__name__)

def dumpform(form):
    r = ""
    for index, item in enumerate(form):
        r = r + '{0}{1}:{2}|'.format(index, item, form[item])
    return r

def set_tags(tags, post_id):
	c = conn.cursor()
	c.execute("BEGIN TRANSACTION")
	c.execute("delete from tag_post where post_id = ?", (int(post_id), ))
	for tag in tags.split(';'):
		print(tag.strip())
		c.execute("INSERT OR IGNORE INTO tag values(?);", (tag.strip(), ))
		c.execute("INSERT OR IGNORE into tag_post values (?, ?);", (tag.strip(), post_id))
	conn.commit()
		
def get_tags(post_id):
	c = conn.cursor()
	c.execute("select tag from tag_post where post_id = ?;", (post_id, ))
	tags = c.fetchall()
	return tags

def get_post(post_id):
	p = {}
	c = conn.cursor()
	c.execute("""select title, body, publish_date, page, slide_url 
					from post where id = ?""", (post_id, ))
	r = c.fetchone()
	if r is None:
		return None
	p['title'] = r[0]
	p['body'] = r[1]
	p['publish_date'] = r[2]
	p['page'] = r[3]
	p['url'] = r[4]
	if p == []: return None
	else: return p 
	
@app.route('/add_entry', methods=['GET', 'POST'])
def add_entry():
	if request.method == 'GET':
		unpublished_slides = utility.get_unused_slides(conn)
		c = conn.cursor()
		c.execute("select max(publish_date) from post;")
		
		# 2015-01-01 03:19:00
		current_lead_date = datetime.datetime.strptime(c.fetchone()[0], '%Y-%m-%d %H:%M:%S')
		rand_hours = random.randrange(5, 25)
		rand_minutes = random.randrange(1, 59)
		suggested_time = current_lead_date + timedelta(hours=rand_hours) + timedelta(minutes=rand_minutes)
		return render_template('blog-entry.html', action = '/add_entry', 
				url = 'https://s3.amazonaws.com/35found/thumbnail/',
				slides = unpublished_slides,
				date = suggested_time)
	
	else:
		c = conn.cursor()
		c.execute("select max(id) from post;")
		r = c.fetchone()
		new_id = r[0] + 1

		publish_date = request.form['publish_date']

		
		page = int((new_id / 5) + 1)
		try:
			c.execute("""INSERT into post (id, title, body, publish_date, slide_url, page) 
					values (?, ?, ?, ?, ?, ?)""", (new_id, 
						request.form['title'],
						request.form['body'], 
						request.form['publish_date'], 
						request.form['slide_url'],
						page))
			conn.commit()
		except:
			raise
		set_tags(request.form['tags'], new_id)
		return redirect(url_for(".detail", post_id=str(new_id)))
		return dumpform(request.form)

@app.route('/')
def index():
	c = conn.cursor()
	c.execute("""select id, title, body, slide_url, publish_date
					from post  where publish_date <= datetime('now') 
					order by id desc LIMIT 4""")
	posts = c.fetchall()
	page_data = {}
	c.execute("select max(page) from post where publish_date <= datetime('now') ;")
	last_page = c.fetchone()[0]



	return render_template("page.html", posts = posts, 
		page_title = "Recent Posts", last_page = last_page, current_page = last_page)


@app.route('/<int:post_id>/edit', methods=['GET', 'POST'])
def edit_post(post_id):
	if request.method == 'GET':
		tag_list = get_tags(post_id)
		tags = '; '.join([x[0] for x in tag_list])
		try:
			p = get_post(post_id)
		except Exception:
			raise
			return abort(404)
		if not p:
			print('No data')
			return abort(404)
		return render_template('blog-entry.html', 
			title = p['title'], 
			body = p['body'],
			url = p['url'], 
			date = p['publish_date'], 
			action='/{0}/edit'.format(str(post_id)),
			tags = tags,
			mode = 'edit')
	else:
		c = conn.cursor()
		try:
			c.execute("""update post set title = ?, body = ?, publish_date = ?,
						 slide_url = ? where id = ?""", (request.form['title'],
						 	request.form['body'],
						 	request.form['publish_date'],
						 	request.form['slide_url'],
						 	post_id))
			conn.commit()
		except:
			raise
		set_tags(request.form['tags'], post_id)
		return redirect(url_for(".detail", post_id=str(post_id)))

@app.route('/<int:post_id>.html')
def detail(post_id):
	tag_list = get_tags(post_id)
	tags = [x[0] for x in tag_list]
	try:
		p = get_post(post_id)
	except Exception:
		print("database error")
		raise
		return abort(404)
	if p is None:
		print("Nothing returned")
		return abort(404)
	c = conn.cursor()
	c.execute("select max(page) from post where publish_date <= datetime('now');")
	last_page = c.fetchone()[0]
	c.execute("select max(id) from post where publish_date <= datetime('now');")
	last_id = c.fetchone()[0]
	return render_template('post-detail.html', title = p['title'], body = p['body'],
			url = p['url'], date = p['publish_date'], tags = tags, 
			last_id = last_id, current_id = post_id,
			last_page = last_page, 
			current_page = p['page'], show_page_control = 1), 200, {'Content-Type': 'text/html; charset=utf-8'}

@app.route('/tags.html')
def list_tags():
	c = conn.cursor()
	c.execute("""select tag, count(post_id) from tag_post where tag in (select tag from tag_post t 
		inner join post p on t.post_id = p.id 
		 where publish_date <= datetime('now')) and tag != '' group by tag order by tag;""")
	rows = c.fetchall()
	return render_template("tags.html", tags = rows, current_page = 1, last_page = 1, show_page_control = 0)

@app.route('/tags/<tag>.html')
def tag_matches(tag):
	c = conn.cursor()
	c.execute("""select id, title, body, publish_date 
		from post p 
		inner join tag_post t on p.id = t.post_id 
		where t.tag = ? and p.publish_date <= datetime('now') ;""", (tag, ))
	rows = c.fetchall()
	if rows:
		return render_template("tag_post.html", posts = rows, tag = tag)
	else:
		return abort(404)

@app.route('/page/<int:page>.html')
def load_page(page):
	c = conn.cursor()
	c.execute("""select id, title, body, slide_url, publish_date
					from post where page = ? and publish_date <= datetime('now') 
					order by publish_date desc;"""
					, (page, ))
	posts = c.fetchall()
	page_data = {}
	c.execute("select max(page) from post where publish_date <= datetime('now');")
	last_page = c.fetchone()[0]
	return render_template("page.html", posts = posts, 
		last_page = last_page, 
		current_page = page,
		show_page_control = 1)

@app.route('/faq.html')
def faq():
	return render_template("faq.html")

@app.route('/search.html')
def search():
	return render_template("search.html")

@app.route('/rss.xml')
def rss():
	Post = namedtuple("Post", ['id', 'title', 'slide_url', 'publish_date', 'page', 'body'])
	def post_desc(post):
		return """
		<p>{post.body}</p>
		<img src="{post.slide_url}" />
		""".format(post = post)
	c = conn.cursor()
	rs = c.execute("""select id, title, slide_url, publish_date, page, body 
		from post where publish_date <= datetime('now') order by id desc;""").fetchall()
	# print ([(l, type(l)) for l in rs[0]])
	posts = [Post(*r) for r in rs]
	posts = [(p, post_desc(p)) for p in posts]
	
	return render_template("rss.xml", datetime = datetime.datetime, 
		date_format = '%a, %d %b %Y %H:%M:%S GMT', posts = posts ), 200, {'Content-Type': 'application/rss+xml; charset=utf-8'}


if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0')