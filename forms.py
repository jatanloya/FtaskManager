from flask_wtf import Form
from wtforms.validators import DataRequired, EqualTo, Length, Email
from wtforms import StringField, PasswordField
from models import Users


def isUsernameUnique(form, field):
    if Users.select().where(Users.username == field.data).exists():
        raise ValueError("User already exists")


class RegisterForm(Form):
    username = StringField(
        'Username',
        validators=[
            DataRequired(),
            isUsernameUnique
        ]
    )
    email = StringField(
        'Email',
        validators=[
            DataRequired()
        ]
    )
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            Length(min=6),
            EqualTo('confirmPassword', message='Passwords do not match')
        ]
    )
    confirmPassword = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired(),
            Length(min=6)
        ]
    )


class LoginForm(Form):
    username = StringField(
        'Username',
        validators=[
            DataRequired()
        ]
    )
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            Length(min=6)
        ]
    )
