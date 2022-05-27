from flask import Flask, render_template, flash, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import ForeignKey, true
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_ckeditor import CKEditor
from werkzeug.utils import secure_filename
import uuid as uuid
import os

from blogforms import UsersForm, NameForm, Test_pwForm, LoginForm, PostsForm, SearchForm

# import mysql.connector

app = Flask(__name__)

# initialize ckeditor
ckeditor = CKEditor(app)
# Sqlite connector
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://rmpmdruibwzfiv:425905490193cf2e078990b77d3309cc10ef309f6e2690b106601433d36081b5@ec2-52-4-104-184.compute-1.amazonaws.com:5432/d11684rj8gnc45'

# Mysql connector
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/users'

# secrete key
app.config['SECRET_KEY'] = "This is my secret key"

UPLOAD_FOLDER = 'static/img/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# initailize db
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# flask login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))    


# Users database model
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False, unique=True)
    favorite_color = db.Column(db.String(120))
    about_author = db.Column(db.Text(), nullable=True)
    profile_pic = db.Column(db.String(), nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Posts', backref='author')

    @property
    def password(self):
        raise AttributeError("This password does not have a readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password) 

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        return '<name %r>' % self.name


# Blog post model
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    #author = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    content =  db.Column(db.Text, nullable=False)
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable = False)




@app.route("/")
def index():
    languages = ["Python", "html", "CSS", "JavaScript", "Java", "RubyonRails"]
    return render_template("index.html", languages=languages)


@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    form =  UsersForm()
    user_update = Users.query.get_or_404(id)
    if request.method == "POST":
        user_update.name = request.form['name']
        user_update.email = request.form['email']
        user_update.favorite_color = request.form['favorite_color']
        user_update.about_author = request.form['about_author']
        user_update.profile_pic = request.files['profile_pic'] # it worked for me without error
        # Grab image name
        pic_filename = secure_filename(user_update.profile_pic.filename)
        # Set UUID
        pic_name = str(uuid.uuid1()) + "_" + pic_filename

        #save image to static folder
        #user_update.profile_pic.save(os.path.join(app.config['UPLOAD_FOLDER']), pic_name)
        #save image name to db
        user_update.profile_pic = pic_name

        try:
            db.session.commit()
            name = form.name.data
            form.name.data = ""
            form.email.data = ""
            form.favorite_color.data = ""
            form.about_author.data = ""
            flash("User updated successfully!")
            user_list = Users.query.order_by(Users.date_created)
            return render_template('dashboard.html', form=form, user_list=user_list)
        except:
            flash("Error! Something went wrong....try again!")
            return render_template('add_user.html', form=form, user_list=user_list)
    else:
        return render_template('update.html', form=form, user_update=user_update)


@app.route("/posts/editpost/<int:id>", methods = ['GET', 'POST'])
@login_required
def edit_post(id):
    form = PostsForm()
    get_post = Posts.query.get_or_404(id)
    if request.method == 'POST':
        get_post.title = request.form['title']
        get_post.slug = request.form['slug']
        get_post.content = request.form['content']
        db.session.add(get_post)
        db.session.commit()
        flash("Posts updated successfully!")
        return redirect(url_for('read_more', id=get_post.id))
    if get_post.poster_id == current_user.id:
        form.title.data = get_post.title 
        form.slug.data = get_post.slug
        form.content.data = get_post.content
    else:
         flash("You're not authorized to edit the post!")
    return render_template('editpost.html', form=form, get_post=get_post)
    

@app.route('/delete/<int:id>')
@login_required
def delete(id):
    user_to_delete = Users.query.get_or_404(id)
    name = None
    form=UsersForm()
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User deleted successfully!")
        user_list = Users.query.order_by(Users.date_created)
        return render_template('add_user.html', form=form, name=name, user_list=user_list, id=id)
    except:
        flash("Error! Something went wrong...could not delete user!")
        return render_template('add_user.html', form=form, name=name, user_list=user_list, id=id)

@app.route('/posts/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_post(id):
    post_to_del = Posts.query.get_or_404(id)
    if post_to_del.poster_id == current_user.id:
        try:
            db.session.delete(post_to_del)
            db.session.commit()
            flash("Post deleted successfully!")
            return redirect(url_for('view_post'))
        except:
            flash("Error! Something went wrong!")
            return redirect(url_for('view_post'))
    else:
        flash("Access denied!")
    return redirect(url_for('view_post'))

@app.route("/user/<name>")
def user(name):
    return render_template("user.html", name=name)

# Create Custom Error Pages

# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

# Internal Server Error
@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500

@app.route("/name", methods = ['GET', 'POST'])
def your_name():
    name = None
    form = NameForm()
    # form validation
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ""
        flash("Form submitted successfully")

    return render_template("name.html", name=name, form=form)


@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    name = None
    form = UsersForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            hash_pw = generate_password_hash(form.pw_hash.data, "sha256")
            user = Users(username=form.username.data,name=form.name.data, email=form.email.data, 
            favorite_color=form.favorite_color.data, about_author=form.about_author.data,
            password_hash=hash_pw)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ""
        form.username.data = ""
        form.email.data = ""
        form.favorite_color.data = ""
        form.about_author.data = ""
        form.pw_hash.data = ""
        flash('User added successfully!')
    user_list = Users.query.order_by(Users.date_created)  
    return render_template('add_user.html', form=form, name=name, user_list=user_list)


@app.route("/add_posts", methods = ['GET', 'POST'])
@login_required
def add_posts():
    form = PostsForm()
    posts = None
    if form.validate_on_submit():
        poster_id = current_user.id
        posts = Posts(title=form.title.data, poster_id = poster_id, slug=form.slug.data, content=form.content.data)
        db.session.add(posts)
        db.session.commit()
        form.title.data = ''
        form.slug.data = ''
        form.content.data = ''
        flash("Post submitted successfully!")
    
    return render_template('add_post.html', form=form, posts=posts)


@app.route("/viewpost", methods = ['GET', 'POST'])
@login_required
def view_post():
    blog_posts = Posts.query.order_by(Posts.date_created)
    return render_template('viewpost.html', blog_posts=blog_posts)

@app.route("/readmore/<int:id>", methods = ['GET', 'POST'])
def read_more(id):
    post = Posts.query.get_or_404(id)
    return render_template("readmore.html", post=post)


@app.route("/login", methods = ['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            # check the hash password
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash("Login successfull")
                return redirect(url_for('dashboard'))
            else:
                flash("Wrong username or password! try again")
        else:
            flash("This user does not exist")
    return render_template("login.html", form=form)


@app.route("/dashboard", methods = ['GET', 'POST'])
@login_required
def dashboard():
    return render_template("dashboard.html")

@app.route("/logout", methods = ['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("You're now logged out! Thanks for stopping by")
    return redirect(url_for('login'))

@app.route("/test_pw", methods = ['GET', 'POST'])
def your_email():
    email = None
    password = None
    pw_hash = None
    check_pw = None
    form = Test_pwForm()
    # form validation
    if form.validate_on_submit():
        email = form.email.data
        password = form.pw.data
        form.email.data = ""
        form.pw.data = ""
        pw_hash = Users.query.filter_by(email=email).first()
        
        check_pw = check_password_hash(pw_hash.password_hash, password)

    return render_template("test_pw.html", email=email, password=password, pw_hash=pw_hash, check_pw=check_pw, form=form)

# Pass form to navbar
@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)

@app.route('/search', methods=['POST'])
def search():
    form = SearchForm()
    if form.validate_on_submit():
        post_searched = form.searched.data
        posts = Posts.query.filter(Posts.content.like('%' + post_searched + '%'))
        posts = posts.order_by(Posts.title).all()
        return render_template('search.html', form=form, searched=post_searched, posts=posts)
    return render_template('search.html', form=form)



@app.route("/admin")
@login_required
def admin():
    id = current_user.id
    if id == 17:
        return render_template("admin.html")
    else:
        flash("Access denied: You need to be an admin to access this page!!!")
        return redirect(url_for('dashboard'))