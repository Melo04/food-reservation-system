from functools import wraps
from flask import render_template, url_for, flash, redirect, request, current_app
from website import app, db, bcrypt, mail
from website.forms import RegistrationForm, LoginForm, UpdateProfileForm, RequestResetForm, ResetPasswordForm, AdminUpdateProfileForm
from website.models import User
from flask_login import login_user, current_user, logout_user
from flask_mail import Message
import secrets
import os
from PIL import Image
from website.menu.models import Addmenu

with app.app_context():
    db.create_all()

def login_required(role="ANY"):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
               return current_app.login_manager.unauthorized()
            if ((current_user.role != role) and (role != "ANY")):
               return current_app.login_manager.unauthorized()      
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper

def check_role(role="ANY"):
    if current_user.is_authenticated:
        if current_user.role == 'parent':
            return redirect(url_for('parent_dashboard'))
        elif current_user.role == 'student':
            return redirect(url_for('student_dashboard'))
        elif current_user.role == 'worker':
            return redirect(url_for('worker_dashboard'))
        elif current_user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
    return render_template('home.html')

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/dashboard/parent", methods=['GET', 'POST'])
@login_required(role="parent")
def parent_dashboard():
    return render_template('parent/dashboard.html')

@app.route("/dashboard/student", methods=['GET', 'POST'])
@login_required(role="student")
def student_dashboard():
    return render_template('student/dashboard.html')

@app.route("/dashboard/worker", methods=['GET', 'POST'])
@login_required(role="worker")
def worker_dashboard():
    menus = Addmenu.query.all()
    return render_template('worker/dashboard.html',menus=menus)

@app.route("/dashboard/admin", methods=['GET', 'POST'])
@login_required(role="admin")
def admin_dashboard():
    users = User.query.all()
    page = request.args.get('page', 1, type=int)
    per_page = 5
    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    paginated_users = users[start_index:end_index]

    form = AdminUpdateProfileForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        user.username = form.username.data
        user.status = form.status.data
        db.session.commit()
        flash('User profile has been updated!', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin/dashboard.html', form=form, users=paginated_users, page=page, per_page=per_page, total_users=len(users), title='Admin Dashboard')

@app.route("/register", methods=['GET', 'POST'])
def register():
    check_role()
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, firstname=form.firstname.data, lastname=form.lastname.data, phone=form.phone.data, role=form.role.data, status=form.status.data, password=hashed_password, parent_id=form.parent_id.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    check_role()
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            if user.role == 'parent':
                return redirect(next_page) if next_page else redirect(url_for('parent_dashboard'))
            elif user.role == 'student':
                return redirect(next_page) if next_page else redirect(url_for('student_dashboard'))
            elif user.role == 'worker':
                return redirect(next_page) if next_page else redirect(url_for('worker_dashboard'))
            elif user.role == 'admin':
                return redirect(next_page) if next_page else redirect(url_for('admin_dashboard'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    output_size = (125,125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn

@app.route("/profile", methods=['GET', 'POST'])
def profile():
    form = UpdateProfileForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.firstname = form.firstname.data
        current_user.lastname = form.lastname.data
        current_user.phone = form.phone.data
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.firstname.data = current_user.firstname
        form.lastname.data = current_user.lastname
        form.phone.data = current_user.phone
        image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
        if current_user.role == 'parent':
            students = User.query.filter(User.parent_id.contains(str(current_user.id))).all()
            return render_template('profile.html', title='Profile', image_file=image_file, form=form, students=students)
        elif current_user.role == 'student':
            if isinstance(current_user.parent_id, int):
                parent_ids = [current_user.parent_id]
            else:
                parent_ids = [int(id.strip()) for id in current_user.parent_id.split(',')]
            parents = User.query.filter(User.id.in_(parent_ids)).all()
            return render_template('profile.html', title='Profile', image_file=image_file, form=form, parents=parents)
        elif current_user.role == 'worker' or current_user.role == 'admin':
            return render_template('profile.html', title='Profile', image_file=image_file, form=form)

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='noreply@demo.com', recipients=[user.email])
    msg.body=f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no change will be made.
    '''
    mail.send(msg)

@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    check_role()
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)

@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    check_role()
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid token or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        print(user.password)
        db.session.add(user)
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)