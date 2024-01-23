from flask import Blueprint, render_template, url_for, flash, redirect, request
from flask_login import current_user
from website.routes.main import login_required
from website import app, db
from website.models import *
from website.forms import *
from PIL import Image
import secrets
import os

admin = Blueprint('admin', __name__)

def save_payout(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/payout_pics', picture_fn)
    output_size = (125,125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn

@admin.route("/dashboard/admin", methods=['GET', 'POST'])
@login_required(role="admin")
def admin_dashboard():
    payoutform = PayoutForm(prefix="payoutform")
    updatepayoutform = UpdatePayoutForm(prefix="updatepayoutform")
    per_page = 5
    users = USER.query.all()
    user_page = request.args.get('user_page', 1, type=int)
    start_user_index = (user_page - 1) * per_page
    end_user_index = start_user_index + per_page
    paginated_users = users[start_user_index:end_user_index]

    menus = FOOD_MENU.query.all()
    menu_page = request.args.get('menu_page', 1, type=int)
    start_menu_index = (menu_page - 1) * per_page
    end_menu_index = start_menu_index + per_page
    paginated_menus = menus[start_menu_index:end_menu_index]
    students = STUDENT.query.all()

    foodorders = FOOD_ORDER.query.all()
    orders = sorted(foodorders, key=lambda x: x.transaction.DATE_TIME if x.transaction else None, reverse=True)
    order_page = request.args.get('order_page', 1, type=int)
    start_order_index = (order_page - 1) * per_page
    end_order_index = start_order_index + per_page
    paginated_orders = orders[start_order_index:end_order_index]

    trans = TRANSACTION.query.all()
    transactions = sorted(trans, key=lambda x: x.DATE_TIME, reverse=True)
    transaction_page = request.args.get('transaction_page', 1, type=int)
    start_transaction_index = (transaction_page - 1) * per_page
    end_transaction_index = start_transaction_index + per_page
    paginated_transactions = transactions[start_transaction_index:end_transaction_index]

    pay = PAYOUT.query.all()
    payouts = sorted(pay, key=lambda x: x.DATE_TIME, reverse=True)
    payout_page = request.args.get('payout_page', 1, type=int)
    start_payout_index = (payout_page - 1) * per_page
    end_payout_index = start_payout_index + per_page
    paginated_payouts = payouts[start_payout_index:end_payout_index]

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
        return redirect(url_for('admin.admin_dashboard'))
    
    # Update Menu Visibility
    menuform = AdminUpdateMenuForm()
    if menuform.validate_on_submit():
        menu = FOOD_MENU.query.filter_by(SET=menuform.set.data).first()
        menu.SET = menuform.set.data
        menu.VISIBILITY = menuform.visibility.data
        db.session.commit()
        flash(f'Menu {menu.SET} Visibility has been updated!', 'success')
        return redirect(url_for('admin.admin_dashboard'))
    
    # Add Payout
    if payoutform.submit.data and payoutform.validate_on_submit():
        payout_error = PAYOUT.query.filter_by(REFERENCE=payoutform.reference.data).first()
        if payout_error:
            flash(f'Failed to add payout. This reference has already exists in your database.', 'danger')
            return redirect(url_for('admin.admin_dashboard') + '#payout')
        elif payoutform.amount.data < 0 or payoutform.amount.data == 0:
            flash(f'Failed to add payout. Please enter a valid amount.', 'danger')
            return redirect(url_for('admin.admin_dashboard') + '#payout')
        elif  payoutform.picture.data.filename[-4:] not in ['.jpg', '.png', 'jpeg']:
            flash(f'Update failed. Invalid file type. Only jpg, png, and jpeg are allowed.', 'danger')
            return redirect(url_for('admin.admin_dashboard') + '#payout')
        image_file = save_payout(payoutform.picture.data)
        addpayout = PAYOUT(ADMIN_ID=current_user.id, AMOUNT=payoutform.amount.data, IMAGE=image_file, REFERENCE=payoutform.reference.data, DATE_TIME=datetime.now().replace(microsecond=0))
        with app.app_context():
            db.session.add(addpayout)
            db.session.commit()
        flash(f'Payout has been added successfully', 'success')
        return redirect(url_for('admin.admin_dashboard'))
    
    # Update Payout
    elif updatepayoutform.submit.data and updatepayoutform.validate_on_submit():
        payout = PAYOUT.query.filter_by(id=updatepayoutform.id.data).first()
        payout_error = PAYOUT.query.filter_by(REFERENCE=updatepayoutform.reference.data).first()
        if payout_error and (payout.REFERENCE != updatepayoutform.reference.data):
            flash(f'Update failed. This reference has already exists in your database.', 'danger')
            return redirect(url_for('admin.admin_dashboard') + '#payout')
        elif updatepayoutform.amount.data < 0 or updatepayoutform.amount.data == 0:
            flash(f'Update failed. Please enter a valid amount.', 'danger')
            return redirect(url_for('admin.admin_dashboard') + '#payout')
        if updatepayoutform.picture.data:
            if updatepayoutform.picture.data.filename[-4:] not in ['.jpg', '.png', 'jpeg']:
                flash(f'Update failed. Invalid file type. Only jpg, png, and jpeg are allowed.', 'danger')
                return redirect(url_for('admin.admin_dashboard') + '#payout')
            else:
                picture_file = save_payout(updatepayoutform.picture.data)
                payout.IMAGE = picture_file
        else:
            payout.IMAGE = payout.IMAGE
        payout.AMOUNT = updatepayoutform.amount.data
        payout.REFERENCE = updatepayoutform.reference.data
        db.session.commit()
        flash('Payout has been updated successfully!', 'success')
        return redirect(url_for('admin.admin_dashboard'))
    
    profileform = UpdateProfileForm()
    return render_template('admin/dashboard.html', form=form, payoutform=payoutform, updatepayoutform=updatepayoutform, profileform=profileform, students=students, menuform=menuform, paginated_menus=paginated_menus, users=users, paginated_users=paginated_users, paginated_orders=paginated_orders, paginated_transactions=paginated_transactions, paginated_payouts=paginated_payouts, user_page=user_page, menu_page=menu_page, order_page=order_page, transaction_page=transaction_page, payout_page=payout_page,
                            per_page=per_page, total_menus=len(menus), total_users=len(users), total_orders=len(orders), total_transactions=len(transactions), total_payouts=len(payouts), title='Admin Dashboard', orders=orders, transactions=transactions, payouts=payouts, menus=menus)

@admin.route('/dashboard/admin/deletepayout/<int:id>',methods=['POST'])
def deletepayout(id):
    payout=PAYOUT.query.get_or_404(id)
    if request.method=='POST':
        db.session.delete(payout)
        db.session.commit()
        flash(f'Payout recorded at {payout.DATE_TIME} was deleted successfully','success')
        return redirect(url_for('admin.admin_dashboard'))
    return redirect(url_for('admin.admin_dashboard'))
