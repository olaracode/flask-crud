"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

# User: Nuestro modelo/table
# query: Buscar/filtrar/encontrar
# all: todos
# User.query.all()
@app.route('/users', methods=['GET', 'POST'])
def handle_hello():
    users = User.query.all()
    serialize_users = [user.serialize() for user in users]
    return jsonify({
        "users": serialize_users
    }), 200
# CREATE / READ / UPDATE / DELETE
#  POST / GET 2(2) / PATCH o PUT / DELETE
@app.route('/user/<int:id>', methods=["GET"])
def get_user(id):
    # User.query.get(id) -> Busca un usuario por el id
    user = User.query.get(id)
    if user is None:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify({
        "user": user.serialize()
    }), 200

@app.route("/user", methods=["POST"])
def add_user():
    body = request.json
    email = body.get("email", None)
    password = body.get("password", None)
    

    if email is None:
        # utf-8
        # {"llave": "valor", "nombre": "Gustavo", "apellido": "patinio"}
        return jsonify({"error": "El email es requerido"}), 400
    if password is None:
        return jsonify({"error": "El password es requerido"}), 400
    
    # Creamos una nueva instancia de nuestro modal
    new_user = User(email=email, password=password, is_active=True)
    # db
    try:
        db.session.add(new_user)
        db.session.commit()
        # Obtiene los datos unicos de la BBDD(Como ID)
        db.session.refresh(new_user)
        return jsonify({"usuario": new_user.serialize()}), 201
    except Exception as error:
        db.session.rollback() # Es que revierte los cambios que no
        # se hayan guardado

        return jsonify({"error": f"{error}"}), 500
    
@app.route("/user/<int:id>", methods=["PUT"])
def update_user(id):
    # Ver si ese usuario existe
    body = request.json
    user = User.query.get(id)
    if user is None:
        return jsonify({"error", "Usuario no encontrado"}), 404
    
    email = body.get("email", None)
    if email is None:
        return jsonify({"error": "El email es requerido"}), 400

    user.email = email
    try:
        db.session.commit()
        return jsonify({"user": user.serialize()}), 200
    except Exception as error:
        db.session.rollback()
        return jsonify({"error": f"Internal server error: {error}"}), 500
    
@app.route("/user/<int:id>", methods=["DELETE"])
def delete_user(id):
    user = User.query.get(id)
    if user is None:
        return jsonify({"error": "User not found"}), 404
    try:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"msg": "Usuario borrado"}), 200
    except Exception as error:
        db.session.rollback()
        return jsonify({"error": f"internal server error: {error}"}),500

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
