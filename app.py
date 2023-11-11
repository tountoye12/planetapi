import os.path

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, Float, String
import os
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager, jwt_required, create_access_token

app = Flask(__name__)

baseDir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(baseDir, "planetapi.db")
app.config["JWT_SECRET_KEY"] = "secret-key"

db = SQLAlchemy(app)
ma = Marshmallow(app)
jwt = JWTManager(app)


@app.cli.command("db_create")
def db_create():
    db.create_all()
    print("Db creation is done!!")


@app.cli.command("db_drop")
def db_drop():
    db.drop_all()
    print("All data droped")


@app.cli.command("db_seed")
def db_seed():
    mercury = Planet(planet_name="Mercury",
                     planet_type="Class A",
                     home_star="Sol",
                     mass=1000.3553,
                     radius=1615,
                     distance=35.38373
                     )
    venus = Planet(planet_name="Venus",
                   planet_type="Class B",
                   home_star="Sol",
                   mass=1000.3553,
                   radius=1615,
                   distance=35.38373
                   )
    db.session.add(mercury)
    db.session.add(venus)

    user = User(first_name="Diallo", last_name="Drame",
                email="diallo@miu.edu", password="diallo10@")
    db.session.add(user)
    db.session.commit()
    print("data Seeded")


@app.route('/')
def hello():
    return "Hello"


@app.route("/super_simple")
def super_simple():
    return jsonify(message="supper", name="Diallo")


@app.route("/parameters")
def parameters():
    name = request.args.get('name')
    age = int(request.args.get('age'))
    print(name)
    print(age)
    if age < 10:
        return jsonify(message="Sorry " + name + " , you're not old enough")
    else:
        return jsonify(message="Welcome " + name + ", thank you for coming")


@app.route("/url_variables/<string:name>/<int:age>")
def url_variables(name: str, age: int):
    if age < 10:
        return jsonify(message="Sorry " + name + " , you're not old enough"), 401
    else:
        return jsonify(message="Welcome " + name + ", thank you for coming")


@app.route("/planets", methods=["GET"])
def planets():
    planets_list = Planet.query.all()
    return jsonify(data=planets_schema.dump(planets_list))


@app.route("/users", methods=["GET"])
def users():
    user_list = User.query.all()
    return jsonify(data=users_schema.dump(user_list))


@app.route("/register", methods=["POST"])
def register():
    email = request.form["email"]
    if User.query.filter_by(email=email).first():
        return jsonify(message="User with this email is already exist")
    else:
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        password = request.form["password"]
        user = User(first_name=first_name, last_name=last_name, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        return jsonify(message="User created successfully")


@app.route("/login", methods=["POST"])
def login():
    if request.is_json:
        email = request.json["email"]
        password = request.json["password"]
    else:
        email = request.form["email"]
        password = request.form["password"]
    test = User.query.filter_by(email=email, password=password).first()
    if test:
        access_token = create_access_token(identity=email)
        return jsonify(message="successfully logged in", access_token=access_token)
    else:
        return jsonify(message="Bad email or Password")


@app.route("/planet_details/<int:planet_id>", methods=["GET"])
def planet_details(planet_id: int):
    planet = Planet.query.filter_by(planet_id=planet_id).first()
    if planet:
        result = planet_schema.dump(planet)
        return jsonify(result)
    else:
        return jsonify(message="Planet with " + str(planet) + " not exist")


@app.route("/add_planet", methods=["POST"])
def add_planet():
    if request.is_json:
        planet_name = request.json["planet_name"]
        planet_type = request.json["planet_type"]
        home_star = request.json["home_star"]
        mass = request.json["mass"]
        radius = request.json["radius"]
        distance = request.json["distance"]

        planet = Planet(planet_name=planet_name, planet_type=planet_type,
                        home_star=home_star, mass=mass, radius=radius,
                        distance=distance)
        db.session.add(planet)
        db.session.commit()
        return jsonify(message="Planet created successfully")
    else:
        planet_name = request.form["planet_name"]
        planet_type = request.form["planet_type"]
        home_star = request.form["home_star"]
        mass = request.form["mass"]
        radius = request.form["radius"]
        distance = request.form["distance"]

        planet = Planet(planet_name=planet_name, planet_type=planet_type,
                        home_star=home_star, mass=mass, radius=radius,
                        distance=distance)
        db.session.add(planet)
        db.session.commit()
        return jsonify(message="Planet created successfully")


@app.route("/delete_planet/<int:planet_id>", methods=["DELETE"])
def delete_planet(planet_id: int):
    planet = Planet.query.filter_by(planet_id=planet_id).first()
    if not planet:
        return jsonify(message="No planet with this id")
    else:
        db.session.delete(planet)
        db.session.commit()
        return jsonify(message="PLanet deleted successfully")


# database models
class User(db.Model):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)


class Planet(db.Model):
    __tablename__ = "planet"
    planet_id = Column(Integer, primary_key=True)
    planet_name = Column(String)
    planet_type = Column(String)
    home_star = Column(String)
    mass = Column(Float)
    radius = Column(Float)
    distance = Column(Float)


class PlanetSchema(ma.Schema):
    class Meta:
        fields = ("planet_id", "planet_name", "planet_type", "home_star",
                  "mass", "radius", "distance")


class UserSchema(ma.Schema):
    class Meta:
        fields = ("id", "first_name", "last_name", "email", "password")


user_schema = UserSchema()
users_schema = UserSchema(many=True)

planet_schema = PlanetSchema()
planets_schema = PlanetSchema(many=True)

if __name__ == "__main__":
    app.run(debug=True)
