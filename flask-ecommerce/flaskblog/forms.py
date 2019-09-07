from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, DecimalField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange, Regexp
from flaskblog.models import User


class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(),
                    Regexp('^.{6,15}$', message='Your password should be between 6 and 20 characters long.')])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(),
                Regexp('^.{6,15}$', message='Your password should be between 6 and 20 characters long.')])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    picture = FileField('Add Photo', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Post')


class BookForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=300)])
    isbn = StringField('ISBN', validators=[DataRequired(), Length(min=6, max=20)])
    year = StringField('Publication Year', validators=[DataRequired(), Length(4)])
    author = StringField('Author(s)', validators=[DataRequired(), Length(max=300)])
    subject = StringField('Subject', validators=[DataRequired()])
    book_image = FileField('Add Photo', validators=[FileAllowed(['jpg', 'png'])])
    price = DecimalField('Price', validators=[DataRequired()])
    comment = TextAreaField('Add Comment', validators=[Length(max=300)])

    # picture = FileField('Add Photo', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Post')


class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(),
                Regexp('^.{6,15}$', message='Your password should be between 6 and 20 characters long.')])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')



class OrderForm(FlaskForm):
    billing_address = StringField('Billing Address', validators=[DataRequired(), Length(max=400)])
    billing_postcode = StringField('Postcode', validators=[DataRequired(), Length(min=4, max=12)])
    delivery_address = StringField('Delivery Address', validators=[DataRequired(), Length(max=400)])
    delivery_postcode = StringField('Postcode', validators=[DataRequired(), Length(min=4, max=12)])
    card_number = IntegerField('Card Number', validators=[DataRequired()])
    cvv = IntegerField('CVV', validators=[DataRequired()])
    exp_month = IntegerField('Expiry Month', validators=[DataRequired()])
    exp_year = IntegerField('Expiry Year', validators=[DataRequired()])
    submit = SubmitField('Place Order')






