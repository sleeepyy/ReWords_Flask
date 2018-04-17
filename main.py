import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from util import words
import random

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
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()
        cet4_words = list(get_words.process_words('CET4.words').items())
        cet6_words = list(get_words.process_words('CET6.words').items())
        random.shuffle(cet4_words)
        random.shuffle(cet6_words)

        for word, translation in cet4_words:
            db.execute('insert into cet4 (word, translation) values (?, ?)', (word, translation))
        db.commit()
        for word, translation in cet6_words:
            db.execute('insert into cet6 (word, translation) values (?, ?)', (word, translation))
        db.commit()
        

def prepare_word(user_id, book):
    cur = g.db.execute('select book from userwords where id=(?)', str(user_id))
    books = cur.fetchall()
    if book in books:
        return
    else:
        del cur
        cur = g.db.execute('select word, translation from '+book)
        words = cur.fetchall()
        for word, translation in words:
            g.db.execute('insert into userwords (id, book, word, translation, review) values (?, ?, ?, ?, ?)', 
               (session['id'], book, word, translation, random.randint(0, 100)))
        g.db.commit()
        return
            

@app.route('/')
def home():
    cur = g.db.execute('select id, username from users order by id desc')
    entries = [dict(id=row[0], username=row[1]) for row in cur.fetchall()]
    return render_template('home.html', entries=entries)

@app.route('/words')
def get_words():
    cur = g.db.execute('select word, translation from userwords where id=(?) and book=(?) order by review', (str(session['id']), session['book']))
    words = [dict(word=row[0], translation=row[1]) for row in cur.fetchall()]
    return render_template('words.html', words=words)

@app.route('/word', methods=['GET', 'POST'])
def word():
    cur = g.db.execute('select word, translation from userwords where id=(?) and book=(?) order by review limit 1', (str(session['id']), session['book']))
    words = [dict(word=row[0], translation=row[1]) for row in cur.fetchall()]
    word = words[0]
    if request.method == 'POST':
        if request.form['submit'] == '记得':
            g.db.execute('update userwords set review = review+10 where id=(?) and book=(?) and word=(?)', (str(session['id']), session['book'], word['word']))
        if request.form['submit'] == '忘记':
            g.db.execute('update userwords set review= review+5 where id=(?) and book=(?) and word=(?)', (str(session['id']), session['book'], word['word']))
        g.db.commit()
        cur = g.db.execute('select word, translation from userwords where id=(?) and book=(?) order by review limit 1', (str(session['id']), session['book']))
        words = [dict(word=row[0], translation=row[1]) for row in cur.fetchall()]
        word = words[0]
    return render_template('word.html', word=word)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    if request.method == 'POST':
        if request.form['username'] and request.form['password']:
            g.db.execute('insert into users (username, password, email) values (?, ?, ?)',
                 [request.form['username'], request.form['password'], request.form['email']])
            g.db.commit()
            cur = g.db.execute('select word, translation from cet4')
            words = [dict(word=row[0], translation=row[1]) for row in cur.fetchall()]
            flash('signup success!')
            return redirect(url_for('home'))
    return render_template('signup.html', error=error)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        cur = g.db.execute('select id, book from users where username=(?) and password=(?)', 
           (request.form['username'], request.form['password']))
        result = cur.fetchall()
        if len(result) == 1:
            flash('success')
            session['logged_in'] = True
            session['id'] = result[0][0]
            session['name'] = request.form['username']
            session['book'] = result[0][1]
            prepare_word(session['id'], session['book'])
            return redirect(url_for('home'))
        else:
            flash("Login failed. Pls check.")
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('home'))

# @app.route('/user/<name>')
# def user(name):
#     return render_template('user.html', name=name)

if __name__ == '__main__':
    app.run(host='0.0.0.0')