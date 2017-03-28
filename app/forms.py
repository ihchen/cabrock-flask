from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField
from wtforms.validators import Email, Optional, InputRequired

class ContactForm(FlaskForm):
    name = StringField('Your Name', [InputRequired('Please enter your name')])
    email = StringField('Your Email Address', [InputRequired('Please enter your email'), Email('The email address you entered was invalid')])
    subject = StringField('Email Subject', [Optional(True)])
    message = TextAreaField('Message', [InputRequired('Please enter a message')])

class LoginForm(FlaskForm):
    username = StringField('Username')
    password = PasswordField('Password')
