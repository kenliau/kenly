#all the imports
from __future__ import with_statement
from contextlib import closing
import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash

# configuration
DATABASE = '/tmp/kenly.db'
#DEBUG = True
SECRET_KEY = 'u5\xfa&Hm|\xe7\x8f\xa2\x9cH\xe62K\x18\xb1X\xf1\xd7\x04\xa8\xf6\x9c'
USERNAME = 'admin'
PASSWORD = 'default'


app = Flask(__name__)
app.config.from_object(__name__)

@app.route("/")
def index():
  print 'index'
  return "Index Page!"

@app.route("/hello")
def hello():
  return "Hello World!"

@app.route("/test")
def hello():
  return "Test!"


def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql') as f:
            db.cursor().executescript(f.read())
        db.commit()

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()

if __name__ == "__main__":
  # Bind to PORT if defined, otherwise default to 5000.
  port = int(os.environ.get('PORT', 5000))
  app.run(host='0.0.0.0', port=port)
