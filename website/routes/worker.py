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
    orders = FOOD_ORDER.query.all()
    transactions = TRANSACTION.query.all()
    users = USER.query.all()

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
        return redirect(url_for('worker.worker_dashboard'))
    
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
        return redirect(url_for('worker.worker_dashboard'))
    
    # Add Menu
    elif menuform.submit.data and menuform.validate_on_submit():
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
        return redirect(url_for('worker.worker_dashboard'))
    
    return render_template('worker/dashboard.html', fooditem=fooditem, foodmenu=foodmenu, orders=orders, transactions=transactions, users=users, itemform=itemform, itemupdateform=itemupdateform, menuform=menuform, menuupdateform=menuupdateform)

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