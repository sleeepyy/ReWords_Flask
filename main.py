import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from word_process import process

app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig')


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    g.db = rv
    return rv

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'db'):
        connect_db()
    return g.db

@app.before_request
def prepare_db():
    get_db()

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'db'):
        g.db.close()

def init_db():
    with app.app_context():
        db = get_db()
        g.db = db
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.route('/')
def show_users():
    # get_db()
    cur = g.db.execute('select id, username from users order by id desc')
    entries = [dict(id=row[0], username=row[1]) for row in cur.fetchall()]
    return render_template('show_users.html', entries=entries)

@app.route('/add', methods=['POST'])
def add_user():
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('insert into users (id, username) values (?, ?)',
                 [request.form['id'], request.form['username']])
    g.db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_users'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    # get_db()
    if request.method == 'POST':
        
        cur = g.db.execute('select id from users where username=(?) and password=(?)', 
           (request.form['username'], request.form['password']))
        result = cur.fetchall()
        if len(result) == 1:
            flash('success')
            session['logged_in'] = True
            session['id'] = result[0][0]
            session['name'] = request.form['username']
            return redirect(url_for('show_users'))
        else:
            flash("Login failed. Pls check.")

        # if request.form['username'] != app.config['USERNAME']:
        #     error = 'Invalid username'
        # elif request.form['password'] != app.config['PASSWORD']:
        #     error = 'Invalid password'
        # else:
        #     session['logged_in'] = True
        #     flash('You were logged in')
        #     return redirect(url_for('show_users'))
    return render_template('login.html', error=error)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    # get_db()
    if request.method == 'POST':
        if request.form['username'] and request.form['password']:
            g.db.execute('insert into users (username, password) values (?, ?)',
                 [request.form['username'], request.form['password']])
            g.db.commit()
            flash('signup success!')
            return redirect(url_for('show_users'))
    return render_template('signup.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_users'))

@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)

if __name__ == '__main__':
    app.run(debug=True)