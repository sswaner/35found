from flask import Flask, request, g, abort
import sqlite3
import json
from collections import defaultdict

app = Flask(__name__)

DB = "tags.db"
SCHEMA = "tags.schema"

def startup():
    conn = sqlite3.connect(DB)
    with open(SCHEMA) as s:
        conn.executescript(s.read())
    conn.close()

@app.before_request
def setup():
    g.conn = sqlite3.connect(DB)
    g.conn.execute("PRAGMA foreign_keys = ON");

@app.after_request
def teardown(resp):
    g.conn.close()
    return resp

def page_ensure(curs, url):
    curs.execute("INSERT OR IGNORE INTO page (url) VALUES (?)", [url])

def page_prune(curs):
    curs.execute("""
    DELETE FROM page WHERE
        (select count(*) from tag WHERE pid = id) < 1
    """)

def tags_all(curs):
    curs.execute("""
    SELECT p.url, t.tag FROM tag as t
        JOIN page as p on p.id = t.pid
    """)
    results = defaultdict(set)
    for (url, tag) in curs.fetchall():
        results[url].add(tag)
    return results

def tags_for(curs, url):
    curs.execute("""
    SELECT tag from tag as t
        JOIN page as p on p.id = t.pid
        WHERE p.url = ?
    """, [url])
    return [tag for [tag] in curs.fetchall()]

def urls_for(curs, tag):
    curs.execute("""
    SELECT url FROM page as p
        JOIN tag as t on p.id = t.pid
        WHERE t.tag = ?
    """, [tag])
    return [t for [t] in curs.fetchall()]

def tags_push(curs, url, tags):
    curs.executemany("""
    INSERT INTO tag VALUES (
        (select id from page where url = ?), ?
    )
    """, [(url, t) for t in tags])

def tags_pop(curs, url, tags):
    curs.executemany("""
    DELETE FROM tag WHERE 
        pid = (SELECT id FROM page WHERE url = ?)
    and tag = ?
    """, [(url, t) for t in tags])

def tags_clear(curs, url):
    curs.execute("""
    DELETE FROM tag WHERE
        pid = (SELECT id from page WHERE url = ?)
    """, [url])

@app.route("/tags.json", methods=["GET"])
def tags():
    curs = g.conn.cursor()
    if "url" in request.args:
        result = tags_for(curs, request.args["url"])
        if len(result) == 0: abort(404)
    else:
        result = {}
        for (key, tags) in tags_all(curs).iteritems():
            result[key] = list(tags)
    curs.close()
    return json.dumps(result), 200, { "Content-Type": "application/json" }

@app.route("/tags.json", methods=["POST"])
def add_tags():
    tags = json.load(request.stream)
    if len(tags) < 1: abort(400)
    curs = g.conn.cursor()
    page_ensure(curs, request.args["url"])
    tags_push(curs, request.args["url"], tags)
    page_prune(curs)
    curs.close()
    g.conn.commit()
    return "", 200, {}

@app.route("/tags.json", methods=["DELETE"])
def remove_tags():
    body = request.stream.read()
    tags = []
    if body == "":
        op = lambda curs, url, ts: tags_clear(curs, url)
    else:
        tags = json.load(request.stream)
        op = tags_pop
        if len(tags) < 1: abort(400)

    curs = g.conn.cursor()
    page_ensure(curs, request.args["url"])
    op(curs, request.args["url"], tags)
    page_prune(curs)
    curs.close()
    g.conn.commit()

    return "", 200, {}

@app.route("/tags/<tag>/pages.json", methods=["GET"])
def query_pages(tag):
    curs = g.conn.cursor()
    result = dict(pages = urls_for(curs, tag))
    if len(result["pages"]) == 0: abort(404)
    curs.close()
    return json.dumps(result), 200, {"Content-Type": "application/json" }

if __name__ == "__main__":
    startup()
    app.debug = True
    app.run()
