from functools import wraps
from flask import render_template, url_for, flash, redirect, request, current_app
from website import app, db, bcrypt, mail
from website.forms import RegistrationForm, LoginForm, UpdateProfileForm, RequestResetForm, ResetPasswordForm, AdminUpdateProfileForm, AdminUpdateMenuForm, ItemForm, UpdateItemForm, MenuForm, UpdateMenuForm, CartForm
from website.models import USER, FOOD_ITEM, FOOD_MENU, STUDENT, PARENT, FOOD_ORDER, TRANSACTION, RELOAD, CART_ITEM
from flask_login import login_user, current_user, logout_user
from flask_mail import Message
import secrets
import os
from PIL import Image
from datetime import datetime

with app.app_context():
    db.create_all()

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
            return redirect(url_for('parent_dashboard'))
        elif current_user.ROLE == 'student':
            return redirect(url_for('student_dashboard'))
        elif current_user.ROLE == 'worker':
            return redirect(url_for('worker_dashboard'))
        elif current_user.ROLE == 'admin':
            return redirect(url_for('admin_dashboard'))
    return render_template('home.html')

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/dashboard/parent", methods=['GET', 'POST'])
@login_required(role="parent")
def parent_dashboard():
    orders = FOOD_ORDER.query.filter_by(PARENT_ID=current_user.id).all()
    transactions = TRANSACTION.query.filter_by(PARENT_ID=current_user.id).all()
    reloads = RELOAD.query.filter_by(PARENT_ID=current_user.id).all()
    return render_template('parent/dashboard.html', orders=orders, transactions=transactions, reloads=reloads)

@app.route("/foodmenu", methods=['GET', 'POST'])
@login_required(role="parent")
def parent_menu():
    form = CartForm()
    menus = FOOD_MENU.query.all()
    students = STUDENT.query.all()
    return render_template('parent/foodmenu.html', menus=menus, students = students, form=form)

@app.route("/cart", methods=['GET', 'POST'])
@login_required(role="parent")
def parent_cart():
    form = CartForm()
    menus = FOOD_MENU.query.all()
    form.parent_id.data = current_user.id
    parent_id = form.parent_id.data
    balancedecimal = PARENT.query.filter_by(id=parent_id).with_entities(PARENT.EWALLET_BALANCE).all()
    balanceonedp= float(balancedecimal[0][0])
    balancefloat = float(balanceonedp)
    balance = "{:.2f}".format(balancefloat)

    import re
    if request.method == 'POST':
        print("Form data:", request.form)
        for key, value in request.form.items():
            if key.startswith('menu_id_'):
                match = re.match(r'menu_id_(\d+)', key)
                if match:
                    index = match.group(1)
                    menu_id = request.form.get(f'menu_id_{index}')
                    day = request.form.get(f'Day_{index}')
                    student_id = request.form.get('StudentID')
                    print('Menu ID: ', menu_id)
                    print('Day: ', day)
                    print('Student ID: ', student_id)

                    if menu_id and day and student_id:
                        add_item = CART_ITEM(PARENT_ID=parent_id, MENU_ID=menu_id, STUDENT_ID=student_id, ORDER_PER_DAY=day)
                        with app.app_context():
                            db.session.add(add_item)
                            db.session.commit()
                    flash('Items added to cart!', 'success')
                    return redirect(url_for('parent_cart'))
    
    cart_items = CART_ITEM.query.filter_by(PARENT_ID=parent_id).all()
    prices = {menu.id: menu.PRICE for menu in menus}
    total_price = sum(prices[cart_item.MENU_ID] for cart_item in cart_items)
    return render_template('parent/cart.html', form=form, parent_id=parent_id, menu_id=request.form.get('menu_id'), carts=cart_items, menus=menus,total_price=total_price,balance=balance)

@app.route('/cart/delete/<int:cart_id>', methods=['POST'])
@login_required(role="parent")
def deleteCart(cart_id):
    deleteCart = CART_ITEM.query.get_or_404(cart_id)

    if request.method == 'POST':
        db.session.delete(deleteCart)
        db.session.commit()
        flash('Menu deleted!', 'success')
        return redirect(url_for('parent_cart'))

    return redirect(url_for('parent_cart'))

@app.route('/cart/pay', methods=['POST'])
@login_required(role="parent")
def pay():
    parent_id = current_user.id
    menus = FOOD_MENU.query.all()
    cart_items = CART_ITEM.query.filter_by(PARENT_ID=parent_id).all()
    transactionids = TRANSACTION.query.filter_by(PARENT_ID=parent_id).all()
    payment_time = datetime.now()
    
    prices = {menu.id: menu.PRICE for menu in menus}
    total_price = sum(prices[cart_item.MENU_ID] for cart_item in cart_items)

    balancedecimal = PARENT.query.filter_by(id=parent_id).with_entities(PARENT.EWALLET_BALANCE).all()
    balanceonedp= float(balancedecimal[0][0])

    if balanceonedp >= total_price:
        PARENT.EWALLET_BALANCE -= total_price
        db.session.commit()
    
        for cart_item, transactionid in zip(cart_items, transactionids):
            paid = TRANSACTION(
                PARENT_ID=cart_item.PARENT_ID,
                AMOUNT=total_price,
                DATE_TIME=payment_time
            )
            db.session.add(paid)
            for transactionid in transactionids:
                foodorder = FOOD_ORDER(
                    ORDER_DAY=cart_item.ORDER_PER_DAY,
                    REDEMPTION=False,
                    MENU_ID=cart_item.MENU_ID,
                    PARENT_ID=cart_item.PARENT_ID,
                    STUDENT_ID=cart_item.STUDENT_ID,
                    TRANSACTION_ID=transactionid.id
                    )
                
            db.session.delete(cart_item)
        db.session.add(foodorder)
        db.session.commit()
        flash('Payment successful!', 'success')
    else:
        flash('Insufficient balance. Please reload your e-wallet.', 'error')

    return redirect(url_for('parent_cart'))

@app.route("/reload", methods=['GET', 'POST'])
@login_required(role="parent")
def parent_reload():
    return render_template('parent/reload.html')

@app.route("/dashboard/student", methods=['GET', 'POST'])
@login_required(role="student")
def student_dashboard():
    orders = FOOD_ORDER.query.filter_by(PARENT_ID=current_user.id).all()
    return render_template('student/dashboard.html', orders=orders)

@app.route("/dashboard/worker", methods=['GET', 'POST'])
@login_required(role="worker")
def worker_dashboard():
    fooditem = FOOD_ITEM.query.all()
    foodmenu = FOOD_MENU.query.all()
    orders = FOOD_ORDER.query.all()

    itemform = ItemForm(prefix="itemform")
    itemupdateform = UpdateItemForm(prefix="itemupdateform")
    menuform = MenuForm(prefix="menuform")
    menuform.main_course.choices = [(item.id, item.NAME) for item in FOOD_ITEM.query.filter_by(TYPE='Main Course').all()]
    menuform.beverage.choices = [(item.id, item.NAME) for item in FOOD_ITEM.query.filter_by(TYPE='Beverage').all()]
    menuupdateform = UpdateMenuForm(request.form, prefix="menuupdateform")
    menuupdateform.main_course.choices = [(item.id, item.NAME) for item in FOOD_ITEM.query.filter_by(TYPE='Main Course').all()]
    menuupdateform.beverage.choices = [(item.id, item.NAME) for item in FOOD_ITEM.query.filter_by(TYPE='Beverage').all()]
        
    # Add Food Item
    if itemform.submit.data and itemform.validate_on_submit():
        name = itemform.name.data
        type = itemform.type.data
        quantity = itemform.quantity.data
        remarks = itemform.remarks.data
        add_item = FOOD_ITEM(NAME=name, TYPE=type, QUANTITY=quantity,REMARKS=remarks)
        with app.app_context():
            db.session.add(add_item)
            db.session.commit()
        flash(f'{name} has been added to your database', 'success')
        return redirect(url_for('worker_dashboard'))
    
    # Update Food Item
    elif itemupdateform.submit.data and itemupdateform.validate_on_submit():
        item = FOOD_ITEM.query.filter_by(id=itemupdateform.id.data).first()
        item.id = itemupdateform.id.data
        item.NAME = itemupdateform.name.data
        item.TYPE = itemupdateform.type.data
        item.QUANTITY = itemupdateform.quantity.data
        item.REMARKS = itemupdateform.remarks.data
        db.session.commit()
        flash(f'{item.NAME} has been updated','success')
        return redirect(url_for('worker_dashboard'))
    
    # Add Menu
    elif menuform.submit.data and menuform.validate_on_submit():
        set = menuform.set.data
        price = menuform.price.data
        type = menuform.type.data
        desc = menuform.desc.data
        main_course_id=menuform.main_course.data
        beverage_id=menuform.beverage.data
        visibility=menuform.visibility.data
        if menuform.picture.data:
            image_file = save_menupic(menuform.picture.data)
        else:
            image_file = 'default.jpg'
        addmenu = FOOD_MENU(SET=set, PRICE=price, TYPE=type, DESCRIPTION=desc, IMAGE=image_file, VISIBILITY=visibility, MAIN_COURSE_ID=main_course_id, BEVERAGE_ID=beverage_id)
        with app.app_context():
            db.session.add(addmenu)
            db.session.commit()
        flash(f'The menu {set} has been added to your database', 'success')
        return redirect(url_for('worker_dashboard'))
    
    # Update Menu
    elif menuupdateform.submit.data and request.method == 'POST':
        menu = FOOD_MENU.query.filter_by(id=menuupdateform.id.data).first()
        menu.id = menuupdateform.id.data
        menu.SET = menuupdateform.set.data
        menu.PRICE = menuupdateform.price.data
        menu.TYPE = menuupdateform.type.data
        menu.DESCRIPTION = menuupdateform.desc.data
        menu.MAIN_COURSE_ID = menuupdateform.main_course.data
        menu.BEVERAGE_ID = menuupdateform.beverage.data
        menu.VISIBILITY=menuupdateform.visibility.data
        if menuupdateform.picture.data:
            picture_file = save_menupic(menuupdateform.picture.data)
            menu.IMAGE = picture_file
        db.session.commit()
        flash(f'Menu {menu.SET} has been updated','success')
        return redirect(url_for('worker_dashboard'))
    
    return render_template('worker/dashboard.html', fooditem=fooditem, foodmenu=foodmenu, orders=orders, itemform=itemform, itemupdateform=itemupdateform, menuform=menuform, menuupdateform=menuupdateform)

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

@app.route("/dashboard/admin", methods=['GET', 'POST'])
@login_required(role="admin")
def admin_dashboard():
    per_page = 5
    users = USER.query.all()
    page = request.args.get('page', 1, type=int)
    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    paginated_users = users[start_index:end_index]

    menus = FOOD_MENU.query.all()
    menupage = request.args.get('menupage', 1, type=int)
    start_menu_index = (menupage - 1) * per_page
    end_menu_index = start_index + per_page
    paginated_menus = menus[start_menu_index:end_menu_index]
    students = STUDENT.query.all()

    # Update User Status
    form = AdminUpdateProfileForm()
    if form.validate_on_submit():
        user = USER.query.filter_by(USERNAME=form.username.data).first()
        user.USERNAME = form.username.data
        if user.ROLE == 'student':
            student = STUDENT.query.filter_by(id=user.id).first()
            student.STATUS = form.status.data
        db.session.commit()
        flash('User profile has been updated!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    # Update Menu Visibility
    menuform = AdminUpdateMenuForm()
    if menuform.validate_on_submit():
        menu = FOOD_MENU.query.filter_by(SET=menuform.set.data).first()
        menu.SET = menuform.set.data
        menu.VISIBILITY = menuform.visibility.data
        db.session.commit()
        flash(f'Menu {menu.SET} Visibility has been updated!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    profileform = UpdateProfileForm()
    orders = FOOD_ORDER.query.all()
    transactions = TRANSACTION.query.all()
    reloads = RELOAD.query.all()
    return render_template('admin/dashboard.html', form=form, profileform=profileform, students=students, menuform=menuform, menus=paginated_menus, users=paginated_users, page=page, menupage=menupage, per_page=per_page, total_menus=len(menus), total_users=len(users), title='Admin Dashboard', orders=orders, transactions=transactions, reloads=reloads)

@app.route("/register", methods=['GET', 'POST'])
def register():
    check_role()
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8') 
        if form.role.data == 'parent':
            parent = PARENT(USERNAME=form.username.data, EMAIL=form.email.data, FIRST_NAME=form.firstname.data, LAST_NAME=form.lastname.data, PHONE=form.phone.data, ROLE=form.role.data, PASSWORD=hashed_password, EWALLET_BALANCE=0)
            db.session.add(parent)
            db.session.commit()
        elif form.role.data == 'student':
            student = STUDENT(USERNAME=form.username.data, EMAIL=form.email.data, FIRST_NAME=form.firstname.data, LAST_NAME=form.lastname.data, PHONE=form.phone.data, ROLE=form.role.data, PASSWORD=hashed_password, STATUS='active', PARENT1_ID=form.parent1_id.data, PARENT2_ID=form.parent2_id.data)
            db.session.add(student)
            db.session.commit()
        else:
            user = USER(USERNAME=form.username.data, EMAIL=form.email.data, FIRST_NAME=form.firstname.data, LAST_NAME=form.lastname.data, PHONE=form.phone.data, ROLE=form.role.data, PASSWORD=hashed_password)
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
        user = USER.query.filter_by(USERNAME=form.username.data).first()
        if user and bcrypt.check_password_hash(user.PASSWORD, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            if user.ROLE == 'parent':
                return redirect(next_page) if next_page else redirect(url_for('parent_dashboard'))
            elif user.ROLE == 'student':
                return redirect(next_page) if next_page else redirect(url_for('student_dashboard'))
            elif user.ROLE == 'worker':
                return redirect(next_page) if next_page else redirect(url_for('worker_dashboard'))
            elif user.ROLE == 'admin':
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
            current_user.IMAGE = picture_file
        current_user.USERNAME = form.username.data
        current_user.EMAIL = form.email.data
        current_user.FIRST_NAME = form.firstname.data
        current_user.LAST_NAME = form.lastname.data
        current_user.PHONE = form.phone.data
        if current_user.ROLE == 'parent':
            current_user.EWALLET_BALANCE = form.ewallet_balance.data
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('profile'))
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
{url_for('reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no change will be made.
    '''
    mail.send(msg)

@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    check_role()
    form = RequestResetForm()
    if form.validate_on_submit():
        user = USER.query.filter_by(EMAIL=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)

@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    check_role()
    user = USER.verify_reset_token(token)
    if user is None:
        flash('That is an invalid token or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.PASSWORD = hashed_password
        print(user.PASSWORD)
        db.session.add(user)
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)

@app.route('/dashboard/worker/deleteitem/<int:id>',methods=['POST'])
def deleteitem(id):
    item=FOOD_ITEM.query.get_or_404(id)
    if request.method=='POST':
        db.session.delete(item)
        db.session.commit()
        flash(f'{item.NAME} was deleted from your record','success')
        return redirect(url_for('worker_dashboard'))
    return redirect(url_for('worker_dashboard'))

@app.route('/dashboard/worker/deletemenu/<int:id>',methods=['POST'])
def deletemenu(id):
    menu=FOOD_MENU.query.get_or_404(id)
    if request.method=='POST':
        db.session.delete(menu)
        db.session.commit()
        flash(f'The menu {menu.SET} was deleted from your record','success')
        return redirect(url_for('worker_dashboard'))
    flash(f'Cannot delete the menu','danger')
    return redirect(url_for('worker_dashboard'))