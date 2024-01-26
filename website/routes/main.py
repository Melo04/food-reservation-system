from flask import Blueprint, render_template, url_for, flash, redirect, current_app, request
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
from website import app, db, bcrypt, mail
from functools import wraps
from website.models import *
from website.forms import *
from PIL import Image
import secrets
import os

main = Blueprint('main', __name__)

def login_required(role="ANY"):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
               return current_app.login_manager.unauthorized()
            if ((current_user.ROLE != role) and (role != "ANY")):
               return current_app.login_manager.unauthorized()      
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper

def check_role(role="ANY"):
    if current_user.is_authenticated:
        if current_user.ROLE == 'parent':
            return redirect(url_for('parent.parent_dashboard'))
        elif current_user.ROLE == 'student':
            return redirect(url_for('student.student_dashboard'))
        elif current_user.ROLE == 'worker':
            return redirect(url_for('worker.worker_dashboard'))
        elif current_user.ROLE == 'admin':
            return redirect(url_for('admin.admin_dashboard'))
    return render_template('home.html')

@main.errorhandler(404)
def page_not_found(e):
    return render_template('error.html')

@main.route("/")
@main.route("/home")
def home():
    return render_template('home.html')

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

@main.route("/login", methods=['GET', 'POST'])
def login():
    check_role()
    if current_user.is_authenticated:
        flash('User is already logged in', 'danger')
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = USER.query.filter_by(USERNAME=form.username.data).first()
        if user and bcrypt.check_password_hash(user.PASSWORD, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            if user.ROLE == 'parent':
                return redirect(next_page) if next_page else redirect(url_for('parent.parent_dashboard'))
            elif user.ROLE == 'student':
                return redirect(next_page) if next_page else redirect(url_for('student.student_dashboard'))
            elif user.ROLE == 'worker':
                return redirect(next_page) if next_page else redirect(url_for('worker.worker_dashboard'))
            elif user.ROLE == 'admin':
                return redirect(next_page) if next_page else redirect(url_for('admin.admin_dashboard'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@main.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@main.route("/profile", methods=['GET', 'POST'])
@login_required(role="ANY")
def profile():
    users = USER.query.all()
    form = UpdateProfileForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.IMAGE = picture_file
        current_user.USERNAME = form.username.data
        current_user.EMAIL = form.email.data
        current_user.FIRST_NAME = form.firstname.data
        current_user.LAST_NAME = form.lastname.data
        current_user.PHONE = form.phone.data
        if current_user.ROLE == 'parent':
            current_user.EWALLET_BALANCE = form.ewallet_balance.data
        for user in users:
            if user.USERNAME == form.username.data and user.id != current_user.id:
                flash('That username is taken. Please enter a different username.', 'danger')
                return redirect(url_for('main.profile'))
            elif user.EMAIL == form.email.data and user.id != current_user.id:
                flash('That email is taken. Please enter a different email.', 'danger')
                return redirect(url_for('main.profile'))
            elif user.PHONE == form.phone.data and user.id != current_user.id:
                flash('That phone is taken. Please enter a different phone number.', 'danger')
                return redirect(url_for('main.profile'))
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('main.profile'))
    elif request.method == 'GET':
        form.username.data = current_user.USERNAME
        form.email.data = current_user.EMAIL
        form.firstname.data = current_user.FIRST_NAME
        form.lastname.data = current_user.LAST_NAME
        form.phone.data = current_user.PHONE
        image_file = url_for('static', filename='profile_pics/' + current_user.IMAGE)
        if current_user.ROLE == 'parent':
            current_parent = PARENT.query.filter_by(id=current_user.id).first()
            form.ewallet_balance.data = current_parent.EWALLET_BALANCE
            students = STUDENT.query.filter_by(PARENT1_ID=current_user.id).all() + STUDENT.query.filter_by(PARENT2_ID=current_user.id).all()
            return render_template('profile.html', title='Profile', image_file=image_file, form=form, students=students)
        elif current_user.ROLE == 'student':
            current_student = STUDENT.query.filter_by(id=current_user.id).first()
            form.status.data = current_student.STATUS
            parents = USER.query.filter(USER.id.in_([current_student.PARENT1_ID, current_student.PARENT2_ID])).all()
            return render_template('profile.html', title='Profile', image_file=image_file, form=form, parents=parents)
        elif current_user.ROLE == 'worker' or current_user.ROLE == 'admin':
            return render_template('profile.html', title='Profile', image_file=image_file, form=form)

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='noreply@demo.com', recipients=[user.EMAIL])
    msg.body=f'''To reset your password, visit the following link:
{url_for('main.reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no change will be made.
    '''
    mail.send(msg)

@main.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    check_role()
    form = RequestResetForm()
    if form.validate_on_submit():
        user = USER.query.filter_by(EMAIL=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('main.login'))
    return render_template('reset_request.html', title='Reset Password', form=form)

@main.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    check_role()
    user = USER.verify_reset_token(token)
    if user is None:
        flash('That is an invalid token or expired token', 'warning')
        return redirect(url_for('main.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.PASSWORD = hashed_password
        print(user.PASSWORD)
        db.session.add(user)
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('main.login'))
    return render_template('reset_token.html', title='Reset Password', form=form)

@main.route("/change_password", methods=['GET', 'POST'])
@login_required(role="ANY")
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if bcrypt.check_password_hash(current_user.PASSWORD, form.old_password.data):
            if bcrypt.check_password_hash(current_user.PASSWORD, form.new_password.data):
                flash('New password cannot be the same as old password', 'danger')
            else:
                hashed_password = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
                current_user.PASSWORD = hashed_password
                db.session.commit()
                flash('Your password has been updated!', 'success')
                return redirect(url_for('main.profile'))
        else:
            flash('Incorrect old password', 'danger')
    return render_template('change_password.html', title='Change Password', form=form)