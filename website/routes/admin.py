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
    payoutform = PayoutForm()
    per_page = 5
    users = USER.query.all()
    page = request.args.get('page', 1, type=int)
    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    paginated_users = users[start_index:end_index]

    menus = FOOD_MENU.query.all()
    menu_page = request.args.get('menu_page', 1, type=int)
    start_menu_index = (menu_page - 1) * per_page
    end_menu_index = start_menu_index + per_page
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
        print(payoutform.picture.data)
        image_file = save_payout(payoutform.picture.data)
        addpayout = PAYOUT(ADMIN_ID=current_user.id, AMOUNT=payoutform.amount.data, IMAGE=image_file, REFERENCE=payoutform.reference.data, DATE_TIME=datetime.now().replace(microsecond=0))
        with app.app_context():
            db.session.add(addpayout)
            db.session.commit()
        flash(f'Payout has been added successfully', 'success')
        return redirect(url_for('admin.admin_dashboard'))
    
     # Update Payout
    updatepayoutform = UpdatePayoutForm()
    if updatepayoutform.validate_on_submit():
        payout = PAYOUT.query.filter_by(id=updatepayoutform.id.data).first()
        payout.AMOUNT = updatepayoutform.amount.data
        payout.REFERENCE = updatepayoutform.reference.data
        if updatepayoutform.picture.data:
            picture_file = save_payout(updatepayoutform.picture.data)
            payout.IMAGE = picture_file
        db.session.commit()
        flash('Payout has been updated successfully!', 'success')
        return redirect(url_for('admin.admin_dashboard'))
    
    profileform = UpdateProfileForm()
    orders = FOOD_ORDER.query.all()
    transactions = TRANSACTION.query.all()
    payouts = PAYOUT.query.all()
    return render_template('admin/dashboard.html', form=form, payoutform=payoutform, updatepayoutform=updatepayoutform, profileform=profileform, students=students, menuform=menuform, paginated_menus=paginated_menus, users=users, paginated_users=paginated_users, page=page, menu_page=menu_page, per_page=per_page, total_menus=len(menus), total_users=len(users), title='Admin Dashboard', orders=orders, transactions=transactions, payouts=payouts, menus=menus)

@admin.route('/dashboard/admin/deletepayout/<int:id>',methods=['POST'])
def deletepayout(id):
    payout=PAYOUT.query.get_or_404(id)
    if request.method=='POST':
        db.session.delete(payout)
        db.session.commit()
        flash(f'Payout recorded at {payout.DATE_TIME} was deleted successfully','success')
        return redirect(url_for('admin.admin_dashboard'))
    return redirect(url_for('admin.admin_dashboard'))
