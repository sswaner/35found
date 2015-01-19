from flask_frozen import Freezer
from _35found import app
import sqlite3
import sync
freezer = Freezer(app)

conn = sqlite3.connect('35found.db', check_same_thread = False)



@freezer.register_generator
def post_url_generator():  # Some other function name
    # `(endpoint, values)` tuples
    c = conn.cursor()
    c.execute("select max(id) from post where publish_date <= datetime('now');")

    max_page = c.fetchone()[0]
    for x in range(1, max_page + 1):
    	yield 'detail', {'post_id': str(x)}
    
@freezer.register_generator
def page_url_generator():  # Some other function name
    # `(endpoint, values)` tuples
    c = conn.cursor()
    c.execute("select max(page) from post where publish_date <= datetime('now');")

    max_page = c.fetchone()[0]
    print(max_page)
    for x in range(1, max_page + 1):
    	yield 'load_page', {'page': str(x)}


@freezer.register_generator
def tag_url_generator():  # Some other function name
    # `(endpoint, values)` tuples
    c = conn.cursor()
    c.execute("""select distinct(tag) from tag_post where tag in 
    	(select tag from tag_post t inner join post p on t.post_id = p.id 
		 where publish_date <= datetime('now')) and tag != '';""")

    tags = c.fetchall()
    for tag in tags:
    	yield 'tag_matches', {'tag': tag[0]}
    

if __name__ == '__main__':
    freezer.freeze()
    sync.sync()