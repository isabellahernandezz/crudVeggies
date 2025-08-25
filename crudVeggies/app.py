# app.py
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)

# Configuración de la base de datos
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///instance/app.db")
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "changeme")

db = SQLAlchemy(app)

# Modelo Vegetable
class Vegetable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True)
    color = db.Column(db.String(50))
    price = db.Column(db.Float)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "color": self.color, "price": 
self.price}

# Crear tablas automáticamente
with app.app_context():
    db.create_all()

# Rutas CRUD

# Listar todos los vegetales
@app.route("/api/veggies", methods=["GET"])
def get_veggies():
    veggies = Vegetable.query.all()
    return jsonify([v.to_dict() for v in veggies]), 200

# Obtener vegetal por ID
@app.route("/api/veggies/<int:id>", methods=["GET"])
def get_veggie(id):
    v = Vegetable.query.get(id)
    if not v:
        return jsonify({"error": "Vegetal no encontrado"}), 404
    return jsonify(v.to_dict()), 200

# Crear vegetal
@app.route("/api/veggies", methods=["POST"])
def create_veggie():
    data = request.get_json()
    if not data or not data.get("name"):
        return jsonify({"error": "El nombre es obligatorio"}), 400
    v = Vegetable(name=data["name"], color=data.get("color"), 
price=data.get("price"))
    try:
        db.session.add(v)
        db.session.commit()
        return jsonify(v.to_dict()), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Vegetal ya existe"}), 409

# Actualizar vegetal
@app.route("/api/veggies/<int:id>", methods=["PUT"])
def update_veggie(id):
    v = Vegetable.query.get(id)
    if not v:
        return jsonify({"error": "Vegetal no encontrado"}), 404
    data = request.get_json()
    if "name" in data:
        v.name = data["name"]
    if "color" in data:
        v.color = data["color"]
    if "price" in data:
        v.price = data["price"]
    try:
        db.session.commit()
        return jsonify(v.to_dict()), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Nombre de vegetal ya existe"}), 409

# Eliminar vegetal
@app.route("/api/veggies/<int:id>", methods=["DELETE"])
def delete_veggie(id):
    v = Vegetable.query.get(id)
    if not v:
        return jsonify({"error": "Vegetal no encontrado"}), 404
    db.session.delete(v)
    db.session.commit()
    return jsonify({"message": "Vegetal eliminado"}), 200

# Ejecutar app
if __name__ == "__main__":
    app.run(debug=True)


