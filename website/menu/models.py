from website import db,app

class MainCourse(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    quantity = db.Column(db.Integer,nullable=False)
    remarks=db.Column(db.Text, nullable=False)

def __repr__(self):
    return f"Main Course('{self.name},'{self.quantity}','{self.remarks}')"

class Beverage(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    quantity = db.Column(db.Integer,nullable=False)
    remarks=db.Column(db.Text, nullable=False)

def __repr__(self):
    return f"Beverage('{self.name},'{self.quantity}','{self.remarks}')"

class Menu(db.Model):
    __searchable__ = ['name', 'desc']
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    type = db.Column(db.Text, nullable=False)
    desc = db.Column(db.Text, nullable=False)
    image_file = db.Column(db.String(30), nullable=False, default='default_menu.jpg')

    main_course_id = db.Column(db.Integer, db.ForeignKey('main_course.id'), nullable=False)
    main_course = db.relationship('MainCourse', backref='menu') 

    beverage_id = db.Column(db.Integer, db.ForeignKey('beverage.id'), nullable=False)
    beverage = db.relationship('Beverage', backref='menu')

    def __repr__(self):
        return f"Menu('{self.name},'{self.price}','{self.type}','{self.desc}')"

with app.app_context():
    db.create_all()