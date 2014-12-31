from flask_frozen import Freezer
from _35found import app
import sqlite3

freezer = Freezer(app)

conn = sqlite3.connect('35found.db', check_same_thread = False)



@freezer.register_generator
def post_url_generator():  # Some other function name
    # `(endpoint, values)` tuples
    c = conn.cursor()
    c.execute("select max(id) from post;")

    max_page = c.fetchone()[0]
    for x in range(1, max_page + 1):
    	yield 'detail', {'post_id': str(x)}
    
@freezer.register_generator
def page_url_generator():  # Some other function name
    # `(endpoint, values)` tuples
    c = conn.cursor()
    c.execute("select max(page) from post;")

    max_page = c.fetchone()[0]
    print(max_page)
    for x in range(1, max_page + 1):
    	yield 'load_page', {'page': str(x)}


@freezer.register_generator
def tag_url_generator():  # Some other function name
    # `(endpoint, values)` tuples
    c = conn.cursor()
    c.execute("select tag from tag;")

    tags = c.fetchall()
    for tag in tags:
    	yield 'tag_matches', {'tag': tag[0]}
    

if __name__ == '__main__':
    freezer.freeze()