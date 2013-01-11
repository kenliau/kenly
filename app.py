#all the imports
from __future__ import with_statement
from contextlib import closing
import os
import sqlite3
import urlparse
import httplib
import random
import string
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
    return render_template('index.html')


@app.route("/result/", methods=['POST'])
def add_urls():
    result = 'Here is your ken.lified URL!'
    broken_url = False
    #flash('testing')
    if request.method == 'POST':
        user_url = request.form['url']
        valid_url = check_url(user_url)
        if valid_url == False:
            broken_url = True

    if broken_url:
        result = "The URL is not valid! Make sure it has valid protocol and domain name."
        return render_template('result.html', result=result)

    

    
    return render_template('result.html', result=result, url=user_url)

@app.route("/url/<string:id>/")
def redirection(id):
    return render_template('redirection.html')


def get_server_status_code(url):
    """
    Download just the header of a URL and
    return the server's status code.
    """
    # http://stackoverflow.com/questions/1140661
    host, path = urlparse.urlparse(url)[1:3]    # elems [1] and [2]
    try:
        conn = httplib.HTTPConnection(host)
        conn.request('HEAD', path)
        return conn.getresponse().status
    except StandardError:
        return None

def check_url(url):
    """
    Check if a URL exists without downloading the whole file.
    We only check the URL header.
    """
    # see also http://stackoverflow.com/questions/2924422
    good_codes = [httplib.OK, httplib.FOUND, httplib.MOVED_PERMANENTLY]
    return get_server_status_code(url) in good_codes



def random_characters():
    return ''.join(random.choice(string.letters) for i in range(5))

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
