from . import db
from flask_login import UserMixin


class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String(64), unique=True, nullable=False)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(64), nullable=False)
    recipes = db.relationship('Recipe')


class Recipe(db.Model):
    __tablename__ ='recipe'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.String(1024), unique=True, nullable=False)
    path = db.Column(db.String(256), nullable=True, unique=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))