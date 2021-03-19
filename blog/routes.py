from flask import Flask, render_template, request, flash, redirect, url_for
from blog.forms import accountForm, loginForm, postForm, registrationForm, updateForm
from blog import bcrypt, db, app
from blog.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
import secrets, os
from PIL import Image

@app.route('/home')
@app.route('/')
def home():
    post = Post.query.order_by(Post.date.desc()).all()
    return render_template('home.html', posts=post)

@app.route('/about')
def about():
    return render_template('about.html', title='About Us')

@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = loginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user,''' remember = form.remember.data''')
            next_page= request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login unsuccessful!', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
    logout_user()
    flash('You have been successfully logged out','success')
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = registrationForm()
    if form.validate_on_submit():
        encrypted_pass = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=encrypted_pass)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created successfully!', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html', title='Signup', form=form)

def save_picture(form_picture):
    random_picture = secrets.token_hex(8)
    filename, file_ext = os.path.splitext(form_picture.filename)
    picture_name = random_picture + file_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pic', picture_name)
    outputsize = (200, 200)
    image = Image.open(form_picture)
    image.thumbnail(outputsize)
    image.save(picture_path)
    return picture_name

@app.route('/account', methods=['GET','POST'])
@login_required
def account():
    form = accountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data =  current_user.email
    image_file = url_for('static', filename='profile_pic/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)

# trial post route(renamed as newpost)
@app.route('/newpost', methods=['GET','POST'])
@login_required
def newpost():
    form = postForm()
    if form.validate_on_submit():
        post = Post(title= form.title.data, content = form.content.data, author = current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created successfully!', 'success')
        return redirect(url_for('home'))
    return render_template('newpost.html', title='Post', form=form)

# trial view route
@app.route('/view/<int:post_id>', methods=['GET','POST'])
@login_required
def viewpost(post_id):
    post = Post.query.filter_by(id=post_id).one()
    return render_template('view.html', title='View' , post=post)

# timeline route
@app.route('/timeline', methods=['GET','POST'])
@login_required
def timeline():
    posts = Post.query.filter_by(author = current_user).order_by(Post.date.desc()).all()
    return render_template('timeline.html', title='Timeline' , posts=posts)

# trial update-post route
@app.route('/updatepost/<int:id>', methods=['GET','POST'])
@login_required
def updatepost(id):
    form = updateForm()
    post = Post.query.filter_by(id=id).one()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash("Post updated successfully", "success") 
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data =  post.content
    return render_template('updatepost.html',post = post, form=form)

# trial delete-post route
@app.route('/deletepost/<string:title>', methods=['GET','POST'])
@login_required
def deletepost(title):
    post = Post.query.filter_by(title=title).one()
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted successfully!', 'success')
    return redirect(url_for('home'))

