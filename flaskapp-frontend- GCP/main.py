from flask import Blueprint, render_template, url_for,request, redirect, flash, abort
from . import db
from flask_login import login_required, current_user
from .models import User
from .models import Restaurante
from werkzeug.utils import redirect, secure_filename
#import form
import os

from .auth import token_required
#MODIFICACIONES PARA EL CLOUD STORAGE BUCKET
from google.cloud import storage
import google.cloud.storage
import json
import sys

PATH = os.path.join(os.getcwd() , '/home/mauriciocd12/credenciales.json')
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = PATH
storage_client = storage.Client(PATH)

main = Blueprint('main', __name__)



@main.route('/')
def index():
    return render_template("index.html")



@main.route('/profile')
@login_required
def profile():
	restaurantes = Restaurante.query.filter_by(user_id = current_user.id).order_by(Restaurante.fecha.desc()).all()
	band = True if len(restaurantes) == 0 else  False
	return render_template("profile.html", name = current_user.name, band = band, restaurantes = restaurantes)


@main.route('/nuevo_rest')
@login_required
def nuevo_restaurante():
    return render_template("agregar_restaurante.html")


@main.route('/nuevo_rest', methods=['POST'])
@login_required
def nuevo_restaurante_post():
    nombre = request.form["nombre"]
    categoria = request.form["categoria"]
    lugar = request.form["lugar"]
    direccion = request.form["direccion"]
    telefono = request.form["telefono"]
    domicilio = False if request.form['options'] == "no" else True

    # obtenemos el archivo del input "archivo"
    f = request.files['logo']
    f2 = request.files['menu']
    filename = secure_filename(f.filename)
    filename2 = secure_filename(f2.filename)
    # Guardamos el archivo en el directorio "Archivos PDF"
    f.save(os.path.join("/home/mauriciocd12/flaskapp/static", filename))
    f2.save(os.path.join("/home/mauriciocd12/flaskapp/static", filename2))
    # Retornamos una respuesta satisfactoria
    logo_url = filename
    menu_url = filename2
    print(filename,filename2,os.getcwd())
    #guardamos tambien en cloud stora para probar
    UPLOADFILE = os.path.join("/home/mauriciocd12/flaskapp/static", filename)
    UPLOADFILE1 = os.path.join("/home/mauriciocd12/flaskapp/static", filename2)
    bucket = storage_client.get_bucket('storagerestauranteapp')
    blob = bucket.blob(filename)
    blob.upload_from_filename(UPLOADFILE)
    blob = bucket.blob(filename2)
    blob.upload_from_filename(UPLOADFILE1)

    restaurante = Restaurante(nombre = nombre, categoria = categoria, lugar = lugar, direccion = direccion, telefono = telefono,
        domicilio = domicilio, user_id = current_user.id,logo_url = logo_url, menu_url = menu_url)
    db.session.add(restaurante)
    db.session.commit()

    flash('Your restaurant has been added!')

    #return redirect(url_for('main.user_restaurantes'))
    return redirect(url_for("main.profile"))


@main.route("/detalles/<int:rest_id>/", methods=['GET'])
@login_required
def detalles(rest_id):
    restaurante = Restaurante.query.filter_by(id = rest_id).first()
    return render_template("detalle.html", restaurante = restaurante)





@main.route("/editar/<int:rest_id>/update", methods=['GET'])
@login_required
def editar_restaurante(rest_id):
    restaurante = Restaurante.query.filter_by(id = rest_id).first()
    return render_template("editar.html", restaurante = restaurante)





@main.route('/all_rest')
@login_required
#@token_required
def user_restaurantes():
    #user = User.query.filter_by(email=current_user.email).first_or_404()
    restaurantes = Restaurante.query.filter_by(user_id= current_user.id).order_by(Restaurante.fecha.desc()).all()
    #restaurantes = user.restaurantes
    #restaurantes = restaurantes.query.order_by(re)
    ans=""
    for ret in restaurantes:
    	ans+= ret.nombre+" "+ret.categoria+" "+ret.lugar+" "+ret.direccion+""+str(ret.telefono)+" "+ret.menu+" "+ret.domicilio+'\n'
    return "Saludos {}\nEstos son los restaurantes que tienes registrados: {}".format(current_user.name,ans)



@main.route("/editar/<int:rest_id>/update", methods=['POST'])
@login_required
def editar_restaurante_post(rest_id):
    restaurante = Restaurante.query.filter_by(id = rest_id).first()


    restaurante.nombre = request.form["nombre"]
    restaurante.categoria = request.form["categoria"] 
    restaurante.lugar = request.form["lugar"]
    restaurante.direccion = request.form["direccion"]
    restaurante.telefono = request.form["telefono"]
    restaurante.domicilio = False if request.form['options'] == "no" else True


    # obtenemos el archivo del input "archivo"
    f = request.files['logo']
    f2 = request.files['menu']
    filename = secure_filename(f.filename)
    filename2 = secure_filename(f2.filename)
    # Guardamos el archivo en el directorio "Archivos PDF"
    if len(filename):
        f.save(os.path.join("/home/mauriciocd12/flaskapp/static", filename))
        restaurante.logo_url = filename
    if len(filename2):
        f2.save(os.path.join("/home/mauriciocd12/flaskapp/static", filename2))
        restaurante.menu_url = filename2

    db.session.commit()

    return redirect(url_for("main.profile"))


@main.route("/eliminar/<int:rest_id>/update", methods=['GET'])
@login_required
def eliminar_restaurante(rest_id):
    bucket = storage_client.get_bucket('storagerestauranteapp')
    restaurante = Restaurante.query.filter_by(id = rest_id).first()
    blob = bucket.blob(restaurante.logo_url)
    blob.delete()
    blob = bucket.blob(restaurante.menu_url)
    blob.delete()


    db.session.delete(restaurante)
    db.session.commit()
    
    return redirect(url_for("main.profile"))
