import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort, session
from flaskblog import app, db, bcrypt, mail
from flaskblog.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                                RequestResetForm, ResetPasswordForm, BookForm, OrderForm)
from flaskblog.models import User, Book, Subject, Order, PurchasedBook
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message


@app.route("/")
@app.route("/home")
def home():
    page = request.args.get('page', 1, type=int)

    books = Book.query.order_by(Book.date_posted.desc()).limit(6).all()
    
    return render_template('home.html', books=books)


@app.route("/about")
def about():
    return render_template('about.html', title='About')

@app.route("/drop-it")
def drop_it():
    return render_template('drop_it.html', title='Drop-It!')


@app.route("/browse_all")
def browse_all():
    page = request.args.get('page', 1, type=int)
    # books = Book.query.order_by(Book.date_posted.desc())
    books = Book.query.order_by(Book.date_posted.desc()).paginate(page=page, per_page=6)
    return render_template('browse_all.html', title='Browse Books', books=books)

@app.route("/browse/<int:subject_id>")
def browse_by_subject(subject_id):
    books = Book.query.filter_by(subject_id=subject_id)\
        .order_by(Book.date_posted.desc())
    # for book in books:
    #     print(book.title)
    return render_template('browse.html', title='Browse Books', books=books)


@app.route("/user/<string:username>")
def user_books(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    books = Book.query.filter_by(poster=user)\
        .order_by(Book.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template('user_books.html', books=books, user=user)





@app.route("/user/<int:user_id>/orders")
def user_orders(user_id):
    user = User.query.filter_by(id=user_id).first_or_404()
    orders = Order.query.filter_by(user_id=current_user.id)\
        .order_by(Order.date.desc())
    return render_template('user_orders.html', orders=orders, user=user)


@app.route("/user/<int:user_id>/sold")
def user_sold(user_id):
    user = User.query.filter_by(id=user_id).first_or_404()
    sold_book = PurchasedBook.query.filter_by(seller=current_user.id)\
        .order_by(PurchasedBook.date_purchased.desc())

    return render_template('user_sold.html', sold_book=sold_book, user=user)





@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

def save_picture2(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/post_pics', picture_fn)

    output_size = (200, 300)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn





@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            print(form.picture.data)
            print("!!!!!!!!!!!HIIIIIIIII!!!!!!****")
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)






def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}
If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)






@app.route("/book/new", methods=['GET', 'POST'])
@login_required
def new_book():
    form = BookForm()
    if form.validate_on_submit():
        print(form.book_image.data)
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        picture_file = save_book_image(form.book_image.data)
        select = request.form.get('subject')
        subject_id = int(select)
        print(subject_id)

        book = Book(title=form.title.data, book_image=picture_file, isbn=form.isbn.data, year=form.year.data, author=form.author.data, subject_id=subject_id, poster=current_user, price=form.price.data, comment=form.comment.data)

        db.session.add(book)
        db.session.commit()
        flash('Your book has been created!', 'success')

        return redirect(url_for('home'))
    return render_template('create_book.html', title='New Book',
                           form=form, legend='New Book')


def save_book_image(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/post_pics', picture_fn)

    output_size = (200, 300)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/buy/<int:book_id>", methods=['GET', 'POST'])
@login_required
def buy(book_id):
    book = Book.query.get_or_404(book_id)
    form = OrderForm()
    if form.validate_on_submit():
        print("HERE!!!!!!!!")
        order = Order(billing_address=form.billing_address.data, billing_postcode=form.billing_postcode.data, delivery_address=form.delivery_address.data, deliver_postcode=form.delivery_postcode.data, book_id=book_id, user_id=current_user.id, price=book.price)
        purchased_book = PurchasedBook(id=book.id, title=book.title, isbn=book.isbn, year=book.year, author=book.author, seller=book.userID, price=book.price, buyer=current_user.id)

        db.session.add(order)
        db.session.add(purchased_book)
        db.session.delete(book)
        db.session.commit()

        return redirect(url_for('purchase_complete'))
    return render_template('buy.html', title='Order', form=form, legend='Order Form', book=book)

@app.route("/purchase_complete")
@login_required
def purchase_complete():
    return render_template('purchase_complete.html', title='Your Order')




@app.route("/book/<int:book_id>")
def book(book_id):
    book = Book.query.get_or_404(book_id)
    return render_template('book.html', title=book.title, book=book)


@app.route("/book/<int:book_id>/update", methods=['GET', 'POST'])
@login_required
def update_book(book_id):
    book = Book.query.get_or_404(book_id)
    if book.poster != current_user:
        abort(403)
    form = BookForm()
    if form.validate_on_submit():
        book.title = form.title.data
        book.isbn = form.isbn.data
        book.year = form.year.data
        book.author = form.author.data
        book.subject_id = form.subject.data
        book.price = form.price.data
        book.comment = form.comment.data
        # book.book_image = form.book_image.data
        db.session.commit()
        flash('Your book has been updated!', 'success')
        return redirect(url_for('book', book_id=book.id))
    elif request.method == 'GET':
        form.title.data = book.title
        form.isbn.data = book.isbn
        form.comment.data = book.comment
        form.year.data = book.year
        form.price.data = book.price
        form.subject.data = book.subjID
        form.author.data = book.author
        # form.book_image = book.book_image
    return render_template('create_book.html', title='Update Book',
                           form=form, legend='Update Book')


@app.route("/book/<int:book_id>/delete", methods=['POST'])
@login_required
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    if book.poster != current_user:
        abort(403)
    db.session.delete(book)
    db.session.commit()
    flash('Your book has been deleted!', 'success')
    return redirect(url_for('home'))





@app.route("/add_to_cart/<int:book_id>")
def add_to_cart(book_id):
    if "cart" not in session:
        session["cart"] = []
    if book_id not in session["cart"]:    
        session["cart"].append(book_id)
        flash("Book added to your saved items!", "success")
    else:
        flash("You have already added this book to your saved items!", "info")
    return redirect("/cart")

@app.route("/cart", methods=['GET', 'POST'])
def cart_display():
    if "cart" not in session:
        flash('There are no items in your cart.')
        return render_template("cart.html", display_cart={}, total=0)
    else:
        items = session["cart"]
        cart = {}

        total_price = 0
        total_quantity = 0
        for item in items:
            book = Book.query.get_or_404(item)
            total_price += book.price
            if book.id in cart:
                cart[book.id]["quantity"] += 1
            else:
                cart[book.id] = {"quantity":1, "title":book.title, "price":book.price, "bookID":book.id}

            total_quantity = sum(item["quantity"] for item in cart.values())

        return render_template("cart.html", title="Your Wishlist", display_cart=cart, total=total_price, total_quantity=total_quantity)
    return render_template("cart.html")

@app.route("/delete_saved_item/<int:book_id>", methods=["POST"])
def delete_saved_item(book_id):
    if "cart" not in session:
        session["cart"] = []
    session["cart"].remove(book_id)
    flash("The book has been removed from your saved items!")
    session.modified = True
    return redirect("/cart")
















