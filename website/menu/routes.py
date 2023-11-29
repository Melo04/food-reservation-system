import os
import secrets
from flask import render_template, session, request, redirect, url_for, flash
from website import db,app
from .forms import Addmenus
from .models import Addmenu

@app.route('/dashboard/worker/addmenu', methods=['POST', 'GET'])
def addmenu():
    form = Addmenus(request.form)
    if request.method == 'POST':
        name = form.name.data
        price = form.price.data
        type = form.type.data
        desc = form.desc.data
        image_file = form.picture.data
        addmenu = Addmenu(name=name, price=price, type=type, desc=desc, image_file=image_file)
        with app.app_context():
            db.session.add(addmenu)
            db.session.commit()
        flash(f'The menu {name} has been added to your database', 'success')
        return redirect(url_for('worker_dashboard'))
    return render_template('worker/addmenu.html', title="Add Menu Page", form=form)

@app.route('/dashboard/worker/updatemenu/<int:id>',methods=['GET','POST'])
def updatemenu(id):
    menu =Addmenu.query.get_or_404(id)
    form = Addmenus(request.form)
    if request.method=='POST':
        menu.name=form.name.data
        menu.price=form.price.data
        menu.type=form.type.data
        menu.desc=form.desc.data
        db.session.commit()
        flash(f'You menu {menu.name} has been updated','success')
        return redirect(url_for('worker_dashboard'))
    form.name.data=menu.name
    form.price.data=menu.price
    form.type.data=menu.type
    form.desc.data=menu.desc
    return render_template('worker/updatemenu.html',form=form,menu=menu)

@app.route('/dashboard/worker/deleteproduct/<int:id>',methods=['POST'])
def deletemenu(id):
    menu=Addmenu.query.get_or_404(id)
    if request.method=='POST':
        db.session.delete(menu)
        db.session.commit()
        flash(f'The menu {menu.name} was deleted from your record','success')
        return redirect(url_for('worker_dashboard'))
    flash(f'Cannot delete the menu','danger')
    return redirect(url_for('worker_dashboard'))

    