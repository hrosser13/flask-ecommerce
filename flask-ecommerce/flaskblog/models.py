from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flaskblog import db, login_manager, app
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.png')
    password = db.Column(db.String(60), nullable=False)
    books = db.relationship('Book', backref='poster', lazy=True)


    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"



class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subjectName = db.Column(db.String(100), nullable=False)
    book_ref = db.relationship('Book', backref='subjID', lazy=True)

    def __repr__(self):
        return f"Subject('{self.subjectName}'"


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    isbn = db.Column(db.String(20), nullable=False)
    year = db.Column(db.String, nullable=False)
    author = db.Column(db.String(100), nullable=False)
    userID = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    comment = db.Column(db.String(300), nullable=True)
    book_image = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f"Book('{self.title}', '{self.author}')"

class Order(db.Model):
    order_id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    billing_address = db.Column(db.String(250), nullable=False)
    billing_postcode = db.Column(db.String(10), nullable=False)
    delivery_address = db.Column(db.String(250), nullable=False)
    deliver_postcode = db.Column(db.String(10), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('purchased_book.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    price = db.Column(db.Float(4,2), nullable=False, default=00.00)
    # seller_id = db.Column(db.Integer, db.ForeignKey('book.userID', nullable=False))
   
    book_details = db.relationship('PurchasedBook', backref='book_deets', lazy=True)

    def __repr__(self):
        return f"Order('{self.order_id}', '{self.date}')"




class PurchasedBook(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    isbn = db.Column(db.String(20), nullable=False)
    year = db.Column(db.String, nullable=False)
    author = db.Column(db.String(100), nullable=False)
    seller = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    date_purchased = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    buyer = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # book_image = db.Column(db.String(20), nullable=False, default=None)

    # seller = db.relationship('User', backref='seller_deets', lazy=True)


    orders = db.relationship('Order', backref='purchased_order', lazy=True)


    def __repr__(self):
        return f"Book('{self.title}', '{self.author}')"

