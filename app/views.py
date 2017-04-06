from flask import render_template, redirect, flash, request, jsonify, url_for, send_from_directory
from flask_mail import Message
from flask_login import login_user, login_required, logout_user
from werkzeug.utils import secure_filename
from slugify import slugify

from app import app, mail, db, login_manager
from app.models import Category, Painting, Video, AdminUser, About
from app.forms import ContactForm, LoginForm
from config import MAIL_USERNAME, ALLOWED_EXTENSIONS

import os
import sys

def render_with_categories(template, **kwargs):
    return render_template(template, categories=Category.query.all(), current_url=request.path, **kwargs)

@app.route('/')
def index():
    return render_with_categories('index.html')

@app.route('/paintings/')
@app.route('/paintings/<category_slug>')
def paintings(category_slug=None):
    category = None
    if category_slug:
        category = Category.query.filter_by(slug=category_slug).first()
        if category is None:
            return page_not_found(404)
        paintings = Painting.query.filter_by(category=category).order_by(Painting.category_order)
    else:
        paintings = Painting.query.all()
    return render_with_categories('paintings.html', paintings=paintings, category=category)

@app.route('/media/<file_type>/<filename>')
def get_media(file_type, filename):
    return send_from_directory(os.path.join(app.config['MEDIA_ROOT'], file_type), filename)

@app.route('/videos')
def videos():
    videos = Video.query.all()
    return render_with_categories('videos.html', videos=videos)

@app.route('/about/')
def about():
    return render_with_categories('about.html', about_model=About.query.get(1))

@app.route('/about/resume')
def resume():
    return render_with_categories('resume.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        msg = Message(form.subject.data,
            sender = form.email.data,
            recipients = [MAIL_USERNAME],
        )
        msg.body = form.message.data+"\n\nFrom: "+form.name.data
        msg.html = render_template('contact_email.html',
            name=form.name.data,
            email=form.email.data,
            subject=form.subject.data,
            message=form.message.data,
        )
        mail.send(msg)
        flash('Email successfully delivered')
        return redirect(url_for('contact'))
    return render_with_categories('contact.html', form=form)

@app.errorhandler(404)
@app.errorhandler(405)
def page_not_found(e):
    return render_with_categories('404.html'), 404

#
# Admin Stuff
#

@login_manager.user_loader
def user_loader(user_id):
    return AdminUser.query.get(user_id)

@app.route('/admin')
def admin():
    return redirect(url_for('login'))

@app.route('/admin/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = AdminUser.query.get(form.username.data)
        if user and user.check_password(form.password.data):
            login_user(user)

            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
    return render_template('login.html', form=form)

@app.route('/admin/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

def commitAndJsonify(**kwargs):
    try:
        db.session.commit()
        return jsonify(success=True, **kwargs)
    except:
        return jsonify(success=False, exception='Database Error', **kwargs)

# Sorting

def reorder_after_sort(oldIndex, newIndex, query_func, attr):
    if newIndex > oldIndex:
        for i in range(oldIndex, newIndex+1):
            setattr(query_func(i), attr, -i)

        setattr(query_func(-oldIndex), attr, newIndex)
        for i in range(oldIndex+1, newIndex+1):
            setattr(query_func(-i), attr, i-1)
    else:
        for i in range(newIndex, oldIndex+1):
            setattr(query_func(i), attr, -i)

        setattr(query_func(-oldIndex), attr, newIndex)
        for i in range(newIndex, oldIndex):
            setattr(query_func(-i), attr, i+1)

@app.route('/update/paintings/order', methods=['POST'])
@app.route('/update/paintings/<category_slug>/order', methods=['POST'])
def update_painting_order(category_slug=None):
    # Sortable returns 0 indexing. SQLAlchemy primary key uses 1 indexing
    oldIndex = int(request.form['oldIndex'])+1
    newIndex = int(request.form['newIndex'])+1

    if category_slug:
        category = Category.query.filter_by(slug=category_slug).first()

        def query_by_category_and_order(index):
            return Painting.query.filter_by(category=category).filter_by(category_order=index).first()

        reorder_after_sort(oldIndex, newIndex, query_by_category_and_order, 'category_order')
    else:
        reorder_after_sort(oldIndex, newIndex, Painting.query.get, 'id')
    return commitAndJsonify()

@app.route('/update/categories/order', methods=['POST'])
def update_category_order():
    oldIndex = int(request.form['oldIndex'])+1
    newIndex = int(request.form['newIndex'])+1

    reorder_after_sort(oldIndex, newIndex, Category.query.get, 'id')
    return commitAndJsonify()

@app.route('/update/videos/order', methods=['POST'])
def update_video_order():
    oldIndex = int(request.form['oldIndex'])+1
    newIndex = int(request.form['newIndex'])+1

    reorder_after_sort(oldIndex, newIndex, Video.query.get, 'id')
    return commitAndJsonify()

# Uploading to database

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/update/paintings/new', methods=['POST'])
def upload_painting():
    # Collect info and initalize Painting
    image = request.files['file']
    if not allowed_file(image.filename):
        flash(".jpg files only")
        return redirect(request.form['currentURL'])
    category = Category.query.filter_by(name=request.form['category']).first()

    new_painting = Painting(
        name = request.form['name'],
        category = category,
        medium = request.form['medium'],
        dimensions = request.form['dimensions'],
        year = request.form['year'],
        filename = secure_filename(image.filename),
    )
    # Upload File (Use new_painting filename since it would've updated for uniquness)
    image.save(os.path.join(app.config['MEDIA_ROOT'], 'image', new_painting.filename))
    # Make thumbnail
    Painting.makeThumbnail(
        os.path.join(app.config['MEDIA_ROOT'], 'image', new_painting.filename),
        os.path.join(app.config['MEDIA_ROOT'], 'thumbnail', new_painting.thumbname),
        category.thumbsize_large if category else False,
    )
    # Update database
    db.session.add(new_painting)
    db.session.commit()
    flash("success")
    return redirect(request.form['currentURL'])

@app.route('/update/categories/new', methods=['POST'])
def add_category():
    if Category.query.filter_by(name=request.form['name']).count():
        flash('Category already exists')
        return redirect(request.form['currentURL'])

    new_category = Category(
        name = request.form['name'],
        header = request.form['header'],
        description = request.form['description'],
        thumbsize_large = True if request.form.get('thumbsize') else False
    )
    slug = new_category.slug

    db.session.add(new_category)
    db.session.commit()
    flash('success')
    return redirect(url_for('paintings', category_slug=slug))

@app.route('/update/videos/new', methods=['POST'])
def add_video():
    new_video = Video(
        name = request.form['name'],
        embed_url = request.form['embedurl']
    )
    db.session.add(new_video)
    db.session.commit()
    flash('success')
    return redirect(url_for('videos'))

# Editing database info

@app.route('/update/paintings/details', methods=['POST'])
def edit_painting():
    p = Painting.query.filter_by(filename=request.form['filename']).first()
    p.name = request.form['name']
    p.medium = request.form['medium']
    p.dimensions = request.form['dimensions']
    p.year = request.form['year']

    return commitAndJsonify();

@app.route('/update/categories/details', methods=['POST'])
def edit_category():
    c = Category.query.filter_by(name=request.form['id']).first()
    c_p = Painting.query.filter_by(category_name=c.name)
    c.name = request.form['name']
    c.header = request.form['header']
    c.description = request.form['description']
    c.slug = slugify(request.form['name'])
    # Update foreign key relation
    for p in c_p:
        p.category_name = c.name
    # Check if thumbsize changed
    if c.thumbsize_large != (True if request.form.get('thumbsize') else False):
        c.thumbsize_large = not c.thumbsize_large
        # Update thumbnails
        c_p = Painting.query.filter_by(category_name=c.name)
        for p in c_p:
            Painting.makeThumbnail(
                os.path.join(app.config['MEDIA_ROOT'], 'image', p.filename),
                os.path.join(app.config['MEDIA_ROOT'], 'thumbnail', p.thumbname),
                c.thumbsize_large
            )
    db.session.commit()
    flash('success')
    return redirect(url_for('paintings', category_slug=c.slug))

@app.route('/update/videos/details', methods=['POST'])
def edit_video():
    video = Video.query.filter_by(embed_url=request.form['oldurl']).first()
    video.name = request.form['name']
    video.embed_url = request.form['embedurl']
    try:
        db.session.commit()
        flash('success')
    except:
        flash('Database error')
    return redirect(url_for('videos'))

@app.route('/update/about/details', methods=['POST'])
def edit_about():
    model = About.query.get(1)
    setattr(model, request.form['component'], request.form['content'])
    return commitAndJsonify();

# Deleting from database

def collapse_ordering(deleted_index, model, attr):
    length = model.query.count()
    for i in range(deleted_index+1, length+2):  # Add 1 for exclusive, Add 1 for current max id
        setattr(model.query.get(i), attr, i-1)

@app.route('/update/paintings/delete', methods=['POST'])
def delete_painting():
    filename = request.form['filename']

    p = Painting.query.filter_by(filename=filename).first()
    thumbname = p.thumbname
    deleted_id = p.id

    db.session.delete(p)
    collapse_ordering(deleted_id, Painting, 'id')
    try:
        os.remove(os.path.join(app.config['MEDIA_ROOT'], 'image', filename))
    except FileNotFoundError as e:
        pass
    try:
        os.remove(os.path.join(app.config['MEDIA_ROOT'], 'thumbnail', thumbname))
    except FileNotFoundError as e:
        pass

    return commitAndJsonify();

@app.route('/update/categories/delete', methods=['POST'])
def delete_category():
    category = Category.query.filter_by(name=request.form['name']).first()
    category_id = category.id
    category_slug = category.slug

    db.session.delete(category)
    collapse_ordering(category_id, Category, 'id')

    if request.form['currentURL'] == url_for('paintings', category_slug=category_slug):
        flash('success')
        return commitAndJsonify(redirect=url_for('paintings'))
    return commitAndJsonify();

@app.route('/update/videos/delete', methods=['POST'])
def delete_video():
    video = Video.query.filter_by(embed_url=request.form['url']).first()
    video_id = video.id
    db.session.delete(video)
    collapse_ordering(video_id, Video, 'id')
    return commitAndJsonify();
