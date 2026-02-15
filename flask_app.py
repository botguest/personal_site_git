import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secret key for session management
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_site.db'  # Use SQLite for simplicity
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define your password here
MANAGER_PASSWORD_HASH = generate_password_hash("61069856")

# alt between these two comments to run on server vs local.
#UPLOAD_FOLDER = '/home/botguest/personal_site/personal_site/static/uploads'
#os.makedirs(UPLOAD_FOLDER, exist_ok=True)
UPLOAD_FOLDER = '/Users/jingxingxu/Desktop/Productivity/job/personal_site_git/static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

first_visit = True


class ArchivePost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    link = db.Column(db.String(255), nullable=True)
    image_filename = db.Column(db.String(255), nullable=True)


@app.route('/')
def home():
    global first_visit
    if first_visit:
        session['logged_in'] = False
        first_visit = False
    return render_template('index.html')


@app.route('/archive')
def archive():
    posts = ArchivePost.query.order_by(ArchivePost.id.desc()).all()  # Retrieve posts in descending order
    return render_template('archive.html', posts=posts)


# this is just a placeholder.
@app.route('/follow')
def follow():
    return render_template('follow.html')


# this is just a placeholder.
@app.route('/follower login')
def follower_login():
    return render_template('follower_login.html')


# this is just a placeholder.
@app.route('/manager', methods=['GET', 'POST'])
def manager():
    if request.method == 'POST':
        password = request.form.get('password')
        if check_password_hash(MANAGER_PASSWORD_HASH, password):
            session['logged_in'] = True
            return redirect(url_for('manager'))
        else:
            return render_template('manager.html', error='Incorrect password')
    return render_template('manager.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/post_content', methods=['POST'])
def post_content():
    if not session.get('logged_in'):
        return redirect(url_for('manager_login'))

    content = request.form.get('content')
    link = request.form.get('link')
    image = request.files.get('image')
    image_filename = None

    if image:
        image_filename = secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))

    new_post = ArchivePost(content=content, link=link, image_filename=image_filename)
    db.session.add(new_post)
    db.session.commit()

    flash("Content posted successfully!")
    return redirect(url_for('archive'))


@app.route('/delete_post/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    if not session.get('logged_in'):
        return redirect(url_for('manager_login'))

    post = ArchivePost.query.get(post_id)
    if post:
        db.session.delete(post)
        db.session.commit()
        flash("Post deleted successfully!")
    else:
        flash("Post not found.")

    return redirect(url_for('archive'))


@app.route('/logout')
def logout():
    session.clear()  # Clears all session data
    return redirect(url_for('home'))

# alt for local & online environ
'''
if __name__ == '__main__':
    db.create_all()
    app.run()
'''
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
