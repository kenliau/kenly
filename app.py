#all the imports
from __future__ import with_statement
from contextlib import closing
import os
import sqlite3
import urlparse
import httplib
import random
import string
import admin
import MySQLdb as mdb
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash

# configuration
RESERVED = ['login', 'logout', 'result', 'list']
url_dict = {}
hotness_dict = {}

app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = admin.secret_key#os.environ['secret_key']

@app.route("/")
def index():
    setup_db()
    return render_template('index.html')

@app.route("/result/", methods=['POST'])
def add_urls():
    setup_db()
    result = 'Here is your ken.lified URL!'
    broken_url = False
    if request.method == 'POST':
        user_url = request.form['url']
        if user_url.startswith('http://') or user_url.startswith('https://'):
            pass  
        else:
            user_url = 'http://' + user_url

        valid_url = check_url(user_url)
        
        if valid_url == False:
            broken_url = True

    if broken_url:
        result = "The URL is not valid! Make sure it has valid protocol and domain name."
        return render_template('result.html', result=result)

    #url is valid. Adding to database
    if user_url in url_dict:
        random_chars = update_db_hotness(user_url)
        redirect_url = request.url_root + random_chars

    else:
        random_chars = random_characters()
        while random_chars in url_dict.values() or random_chars in app.config['RESERVED']:
            random_chars = random_characters()
        insert_to_db(user_url, random_chars)

        redirect_url = request.url_root + random_chars

    return render_template('result.html', result=result, url=user_url, redirect_url=redirect_url)

@app.route("/<string:redirect_id>/")
def redirection(redirect_id):
    setup_db()
    if redirect_id in url_dict.values():
        redirect_url = find_key(url_dict, redirect_id)
        return redirect(redirect_url)
    else:
        abort(404)

@app.route('/login/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != admin.username:#os.environ['username']:
            error = 'Invalid username'
        elif request.form['password'] != admin.password:#os.environ['password']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            #shows table of urls
            return redirect(url_for('show_urls'))
    return render_template('login.html', error=error)


@app.route('/list/')
def show_urls():
    setup_db()
    #if not session.get('logged_in'):
    #    return redirect(url_for('login'))
    return render_template('table.html', host=request.url_root, urls=url_dict, hotness=hotness_dict) 

@app.route('/logout/')
def logout():
    # remove the username from the session if it's there
    session.pop('logged_in', None)
    return redirect(url_for('index'))

@app.errorhandler(404)
def page_not_found(error):
    return render_template('error.html'), 404

@app.errorhandler(405)
def page_not_found(error):
    return render_template('error.html'), 405

def find_key(dic, val):
    return [k for k, v in dic.iteritems() if v == val][0]


def random_characters():
    n = random.choice('1234567')
    return ''.join(random.choice(string.letters) for i in range(int(n)))

def setup_db():
    SELECT_QUERY = "SELECT * FROM links"
    db = mdb.connect(host="localhost", user="kenliau", db="kenliau")
    cursor = db.cursor()
    cursor.execute(SELECT_QUERY)
    while True:
        result = cursor.fetchone()
        if not result: 
            break
        u = result[1]
        r = result[2]
        h = result[3]
        url_dict[u] = r
        hotness_dict[u] = int(h)

    cursor.close()
    db.close()

def update_db_hotness(user_url):
    db = mdb.connect(host="localhost", user="kenliau", db="kenliau")
    cursor = db.cursor()
    UPDATE_QUERY = """UPDATE links SET hotness = hotness + 1 WHERE url = %s"""
    try:
        cursor.execute(UPDATE_QUERY, (user_url))
        db.commit()
    except:
        db.rollback()

    SELECT_QUERY = """SELECT redirect from links WHERE url = %s"""
    cursor.execute(SELECT_QUERY, (user_url))
    result = cursor.fetchone()
    if result:
        redirect = result[0]
    cursor.close()
    db.close()
    return redirect

def insert_to_db(user_url, random):
    db = mdb.connect(host="localhost", user="kenliau", db="kenliau")
    cursor = db.cursor()
    INSERT_QUERY = """INSERT INTO links (url, redirect, hotness) VALUES (%s, %s, %s)"""
    try:
        cursor.execute(INSERT_QUERY, (user_url, random, 1))
        db.commit()
    except:
        db.rollback()

    cursor.close()
    db.close()


def get_server_status_code(url):
    # http://stackoverflow.com/questions/1140661
    host, path = urlparse.urlparse(url)[1:3]    # elems [1] and [2]
    try:
        conn = httplib.HTTPConnection(host)
        conn.request('HEAD', path)
        return conn.getresponse().status
    except StandardError:
        return None
    except httplib.HTTPException:
        return None
    except httplib.ImproperConnectionState:
        return None

def check_url(url):
    # see also http://stackoverflow.com/questions/2924422
    good_codes = [httplib.OK, httplib.FOUND, httplib.MOVED_PERMANENTLY]
    status = get_server_status_code(url)
    #print 'status is ' + str(status)

    return status in good_codes


if __name__ == "__main__":
  # Bind to PORT if defined, otherwise default to 5000.
  # port = int(os.environ.get('PORT', 5000))
  # app.run(host='0.0.0.0', port=port)
  app.run()
