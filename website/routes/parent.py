from flask import Blueprint, render_template, url_for, flash, redirect, request, session
from flask_login import current_user
from website.routes.main import login_required
from website import app, db
from website.models import *
from website.forms import *
import decimal
import stripe

parent = Blueprint('parent', __name__)

@parent.route("/dashboard/parent", methods=['GET', 'POST'])
@login_required(role="parent")
def parent_dashboard():
    menus = FOOD_MENU.query.all()
    users = USER.query.all()
    trans = TRANSACTION.query.filter_by(PARENT_ID=current_user.id).all()
    transactions = sorted(trans, key=lambda x: x.DATE_TIME, reverse=True)
    loads = RELOAD.query.filter_by(PARENT_ID=current_user.id).all()
    reloads = sorted(loads, key=lambda x: x.DATE_TIME, reverse=True)
    foodorders = FOOD_ORDER.query.filter_by(PARENT_ID=current_user.id).all()
    orders = sorted(foodorders, key=lambda x: x.transaction.DATE_TIME if x.transaction else None, reverse=True)

    per_page = 5
    order_page = request.args.get('order_page', 1, type=int)
    start_order_index = (order_page - 1) * per_page
    end_order_index = start_order_index + per_page
    paginated_orders = orders[start_order_index:end_order_index]

    transaction_page = request.args.get('transaction_page', 1, type=int)
    start_transaction_index = (transaction_page - 1) * per_page
    end_transaction_index = start_transaction_index + per_page
    paginated_transactions = transactions[start_transaction_index:end_transaction_index]

    reload_page = request.args.get('reload_page', 1, type=int)
    start_reload_index = (reload_page - 1) * per_page
    end_reload_index = start_reload_index + per_page
    paginated_reloads = reloads[start_reload_index:end_reload_index]

    return render_template('parent/dashboard.html', users=users,orders=orders, transactions=transactions, reloads=reloads,menus=menus, per_page=per_page, paginated_orders=paginated_orders, paginated_transactions=paginated_transactions, paginated_reloads=paginated_reloads, order_page=order_page, transaction_page=transaction_page, reload_page=reload_page, total_orders=len(orders), total_transactions=len(transactions), total_reloads=len(reloads))

@parent.route("/foodmenu", methods=['GET', 'POST'])
@login_required(role="parent")
def parent_menu():
    form = CartForm()
    users = USER.query.all()
    menus = FOOD_MENU.query.all()
    students = STUDENT.query.all()
    return render_template('parent/foodmenu.html', users=users,menus=menus, students = students, form=form)

@parent.route("/cart", methods=['GET', 'POST'])
@login_required(role="parent")
def parent_cart():
    form = CartForm()
    users = USER.query.all()
    menus = FOOD_MENU.query.all()
    form.parent_id.data = current_user.id
    parent_id = form.parent_id.data
    balancedecimal = PARENT.query.filter_by(id=parent_id).with_entities(PARENT.EWALLET_BALANCE).all()
    balanceonedp= float(balancedecimal[0][0])
    balancefloat = float(balanceonedp)
    balance = "{:.2f}".format(balancefloat)

    import re
    if request.method == 'POST':
        for key, value in request.form.items():
            if key.startswith('menu_id_'):
                match = re.match(r'menu_id_(\d+)', key)
                if match:
                    index = match.group(1)
                    menu_id = request.form.get(f'menu_id_{index}')
                    day = request.form.get(f'Day_{index}')
                    student_id = request.form.get('StudentID')

                    if menu_id and day and student_id:
                        add_item = CART_ITEM(PARENT_ID=parent_id, MENU_ID=menu_id, STUDENT_ID=student_id, ORDER_PER_DAY=day)
                        with app.app_context():
                            db.session.add(add_item)
                            db.session.commit()
                            flash('Items added to cart!', 'success')
                    return redirect(url_for('parent.parent_cart'))
    
    cart_items = CART_ITEM.query.filter_by(PARENT_ID=parent_id).all()
    prices = {menu.id: menu.PRICE for menu in menus}
    total_price = sum(prices[cart_item.MENU_ID] for cart_item in cart_items)
    return render_template('parent/cart.html', users=users,form=form, parent_id=parent_id, menu_id=request.form.get('menu_id'), carts=cart_items, menus=menus,total_price=total_price,balance=balance)

@parent.route('/cart/delete/<int:cart_id>', methods=['POST'])
@login_required(role="parent")
def deleteCart(cart_id):
    deleteCart = CART_ITEM.query.get_or_404(cart_id)

    if request.method == 'POST':
        db.session.delete(deleteCart)
        db.session.commit()
        flash('Menu deleted!', 'success')
        return redirect(url_for('parent.parent_cart'))

    return redirect(url_for('parent.parent_cart'))

@parent.route('/cart/pay', methods=['POST'])
@login_required(role="parent")
def pay():
    parent_id = current_user.id
    menus = FOOD_MENU.query.all()
    cart_items = CART_ITEM.query.filter_by(PARENT_ID=parent_id).all()
    payment_time = datetime.now().replace(microsecond=0)
    
    prices = {menu.id: menu.PRICE for menu in menus}
    total_price = sum(prices[cart_item.MENU_ID] for cart_item in cart_items)

    current_parent = PARENT.query.filter_by(id=current_user.id).first()
    decimal_price = decimal.Decimal(total_price)
    
    print("cart_items:", cart_items)

    if not cart_items:
        flash('No items in the cart.', 'error')
    if current_parent.EWALLET_BALANCE >= total_price:
        current_parent.EWALLET_BALANCE -= decimal_price
        db.session.commit()
        for cart_item in cart_items:
            paid = TRANSACTION(
                PARENT_ID=cart_item.PARENT_ID,
                AMOUNT=total_price,
                DATE_TIME=payment_time
            )
        db.session.add(paid)
        db.session.commit()
        transactionid = TRANSACTION.query.filter_by(PARENT_ID=parent_id).order_by(TRANSACTION.DATE_TIME.desc()).first()
        for cart_item in cart_items:
                foodorder = FOOD_ORDER(
                    ORDER_DAY=cart_item.ORDER_PER_DAY,
                    REDEMPTION=False,
                    MENU_ID=cart_item.MENU_ID,
                    PARENT_ID=cart_item.PARENT_ID,
                    STUDENT_ID=cart_item.STUDENT_ID,
                    TRANSACTION_ID=transactionid.id
                    )
                db.session.add(foodorder)    
                db.session.delete(cart_item)
        db.session.commit()
        flash('Payment successful!', 'success')
    else:
        flash('Insufficient balance. Please reload your e-wallet.', 'error')

    return redirect(url_for('parent.parent_cart'))

def clear_reload_session():
    session.pop('reload_amount', None)
    session.pop('reload_init_datetime', None)
    session.pop('reload_session_id', None)
    session.pop('reload_completion_datetime', None)

@parent.route("/reload", methods=['GET', 'POST'])
@login_required(role="parent")
def parent_reload():
    current_parent = PARENT.query.filter_by(id=current_user.id).first()
    balance = current_parent.EWALLET_BALANCE

    clear_reload_session()
    reloadForm = ReloadForm()

    return render_template('parent/reload/reload.html', username=current_user.USERNAME, showBalance=True, balance=balance, reloadForm=reloadForm)

@parent.route("/reload/validate", methods=['GET', 'POST'])
@login_required(role="parent")
def reload_validate():
    if request.method == 'GET':
        return redirect('/404')

    reloadForm = ReloadForm()
    if reloadForm.validate_on_submit():
        session['reload_amount'] = reloadForm.amount.data
        session['reload_init_datetime'] = datetime.now().replace(microsecond=0)
        return redirect(url_for('parent.reload_confirm'), code=307)
    else:
        flash('Reload amount is minimum RM2 and maximum RM10,000', 'error')
        return redirect(url_for('parent.parent_reload'))


@parent.route("/reload/confirm", methods=['GET', 'POST'])
@login_required(role="parent")
def reload_confirm():
    if request.method == 'GET' or not session.get('reload_init_datetime'):
        return redirect(url_for('parent.parent_reload'))

    date_time = str(session['reload_init_datetime'])[:-6]
    amount = "{:.2f}".format(session['reload_amount'])

    return render_template("parent/reload/confirm.html", username=current_user.USERNAME, showDatetime=True, date_time=date_time, showAmount=True, amount=amount)

@parent.route('/reload/charge', methods=['GET', 'POST'])
@login_required(role="parent")
def reload_charge():
    if request.method == 'GET' or not session.get('reload_init_datetime'):
        return redirect(url_for('parent.parent_reload'))
    
    amount = session['reload_amount'] * 100.0 # amount is in cents
    checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price_data': {
                        'product_data': {
                            'name': 'LunchMate E-wallet Reload',
                        },
                        'unit_amount': int(amount), 
                        'currency': 'myr',
                    },
                    'quantity': 1,
                },
            ],
            payment_method_types=['card'],
            mode='payment',
            currency= 'myr',
            success_url=request.host_url + url_for('parent.reload_success_redirect', key=app.config['STRIPE_PUBLISHABLE_KEY']) + '?r=true',
            cancel_url=request.host_url + url_for('parent.reload_success_redirect', key=app.config['STRIPE_PUBLISHABLE_KEY']) + '?r=false',
        )
    session['reload_session_id'] = checkout_session.id

    return redirect(checkout_session.url)


@parent.route('/reload/success/<string:key>', methods=['GET', 'POST'])
@login_required(role="parent")
def reload_success_redirect(key):
    if key != app.config['STRIPE_PUBLISHABLE_KEY'] or not session.get('reload_session_id'):
        return redirect('/404')
    
    session['reload_completion_datetime'] = datetime.now().replace(microsecond=0)
    
    if request.args['r'] == 'true':
        success = True

        # store reload history
        reload = RELOAD(
            PARENT_ID = current_user.id,
            AMOUNT = session['reload_amount'],
            DATE_TIME = session['reload_completion_datetime']
        )
        db.session.add(reload)    
        db.session.commit()

        # update parent e-wallet balance
        current_parent = PARENT.query.filter_by(id=current_user.id).first()
        decimal_amount = decimal.Decimal(session['reload_amount'])
        current_parent.EWALLET_BALANCE += decimal_amount
        db.session.commit()
    else:
        success = False
        stripe.checkout.Session.expire(session['reload_session_id'])


    return redirect(url_for('parent.reload_success', r=str(success).lower()))


@parent.route('/reload/success', methods=['GET', 'POST'])
@login_required(role="parent")
def reload_success():
    if not session.get('reload_completion_datetime'):
        return redirect(url_for('parent.parent_dashboard'))

    amount = "{:.2f}".format(session['reload_amount'])
    date_time = str(session['reload_completion_datetime'])[:-6]

    if request.args['r'] == 'true':
        success = True
    else:
        success = False

    clear_reload_session()

    return render_template('parent/reload/success.html', success=success, username=current_user.USERNAME, showDatetime=True, date_time=date_time, showAmount=True, amount=amount) # , {"Refresh": "2; url=" + url_for('views.pay.reload')} # for redirecting page
