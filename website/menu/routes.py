from flask import render_template, session, request, redirect, url_for, flash
from website import db,app
from .forms import Menus
from .models import Menu
from .forms import MainCourses,Beverages
from .models import MainCourse,Beverage

@app.route('/menupage/worker/addmain', methods=['POST', 'GET'])
def addmain():
    form = MainCourses(request.form)
    if request.method == 'POST':
        name = form.name.data
        quantity = form.quantity.data
        remarks = form.remarks.data
        addmain = MainCourse(name=name, quantity=quantity,remarks=remarks)
        with app.app_context():
            db.session.add(addmain)
            db.session.commit()
        flash(f'{name} has been added to your database', 'success')
        return redirect(url_for('worker_menupage'))
    return render_template('worker/manageitem.html', form=form)

@app.route('/menupage/worker/updatemain/<int:id>',methods=['GET','POST'])
def updatemain(id):
    main_course =MainCourse.query.get_or_404(id)
    form = MainCourses(request.form)
    if request.method == 'POST':
        main_course.name = form.name.data
        main_course.quantity = form.quantity.data
        main_course.remarks = form.remarks.data
        db.session.commit()
        flash(f'{main_course.name} has been updated','success')
        return redirect(url_for('worker_menupage'))
    form.name.data=main_course.name
    form.quantity.data=main_course.quantity
    form.remarks.data=main_course.remarks
    return render_template('worker/manageitem.html',form=form,main_course=main_course)

@app.route('/menupage/worker/deletemain/<int:id>',methods=['POST'])
def deletemain(id):
    main_course=MainCourse.query.get_or_404(id)
    if request.method=='POST':
        db.session.delete(main_course)
        db.session.commit()
        flash(f'{main_course.name} was deleted from your record','success')
        return redirect(url_for('worker_menupage'))
    return redirect(url_for('worker_menupage'))

@app.route('/menupage/worker/addbeverage', methods=['POST', 'GET'])
def add_beverage():
    form = Beverages(request.form)
    if request.method == 'POST':
        name = form.name.data
        quantity = form.quantity.data
        remarks = form.remarks.data
        add_beverage = Beverage(name=name, quantity=quantity,remarks=remarks)
        with app.app_context():
            db.session.add(add_beverage)
            db.session.commit()
        flash(f'{name} has been added to your database', 'success')
        return redirect(url_for('worker_menupage'))
    return render_template('worker/manageitem.html',form=form)

@app.route('/menupage/worker/updatebeverage/<int:id>',methods=['GET','POST'])
def update_beverage(id):
    beverage =Beverage.query.get_or_404(id)
    form = Beverages(request.form)
    if request.method == 'POST':
        beverage.name = form.name.data
        beverage.quantity = form.quantity.data
        beverage.remarks = form.remarks.data
        db.session.commit()
        flash(f'{beverage.name} has been updated','success')
        return redirect(url_for('worker_menupage'))
    form.name.data=beverage.name
    form.quantity.data=beverage.quantity
    form.remarks.data=beverage.remarks
    return render_template('worker/manageitem.html',form=form,beverage=beverage)

@app.route('/menupage/worker/deletebeverage/<int:id>',methods=['POST'])
def delete_beverage(id):
    beverage=Beverage.query.get_or_404(id)
    if request.method=='POST':
        db.session.delete(beverage)
        db.session.commit()
        flash(f'{beverage.name} was deleted from your record','success')
        return redirect(url_for('worker_menupage'))
    return redirect(url_for('worker_menupage'))

@app.route('/menupage/worker/addmenu', methods=['POST', 'GET'])
def addmenu():
    form = Menus(request.form)
    form.main_course.choices = [(main_course.id, main_course.name) for main_course in MainCourse.query.all()]
    form.beverage.choices = [(beverage.id, beverage.name) for beverage in Beverage.query.all()]
    if request.method == 'POST':
        name = form.name.data
        price = form.price.data
        type = form.type.data
        desc = form.desc.data
        main_course_id=form.main_course.data
        beverage_id=form.beverage.data
        image_file=form.picture.data 
        addmenu = Menu(name=name, price=price, type=type, desc=desc, image_file=image_file,main_course_id=main_course_id,beverage_id=beverage_id)
        with app.app_context():
            db.session.add(addmenu)
            db.session.commit()
        flash(f'The menu {name} has been added to your database', 'success')
        return redirect(url_for('worker_menupage'))
    return render_template('worker/managemenu.html',form=form)

@app.route('/dashboard/worker/updatemenu/<int:id>',methods=['GET','POST'])
def updatemenu(id):
    menu =Menu.query.get_or_404(id)
    form = Menus(request.form)
    form.main_course.choices = [(main_course.id, main_course.name) for main_course in MainCourse.query.all()]
    form.beverage.choices = [(beverage.id, beverage.name) for beverage in Beverage.query.all()]
    if request.method == 'POST':
        menu.name = form.name.data
        menu.price = form.price.data
        menu.type = form.type.data
        menu.desc = form.desc.data
        #menu.image_file = form.picture.data
        menu.main_course_id=form.main_course.data
        menu.beverage_id=form.beverage.data
        db.session.commit()
        flash(f'You menu {menu.name} has been updated','success')
        return redirect(url_for('worker_menupage'))
    form.name.data=menu.name
    form.price.data=menu.price
    form.type.data=menu.type
    form.desc.data=menu.desc
    #form.picture.data=menu.image_file
    form.main_course.data=menu.main_course_id
    form.beverage.data=menu.beverage_id
    return render_template('worker/managemenu.html',form=form,menu=menu)

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

    