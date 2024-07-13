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
from models import db, User, Post
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

# POST
# CRUD - CREATE READ[1/3] UPDATE DELETE

@app.route("/posts", methods=["GET"])
def get_posts():
    posts = Post.query.all()
    serialize_posts = [post.serialize() for post in posts]
    return jsonify({"posts": serialize_posts}), 200

@app.route("/posts/user/<int:id>", methods=["GET"])
def get_posts_from_user(id):
    user = User.query.get(id)
    if user is None:
        return jsonify({"error": "user not found"}), 404
    posts = Post.query.filter_by(user_id=id).all()
    serialize_posts = [post.serialize() for post in posts]
    return jsonify({"posts": serialize_posts}), 200

# POST/crear
@app.route("/post", methods=["POST"])
def create_post():
    body = request.json
    content = body.get("content", None) # {"content": "value"}
    user_id = body.get("user_id", None) #

    if user_id is None:
        return jsonify({"error": "user_id is required"}), 400
    user = User.query.get(user_id)
    if user is None:
        return jsonify({"error": "user not found"}), 404
    if content is None:
        return jsonify({"error": "content is required"}), 400

    new_post = Post(user_id=user_id, content=content)
    # despues la agrego a la session y despues guardo la sesion
    try:
        # 
        db.session.add(new_post)
        db.session.commit() # en esta linea
        db.session.refresh(new_post)
        return jsonify({"post": new_post.serialize()}), 201
    
    except Exception as error:
        db.session.rollback() #<3
        return jsonify({"error": f"{error}"}), 500

@app.route("/post/<int:id>", methods=["PUT"])
def update_post(id):
    body = request.json

    post = Post.query.get(id)
    if post is None:
        return jsonify({"error": "Post not found"}), 404

    content = body.get("content", None)
    if content is None:
        return jsonify({"error": "Content is required"}), 400

    post.content = content

    try:
        db.session.commit()
        db.session.refresh(post)
        return jsonify({"post": post.serialize()}), 200
    
    except Exception as error:
        db.session.rollback()
        return jsonify({"error": f"{error}"}), 500

@app.route("/post/<int:id>", methods=["DELETE"])
def delete_post(id):
    post = Post.query.get(id)
    # validar si ese post si quiera existe
    if post is None:
        return jsonify({"error": "Post not found"}), 404
    try:
        db.session.delete(post)
        db.session.commit()
        return jsonify({"msg": "Post deleted successfully"}), 200
    except Exception as error:
        return jsonify({"error": f"{error}"}), 500
# Si, blueprints

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
