
from . import db
from flask_login import UserMixin
from datetime import datetime

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))
    restaurantes = db.relationship('Restaurante', backref='author', lazy=True)



class Restaurante(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100),nullable=False)
    categoria = db.Column(db.String(100),nullable=False)
    lugar = db.Column(db.String(100),nullable=False)
    direccion = db.Column(db.String(100),nullable=False)

    telefono = db.Column(db.String(20), nullable=False)
    domicilio = db.Column(db.String(100),nullable=False)
    fecha = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    logo_url = db.Column(db.String(100), nullable = True)
    menu_url = db.Column(db.String(100), nullable = True)