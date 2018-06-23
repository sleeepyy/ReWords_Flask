import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from util import words
import random

app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig')

def init_db():
    with app.app_context():
        rv = sqlite3.connect(app.config['DATABASE'])
        rv.row_factory = sqlite3.Row
        db = rv
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()
        cet4_words = list(words.process_words('CET4.words').items())
        cet6_words = list(words.process_words('CET6.words').items())
        random.shuffle(cet4_words)
        random.shuffle(cet6_words)

        for word, translation in cet4_words:
            db.execute('insert into cet4 (word, translation) values (?, ?)', (word, translation))
        db.commit()
        for word, translation in cet6_words:
            db.execute('insert into cet6 (word, translation) values (?, ?)', (word, translation))
        db.commit()

if __name__ == '__main__':
    init_db()
    print('Initialized.')