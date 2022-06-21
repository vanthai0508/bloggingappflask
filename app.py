from os import name
import sqlite3
from flask import Flask, render_template, redirect, request,session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import re
app = Flask(__name__)
app.secret_key = "super secret key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False, unique=True)
    content = db.Column(db.Text, nullable=False)
    posted_by = db.Column(db.String(100), nullable=False, default='N/A')
    posted_on = db.Column(db.DateTime, nullable=False,
                            default=datetime.utcnow())
    num_like = db.Column(db.Integer, default=0)
    def __repr__(self):
        return self.title
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    def __repr__(self):
        return '<User %r>' % self.username
db.create_all()
db.session.commit()
@app.route('/')
@app.route('/login',methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST':
         user_name = request.form['Username']
         session['curruser'] = request.form['Username']
         user_pwd = request.form['psw']
         conn = sqlite3.connect('database.db')
         cursorObj = conn.cursor()
         cursorObj.execute('SELECT * FROM user WHERE username = ? AND password = ?', (user_name, user_pwd))
         account = cursorObj.fetchone()
         if account:
             all_posts = Post.query.order_by(Post.posted_on).all()
             return render_template('posts.html', posts=all_posts,msg=user_name)
         else:
             msg = 'Incorrect username or password !'
             return render_template('login.html',msg=msg)   
    else:
      msg = 'Incorrect username or password !'
      return render_template('login.html',msg="")
@app.route('/signup',  methods=['GET', 'POST'])
def signup():
     msg = ''
     if request.method == 'POST':
        user_name = request.form['Username']
        user_email = request.form['email']
        user_pwd = request.form['psw']
        new_user = User(username=user_name,email=user_email,password=user_pwd)
        conn = sqlite3.connect('database.db')
        cursorObj = conn.cursor()
        cursorObj.execute('SELECT * FROM user WHERE username = ?', (user_name, ))
        name = cursorObj.fetchone()
        cursorObj.execute('SELECT * FROM user WHERE email = ?', (user_email, ))
        mail = cursorObj.fetchone()
        if name:
            msg = 'Username already exists !'
            return render_template('signup.html',msg=msg)
        elif mail:
            msg = 'Email already register !'
            return render_template('signup.html',msg=msg)
        elif not re.match(r'[^@]+@[^@]+\.[^@]+',user_email):
            msg = 'Invalid email address !'
            return render_template('signup.html',msg=msg)
        elif not re.match(r'[A-Za-z0-9]+', user_name):
            msg = 'Username must contain only characters and numbers !'
            return render_template('signup.html',msg=msg)
        elif not user_name or not user_pwd or not user_email:
            msg = 'Please fill out the form !'
            return render_template('signup.html',msg=msg)
        else:
            db.session.add(new_user)
            db.session.commit()
            return redirect('/login')
     else:
        msg='Please fill out the form !'
        return render_template('signup.html',msg=msg)
@app.route('/posts',  methods=['GET', 'POST'])
def posts():
    if request.method == 'POST':
        post_title = request.form['title']
        post_content = request.form['post']
        post_author = session['curruser']
        new_post = Post(title=post_title,
                        content=post_content, posted_by=post_author)
        db.session.add(new_post)
        db.session.commit()

        all_posts = Post.query.order_by(Post.posted_on).all()
        name = session['curruser']
        return render_template('posts.html', posts=all_posts,msg=name)
    else:
        all_posts = Post.query.order_by(Post.posted_on).all()
        name = session['curruser']
        return render_template('posts.html', posts=all_posts,msg=name)

@app.route('/posts/new', methods=['GET', 'POST'])
def new_post():
    if request.method == 'POST':
        post_title = request.form['title']
        post_content = request.form['post']
        post_author = session['curruser']
        new_post = Post(title=post_title,
                        content=post_content, posted_by=post_author)
        db.session.add(new_post)
        db.session.commit()
        all_posts = Post.query.order_by(Post.posted_on).all()
        name = session['curruser']
        return render_template('posts.html', posts=all_posts,msg=name)
    else:
        all_posts = Post.query.order_by(Post.posted_on).all()
        name = session['curruser']
        return render_template('new_post.html',posts=all_posts,msg=name)
@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    to_edit = Post.query.get_or_404(id)
    if request.method == 'POST':
        to_edit.title = request.form['title']
        to_edit.content = request.form['post']
        db.session.commit()
        all_posts = Post.query.order_by(Post.posted_on).all()
        name = session['curruser']
        return render_template('posts.html', posts=all_posts,msg=name)
    else:
        return render_template('edit.html', post=to_edit)
@app.route('/posts/delete/<int:id>')
def delete(id):
    to_delete = Post.query.get_or_404(id)
    db.session.delete(to_delete)
    db.session.commit()
    all_posts = Post.query.order_by(Post.posted_on).all()
    name = session['curruser']
    return render_template('posts.html', posts=all_posts,msg=name)
@app.route('/logout')
def logout():
    session.pop('curruser',None)
    return redirect('/login')
# @app.route('/posts/like/<int:id>', methods=['GET', 'POST'])
# def like(id):
#     to_like = CodeSpeedyBlog.query.get_or_404(id)
#     if request.method == 'POST':
#        to_like.num_like = to_like.num_like+1
#        db.session.commit()
#        all_posts = CodeSpeedyBlog.query.order_by(CodeSpeedyBlog.posted_on).all()
#        name = session['curruser']
#        return render_template('posts.html', posts=all_posts,msg=name)
#     else:
#         all_posts = CodeSpeedyBlog.query.order_by(CodeSpeedyBlog.posted_on).all()
#         name = session['curruser']
#         return render_template('posts.html', posts=all_posts,msg=name,numlike=to_like.num_like+1)
if __name__ == "__main__":
    app.run(debug=True)