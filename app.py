#all the imports
from __future__ import with_statement
from contextlib import closing
import os
import sqlite3
import urlparse
import httplib
import sys
import random
import string
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash

# configuration
DATABASE = '/tmp/kenly.db'
RESERVED = ['login', 'logout', 'result', 'list']
#url_dict = {'http://www.google.com': 'login'}
#hotness_dict = {'http://www.google.com': 1}
url_dict = {'http://kennyliau.com': 'k', 'http://goneill.net': 'g'}
hotness_dict = {'http://kennyliau.com': 100, 'http://goneill.net': 1}

app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = os.environ['secret_key']

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
        h = hotness_dict[user_url]
        h = h + 1
        hotness_dict[user_url] = h
        random_chars = url_dict[user_url]
        redirect_url = request.url_root + random_chars

    else:
        random_chars = random_characters()
        while random_chars in url_dict.values() or random_chars in app.config['RESERVED']:
            random_chars = random_characters()
        url_dict[user_url] = random_chars
        hotness_dict[user_url] = 1
        redirect_url = request.url_root + random_chars

    return render_template('result.html', result=result, url=user_url, redirect_url=redirect_url)

@app.route("/<string:redirect_id>/")
def redirection(redirect_id):

    if redirect_id in url_dict.values():
        redirect_url = find_key(url_dict, redirect_id)
        return redirect(redirect_url)
    else:
        abort(404)

@app.route('/login/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != os.environ['username']:
            error = 'Invalid username'
        elif request.form['password'] != os.environ['password']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            #shows table of urls
            return redirect(url_for('show_urls'))
    return render_template('login.html', error=error)


@app.route('/list/')
def show_urls():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
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

'''
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
'''

def get_server_status_code(url):
    """
    Download just the header of a URL and
    return the server's status code.
    """
    # http://stackoverflow.com/questions/1140661
    host, path = urlparse.urlparse(url)[1:3]    # elems [1] and [2]
    try:
        print 'uno'
        sys.stdout.flush()
        conn = httplib.HTTPConnection(host)
        print 'dos'
        sys.stdout.flush()
        conn.request('HEAD', path)
        print 'tres'
        sys.stdout.flush()
        return conn.getresponse().status
    except StandardError:
        return None
    except httplib.HTTPException:
        return None
    except httplib.ImproperConnectionState:
        print 'here it is'
        sys.stdout.flush()
        return None

def check_url(url):
    """
    Check if a URL exists without downloading the whole file.
    We only check the URL header.
    """
    # see also http://stackoverflow.com/questions/2924422
    good_codes = [httplib.OK, httplib.FOUND, httplib.MOVED_PERMANENTLY]
    return get_server_status_code(url) in good_codes


if __name__ == "__main__":
  # Bind to PORT if defined, otherwise default to 5000.
  port = int(os.environ.get('PORT', 5000))
  app.run(host='0.0.0.0', port=port)
