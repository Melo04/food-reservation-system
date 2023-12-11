from functools import wraps
from flask import render_template, url_for, flash, redirect, request, current_app
from website import app, db, bcrypt, mail
from website.forms import RegistrationForm, LoginForm, UpdateProfileForm, RequestResetForm, ResetPasswordForm, AdminUpdateProfileForm, MainCourses, Beverages, Menus, UpdateMainCourses, UpdateBeverages, UpdateMenus, AdminUpdateMenuForm
from website.models import User, Menu, MainCourse, Beverage
from flask_login import login_user, current_user, logout_user
from flask_mail import Message
import secrets
import os
from PIL import Image

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
    menus = Menu.query.all()
    return render_template('parent/dashboard.html', menus=menus)

@app.route("/dashboard/student", methods=['GET', 'POST'])
@login_required(role="student")
def student_dashboard():
    return render_template('student/dashboard.html')

@app.route("/dashboard/worker", methods=['GET', 'POST'])
@login_required(role="worker")
def worker_dashboard():
    return render_template('worker/dashboard.html')

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

def save_menupic(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/menu_pics', picture_fn)
    output_size = (125,125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn

@app.route("/menu/worker", methods=['GET', 'POST'])
@login_required(role="worker")
def worker_menupage():
    main_courses = MainCourse.query.all()
    beverages = Beverage.query.all()
    menus = Menu.query.all()

    mainform = MainCourses(request.form, prefix="mainform")
    mainupdateform = UpdateMainCourses(request.form, prefix="mainupdateform")
    beverageform = Beverages(request.form, prefix="beverageform")
    beverageupdateform = UpdateBeverages(request.form, prefix="beverageupdateform")
    menuform = Menus(request.form, prefix="menuform")
    menuform.main_course.choices = [(main_course.id, main_course.name) for main_course in MainCourse.query.all()]
    menuform.beverage.choices = [(beverage.id, beverage.name) for beverage in Beverage.query.all()]
    menuupdateform = UpdateMenus(request.form, prefix="menuupdateform")
    menuupdateform.main_course.choices = [(main_course.id, main_course.name) for main_course in MainCourse.query.all()]
    menuupdateform.beverage.choices = [(beverage.id, beverage.name) for beverage in Beverage.query.all()]

    # Add Main Course
    if mainform.submit.data and request.method == 'POST':
        name = mainform.name.data
        quantity = mainform.quantity.data
        remarks = mainform.remarks.data
        addmain = MainCourse(name=name, quantity=quantity,remarks=remarks)
        with app.app_context():
            db.session.add(addmain)
            db.session.commit()
        flash(f'{name} has been added to your database', 'success')
        return redirect(url_for('worker_menupage'))
    
    # Update Main Course
    elif mainupdateform.submit.data and request.method == 'POST':
        main_course = MainCourse.query.filter_by(id=mainupdateform.id.data).first()
        main_course.id = mainupdateform.id.data
        main_course.name = mainupdateform.name.data
        main_course.quantity = mainupdateform.quantity.data
        main_course.remarks = mainupdateform.remarks.data
        db.session.commit()
        flash(f'{main_course.name} has been updated','success')
        return redirect(url_for('worker_menupage'))
        
    # Add Beverage
    elif beverageform.submit.data and request.method == 'POST':
        name = beverageform.name.data
        quantity = beverageform.quantity.data
        remarks = beverageform.remarks.data
        add_beverage = Beverage(name=name, quantity=quantity,remarks=remarks)
        with app.app_context():
            db.session.add(add_beverage)
            db.session.commit()
        flash(f'{name} has been added to your database', 'success')
        return redirect(url_for('worker_menupage'))
    
    # Update Beverage
    elif beverageupdateform.submit.data and request.method == 'POST':
        beverage = Beverage.query.filter_by(id=beverageupdateform.id.data).first()
        beverage.id = beverageupdateform.id.data
        beverage.name = beverageupdateform.name.data
        beverage.quantity = beverageupdateform.quantity.data
        beverage.remarks = beverageupdateform.remarks.data
        db.session.commit()
        flash(f'{beverage.name} has been updated','success')
        return redirect(url_for('worker_menupage'))
    
    # Add Menu
    elif menuform.submit.data and request.method == 'POST':
        name = menuform.name.data
        price = menuform.price.data
        type = menuform.type.data
        desc = menuform.desc.data
        main_course_id=menuform.main_course.data
        beverage_id=menuform.beverage.data
        visibility=menuform.visibility.data
        image_file = 'default.jpg'
        if menuform.picture.data:
            image_file = save_menupic(menuform.picture.data)
        else:
            image_file = url_for('static', filename='menu_pics/' + image_file)
        print("========================++==========================")
        print(menuform.picture.data)
        print("=========================++=========================")
        addmenu = Menu(name=name, price=price, type=type, desc=desc, image_file=image_file, main_course_id=main_course_id, beverage_id=beverage_id, visibility=visibility)
        with app.app_context():
            db.session.add(addmenu)
            db.session.commit()
        flash(f'The menu {name} has been added to your database', 'success')
        return redirect(url_for('worker_menupage'))
    
    # Update Menu
    elif menuupdateform.submit.data and request.method == 'POST':
        menu = Menu.query.filter_by(id=menuupdateform.id.data).first()
        menu.id = menuupdateform.id.data
        menu.name = menuupdateform.name.data
        menu.price = menuupdateform.price.data
        menu.type = menuupdateform.type.data
        menu.desc = menuupdateform.desc.data
        menu.main_course_id=menuupdateform.main_course.data
        menu.beverage_id=menuupdateform.beverage.data
        menu.visibility=menuupdateform.visibility.data
        if menuupdateform.picture.data:
            picture_file = save_menupic(menuupdateform.picture.data)
            menu.image_file = picture_file
        db.session.commit()
        flash(f'Menu {menu.name} has been updated','success')
        return redirect(url_for('worker_menupage'))
    
    return render_template('worker/menupage.html', main_courses=main_courses,beverages=beverages,menus=menus, mainform=mainform, mainupdateform=mainupdateform, beverageform=beverageform, beverageupdateform=beverageupdateform, menuform=menuform, menuupdateform=menuupdateform)

@app.route("/dashboard/admin", methods=['GET', 'POST'])
@login_required(role="admin")
def admin_dashboard():
    per_page = 5
    # Fetch User Details
    users = User.query.all()
    page = request.args.get('page', 1, type=int)
    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    paginated_users = users[start_index:end_index]

    # Fetch Menu Details
    menus = Menu.query.all()
    menupage = request.args.get('menupage', 1, type=int)
    start_menu_index = (menupage - 1) * per_page
    end_menu_index = start_index + per_page
    paginated_menus = menus[start_menu_index:end_menu_index]

    # Update User Status
    form = AdminUpdateProfileForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        user.username = form.username.data
        user.status = form.status.data
        db.session.commit()
        flash('User profile has been updated!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    # Update Menu Visibility
    menuform = AdminUpdateMenuForm()
    if menuform.validate_on_submit():
        menu = Menu.query.filter_by(name=menuform.name.data).first()
        menu.name = menuform.name.data
        menu.visibility = menuform.visibility.data
        db.session.commit()
        flash(f'Menu {menu.name} Visibility has been updated!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin/dashboard.html', form=form, menuform=menuform, menus=paginated_menus, users=paginated_users, page=page, menupage=menupage, per_page=per_page, total_menus=len(menus), total_users=len(users), title='Admin Dashboard')

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

@app.route('/menupage/worker/deletemain/<int:id>',methods=['POST'])
def deletemain(id):
    main_course=MainCourse.query.get_or_404(id)
    if request.method=='POST':
        db.session.delete(main_course)
        db.session.commit()
        flash(f'{main_course.name} was deleted from your record','success')
        return redirect(url_for('worker_menupage'))
    return redirect(url_for('worker_menupage'))

@app.route('/menupage/worker/deletebeverage/<int:id>',methods=['POST'])
def delete_beverage(id):
    beverage=Beverage.query.get_or_404(id)
    if request.method=='POST':
        db.session.delete(beverage)
        db.session.commit()
        flash(f'{beverage.name} was deleted from your record','success')
        return redirect(url_for('worker_menupage'))
    return redirect(url_for('worker_menupage'))

@app.route('/dashboard/worker/deletemenu/<int:id>',methods=['POST'])
def deletemenu(id):
    menu=Menu.query.get_or_404(id)
    if request.method=='POST':
        db.session.delete(menu)
        db.session.commit()
        flash(f'The menu {menu.name} was deleted from your record','success')
        return redirect(url_for('worker_menupage'))
    flash(f'Cannot delete the menu','danger')
    return redirect(url_for('worker_menupage'))