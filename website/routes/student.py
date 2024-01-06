from flask import Blueprint, render_template
from flask_login import current_user
from website.routes.main import login_required
from website.models import *
from website.forms import *
import qrcode
from io import BytesIO
from base64 import b64encode

student = Blueprint('student', __name__)

@student.route("/dashboard/student", methods=['GET', 'POST'])
@login_required(role="student")
def student_dashboard():
    orders = FOOD_ORDER.query.filter_by(STUDENT_ID=current_user.id).all()
    menus = FOOD_MENU.query.all()
    transactions = TRANSACTION.query.all()
    orderform = FoodOrderForm()

    today_order = FOOD_ORDER.query.filter_by(STUDENT_ID=current_user.id, ORDER_DAY=datetime.today().strftime('%A')).first()
    base64_img = None
    if today_order:
        memory = BytesIO()
        data = f"{today_order.id}, Order Day:{today_order.ORDER_DAY}, Redemption:{today_order.REDEMPTION}, Menu ID:{today_order.MENU_ID}, Parent ID:{today_order.PARENT_ID}, Student ID:{today_order.STUDENT_ID}, Transaction ID:{today_order.TRANSACTION_ID}"
        img = qrcode.make(data)
        img.save(memory, "PNG")
        memory.seek(0)
        base64_img = "data:image/png;base64," + \
            b64encode(memory.getvalue()).decode('ascii')
    return render_template('student/dashboard.html', orders=orders, menus=menus, transactions=transactions, orderform=orderform, data=base64_img, today_order=today_order)
