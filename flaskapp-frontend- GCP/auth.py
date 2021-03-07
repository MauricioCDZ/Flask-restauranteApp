from flask import Blueprint, render_template, url_for, request, redirect,jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from .models import User
from . import db

import jwt
import datetime
from functools import wraps


auth = Blueprint('auth', __name__)


@auth.route('/signup')
def signup():
    return render_template("registro.html")


@auth.route('/signup', methods=['POST'])
def signup_post():
    name = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("password")

    user = User.query.filter_by(email=email).first()

    if user:
        return render_template("registro.html", band = True)

    new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'))
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for("auth.login"))


@auth.route('/login')
def login():
    return render_template("login.html")


@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get("email")
    password = request.form.get("password")
    remember = True if request.form.get("remember") else False
    
    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        return redirect('auth.login')
    else:

        login_user(user)
        token = jwt.encode({'user': user.name,'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes = 30)}, "secret_key")
        #return redirect(url_for('main.profile'))
        return redirect(url_for("main.profile"))


# JWT FUNCTIONS

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token')

        if not token:
            return "Falta el token!!, ingresalo despues de la ruta; ruta?token = xxxxx", 403
        
        try:
            data = jwt.decode(token, "secret_key")
            

        except:
            return "Token no válido!!",403

        return f(*args, **kwargs) 
    return decorated

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.index"))  

