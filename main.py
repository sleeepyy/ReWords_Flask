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
        

def prepare_word(user_id, book):
    cur = g.db.execute('select distinct book from userwords where id=(?)', str(user_id))
    books = [row[0] for row in cur.fetchall()]
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

@app.route('/review')
def review():
    cur = g.db.execute('select word, translation from userwords where id=(?) and book=(?) order by review', (str(session['id']), session['book']))
    words = [dict(word=row[0], translation=row[1]) for row in cur.fetchall()]
    return render_template('words.html', words=words)

@app.route('/word', methods=['GET', 'POST'])
def word():
    cur = g.db.execute('select word, translation from userwords where id=(?) and book=(?) order by review limit 1', (str(session['id']), session['book']))
    words = [dict(word=row[0], translation=row[1]) for row in cur.fetchall()]
    if len(words) == 1:
        word = words[0]
    else:
        flash("No words yet. Please add words for this book first.")
        return redirect(url_for('home'))
    word = words[0]
    if request.method == 'POST':
        if request.form['submit'] == '记得':
            g.db.execute('update userwords set review = review+10 where id=(?) and book=(?) and word=(?)', (str(session['id']), session['book'], word['word']))
        if request.form['submit'] == '忘记':
            g.db.execute('update userwords set review= review+5 where id=(?) and book=(?) and word=(?)', (str(session['id']), session['book'], word['word']))
        g.db.commit()
        cur = g.db.execute('select word, translation from userwords where id=(?) and book=(?) order by review limit 1', (str(session['id']), session['book']))
        words = [dict(word=row[0], translation=row[1]) for row in cur.fetchall()]

    return render_template('word.html', word=word)

@app.route('/books', methods=['GET', 'POST'])
def books():
    if request.method == 'POST':
        session['book'] = request.form['book']
        g.db.execute('update users set book ="'+session['book']+'" where id=(?)', (str(session['id'])))
        g.db.commit()
        prepare_word(session['id'], session['book'])
        return redirect(url_for('home'))
    return render_template('books.html')
    
@app.route('/manage', methods=['GET', 'POST'])
def manage():
    if request.method == 'POST':
        word = request.form['word']
        translation = request.form['translation']
        g.db.execute('insert into words (user_id, word, translation) values(?,?,?)',(session['id'], word, translation))
        g.db.commit()
        g.db.execute('insert into userwords (id, book, word, translation, review) values (?, ?, ?, ?, ?)', 
               (int(session['id']), 'words', word, translation, random.randint(0, 100)))
        g.db.commit()
        flash('Add words successfully')
    return render_template('manage.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    if request.method == 'POST':
        try:
            g.db.execute('insert into users (username, password, email) values (?, ?, ?)',
                 [request.form['username'], request.form['password'], request.form['email']])
            g.db.commit()
            cur = g.db.execute('select word, translation from cet4')
            words = [dict(word=row[0], translation=row[1]) for row in cur.fetchall()]
            flash('Signup success!')
            return redirect(url_for('home'))
        except Exception as e:
            print(e)
            flash('Signup failed')
    return render_template('signup.html', error=error)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        try:
            cur = g.db.execute('select id, book from users where email=(?) and password=(?)', 
            (request.form['email'], request.form['password']))
            result = cur.fetchall()
        except Exception as e:
            print(e)
            flash("Login failed. Please check.")
        if len(result) == 1:
            flash('success')
            session['logged_in'] = True
            session['id'] = result[0][0]
            session['book'] = result[0][1]
            print(session)
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


if __name__ == '__main__':
    app.run(host='0.0.0.0')