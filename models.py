from peewee import *
from flask_login import UserMixin, login_user
from flask_bcrypt import generate_password_hash
from hashlib import md5
import os
from datetime import *

DATABASE_proxy = Proxy()

DATABASE = SqliteDatabase('todo.db')
DATABASE_proxy.initialize(DATABASE)


class Users(UserMixin, Model):
    username = CharField(unique=True, max_length=20)
    email = CharField(unique=True)
    password = CharField(max_length=100)

    class Meta:
        database = DATABASE_proxy

    @classmethod
    def create_user(cls, username, email, password):
        try:
            with DATABASE.transaction():
                user = cls.create(
                    username=username,
                    email=email,
                    password=generate_password_hash(password)
                )
        except IntegrityError:
            raise ValueError("User already exists")
        else:
            login_user(user)


class Projects(Model):
    name = CharField(max_length=50)
    active = BooleanField()

    class Meta:
        database = DATABASE_proxy


class Tasks(Model):
    project_id = ForeignKeyField(Projects, related_name='task_to_project')
    task = TextField()
    status = BooleanField()
    timestamp = DateTimeField(default=datetime.now)
    role = ForeignKeyField(Users, related_name='user_role', default=1)

    class Meta:
        database = DATABASE_proxy


def initialize():
    DATABASE_proxy.connection()
    DATABASE_proxy.create_tables([Users, Projects, Tasks], safe=True)
    DATABASE_proxy.close()
