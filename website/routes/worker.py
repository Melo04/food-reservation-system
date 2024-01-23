from flask import Blueprint, render_template, url_for, flash, redirect, request, jsonify
from website.routes.main import login_required
from website import app, db
from website.models import *
from website.forms import *
from PIL import Image
import secrets
import os

worker = Blueprint('worker', __name__)

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

@worker.route("/dashboard/worker", methods=['GET', 'POST'])
@login_required(role="worker")
def worker_dashboard():
    fooditem = FOOD_ITEM.query.all()
    foodmenu = FOOD_MENU.query.all()
    foodorders = FOOD_ORDER.query.all()
    transactions = TRANSACTION.query.all()
    users = USER.query.all()
    orders = sorted(foodorders, key=lambda x: x.transaction.DATE_TIME if x.transaction else None, reverse=True)

    per_page = 5
    food_item_page = request.args.get('food_item_page', 1, type=int)
    start_item_index = (food_item_page - 1) * per_page
    end_item_index = start_item_index + per_page
    paginated_items = fooditem[start_item_index:end_item_index]

    food_menu_page = request.args.get('food_menu_page', 1, type=int)
    start_menu_index = (food_menu_page - 1) * per_page
    end_menu_index = start_menu_index + per_page
    paginated_menus = foodmenu[start_menu_index:end_menu_index]

    order_page = request.args.get('order_page', 1, type=int)
    start_order_index = (order_page - 1) * per_page
    end_order_index = start_order_index + per_page
    paginated_orders = orders[start_order_index:end_order_index]

    itemform = ItemForm(prefix="itemform")
    itemupdateform = UpdateItemForm(prefix="itemupdateform")
    menuform = MenuForm(prefix="menuform")
    menuform.main_course.choices = [(item.id, item.NAME) for item in FOOD_ITEM.query.filter_by(TYPE='Main Course').all()]
    menuform.beverage.choices = [(item.id, item.NAME) for item in FOOD_ITEM.query.filter_by(TYPE='Beverage').all()]
    menuupdateform = UpdateMenuForm(prefix="menuupdateform")
    menuupdateform.main_course.choices = [(item.id, item.NAME) for item in FOOD_ITEM.query.filter_by(TYPE='Main Course').all()]
    menuupdateform.beverage.choices = [(item.id, item.NAME) for item in FOOD_ITEM.query.filter_by(TYPE='Beverage').all()]
        
    # Add Food Item
    if itemform.submit.data and itemform.validate_on_submit():
        name = itemform.name.data
        type = itemform.type.data
        quantity = itemform.quantity.data
        remarks = itemform.remarks.data
        name_error = FOOD_ITEM.query.filter_by(NAME=name).first() 
        if name_error:
            flash(f'Failed to add Food Item. {name} already exists in your database', 'danger')
            return redirect(url_for('worker.worker_dashboard') + '#food_item')
        elif quantity < 2:
            flash(f'Failed to add Food Item. Quantity cannot be less than 3', 'danger')
            return redirect(url_for('worker.worker_dashboard') + '#food_item')
        elif quantity > 10000:
            flash(f'Failed to add Food Item. Quantity cannot be more than 10,000', 'danger')
            return redirect(url_for('worker.worker_dashboard') + '#food_item')
        add_item = FOOD_ITEM(NAME=name, TYPE=type, QUANTITY=quantity,REMARKS=remarks)
        with app.app_context():
            db.session.add(add_item)
            db.session.commit()
        flash(f'{name} has been added to your database', 'success')
        return redirect(url_for('worker.worker_dashboard'))
    
    # Update Food Item
    elif itemupdateform.submit.data and itemupdateform.validate_on_submit():
        item = FOOD_ITEM.query.filter_by(id=itemupdateform.id.data).first()
        name_error = FOOD_ITEM.query.filter_by(NAME=itemupdateform.name.data).first()
        if name_error and (item.NAME != itemupdateform.name.data): 
            flash(f'Update failed. {itemupdateform.name.data} already exists in your database', 'danger')
            return redirect(url_for('worker.worker_dashboard') + '#food_item')
        elif itemupdateform.quantity.data < 2:
            flash(f'Update failed. Quantity cannot be less than 3', 'danger')
            return redirect(url_for('worker.worker_dashboard') + '#food_item')
        elif itemupdateform.quantity.data > 10000:
            flash(f'Updated failed. Quantity cannot be more than 10,000', 'danger')
            return redirect(url_for('worker.worker_dashboard') + '#food_item')
        item.id = itemupdateform.id.data
        item.NAME = itemupdateform.name.data
        item.TYPE = itemupdateform.type.data
        item.QUANTITY = itemupdateform.quantity.data
        item.REMARKS = itemupdateform.remarks.data
        db.session.commit()
        flash(f'{item.NAME} has been updated','success')
        return redirect(url_for('worker.worker_dashboard'))
    
    # Add Menu
    elif menuform.submit.data and menuform.validate_on_submit():
        menu_error = FOOD_MENU.query.filter_by(SET=menuform.set.data).first()
        if menu_error:
            flash(f'Failed to Add Menu. Menu Set {menuform.set.data} already exists in your database', 'danger')
            return redirect(url_for('worker.worker_dashboard') + '#food_menu')
        elif menuform.price.data < 0 or menuform.price.data == 0:
            flash(f'Failed to Add Menu. Please enter a valid price', 'danger')
            return redirect(url_for('worker.worker_dashboard') + '#food_menu')
        elif menuform.picture.data.filename[-4:] not in ['.jpg', '.png', 'jpeg']:
            flash('Failed to Add Menu. Invalid file type. Only jpg, jpeg and png extensions are allowed.', 'danger')
            return redirect(url_for('worker.worker_dashboard') + '#food_menu')
        if menuform.picture.data:
            image_file = save_menupic(menuform.picture.data)
        else:
            image_file = 'default.jpg'
        addmenu = FOOD_MENU(SET=menuform.set.data, PRICE=menuform.price.data, TYPE=menuform.type.data, DESCRIPTION=menuform.desc.data, IMAGE=image_file, VISIBILITY=menuform.visibility.data, MAIN_COURSE_ID=menuform.main_course.data, BEVERAGE_ID=menuform.beverage.data)
        with app.app_context():
            db.session.add(addmenu)
            db.session.commit()
        flash(f'The menu {menuform.set.data} has been added to your database', 'success')
        return redirect(url_for('worker.worker_dashboard'))
    
    # Update Menu
    elif menuupdateform.submit.data and menuupdateform.validate_on_submit():
        menu = FOOD_MENU.query.filter_by(id=menuupdateform.id.data).first()
        menu_error = FOOD_MENU.query.filter_by(SET=menuupdateform.set.data).first()
        if menu_error and (menu.SET != menuupdateform.set.data):
            flash(f'Update failed. Menu Set {menuupdateform.set.data} already exists in your database', 'danger')
            return redirect(url_for('worker.worker_dashboard') + '#food_menu')
        elif menuupdateform.price.data < 0 or menuupdateform.price.data == 0:
            flash(f'Update failed. Please enter a valid price', 'danger')
            return redirect(url_for('worker.worker_dashboard') + '#food_menu')
        if menuupdateform.picture.data:
            if menuupdateform.picture.data.filename[-4:] not in ['jpg', 'png', 'jpeg']:
                flash('Update failed. Invalid file type. Only jpg, jpeg and png extensions are allowed.', 'danger')
                return redirect(url_for('worker.worker_dashboard') + '#food_menu')
            else:
                picture_file = save_menupic(menuupdateform.picture.data)
                menu.IMAGE = picture_file
        else:
            menu.IMAGE = menu.IMAGE
        menu.id = menuupdateform.id.data
        menu.SET = menuupdateform.set.data
        menu.PRICE = menuupdateform.price.data
        menu.TYPE = menuupdateform.type.data
        menu.DESCRIPTION = menuupdateform.desc.data
        menu.MAIN_COURSE_ID = menuupdateform.main_course.data
        menu.BEVERAGE_ID = menuupdateform.beverage.data
        menu.VISIBILITY=menuupdateform.visibility.data
        db.session.commit()
        flash(f'Menu {menu.SET} has been updated','success')
        return redirect(url_for('worker.worker_dashboard'))
    
    return render_template('worker/dashboard.html', fooditem=fooditem, foodmenu=foodmenu, orders=orders, transactions=transactions, users=users, itemform=itemform, itemupdateform=itemupdateform, menuform=menuform, menuupdateform=menuupdateform, paginated_items=paginated_items, paginated_menus=paginated_menus, paginated_orders=paginated_orders, food_item_page=food_item_page, food_menu_page=food_menu_page, order_page=order_page, per_page=per_page, total_items=len(fooditem), total_menus=len(foodmenu), total_orders=len(orders))

@worker.route('/dashboard/worker/deleteitem/<int:id>',methods=['POST'])
def deleteitem(id):
    item=FOOD_ITEM.query.get_or_404(id)
    if request.method=='POST':
        db.session.delete(item)
        db.session.commit()
        flash(f'{item.NAME} was deleted from your record','success')
        return redirect(url_for('worker.worker_dashboard'))
    return redirect(url_for('worker.worker_dashboard'))

@worker.route('/dashboard/worker/deletemenu/<int:id>',methods=['POST'])
def deletemenu(id):
    menu=FOOD_MENU.query.get_or_404(id)
    if request.method=='POST':
        db.session.delete(menu)
        db.session.commit()
        flash(f'The menu {menu.SET} was deleted from your record','success')
        return redirect(url_for('worker.worker_dashboard'))
    flash(f'Cannot delete the menu','danger')
    return redirect(url_for('worker.worker_dashboard'))
    
@worker.route('/scanqr')
def scanqr():
    return render_template('worker/scanner.html')

@worker.route('/update_redemption', methods=['POST'])
def update_redemption():
    data = request.get_json()
    order_id = data.get('order_id')
    print(order_id)
    food_order = FOOD_ORDER.query.filter_by(id=order_id).first()
    if food_order:
        food_order.REDEMPTION =True
        db.session.commit()
        return jsonify({'message': 'Redemption updated successfully'})
    else:
        return jsonify({'error': 'Food order not found'}), 404