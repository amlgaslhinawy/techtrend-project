import sqlite3
import logging 
import sys
from flask import Flask, json, render_template, request, url_for, redirect, flash
from flask.wrappers import Response
from werkzeug.exceptions import abort
from logging import StreamHandler
from datetime import datetime


count = 0

def get_db_connection():
    global count 
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    count += 1
    return connection

def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return 

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():

    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    app.logger.info('retrieved')
    return render_template('index.html', posts=posts)

@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
        app.logger.debug("Article with post id \"{}\" does not exist.".format(post_id))
        return render_template('404.html'), 404
    else:
        app.logger.info("Article \"{}\" retrieved".format(post["Title"]))
        return render_template('post.html', post=post)

@app.route('/healthz')
def status():
    response = app.response_class(
            response=json.dumps({"result":"OK - healthy"}),
            status=200,
            mimetype='application/json'
    )
    return response

@app.route('/metrics')
def metrics():
    connection = get_db_connection()
    total_posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    cnt = len(total_posts)
    return {"count": count, "cnt": cnt}    

@app.route('/about')
def about():
    app.logger.info('About us page retrieved')
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            app.logger.info("Article : '{}'".format(title))
            return redirect(url_for('index'))

    return render_template('create.html')

# start the application on port 3111
if __name__ == "__main__":

stdout_handler =  logging.StreamHandler(sys.stdout)
    stderr_handler =  logging.StreamHandler(sys.stderr)
    handlers = [stderr_handler, stdout_handler]
    logging.basicConfig(level=logging.DEBUG, handlers=handlers)
   app.run(host='0.0.0.0', port='3111')
