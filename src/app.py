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
from models import db, User, People, Planets, FavoritePeople, FavoritePlanets
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

@app.route('/users', methods=['GET'])
def get_users():
    all_users = User.query.all()
    results = list(map(lambda user: user.serialize(), all_users))

    return jsonify(results), 200

@app.route('/people', methods=['GET'])
def get_people():
    results = list(map(lambda user: user.serialize(), People.query.all()))

    return jsonify(results), 200

@app.route('/people/<int:people_id>', methods=['GET'])
def get_character(people_id):
    results = People.query.filter_by(id=people_id).first()

    return jsonify(results.serialize()), 200

@app.route('/people', methods=['POST'])
def post_character():
    body = request.get_json()
    character = People(name=body['name'], birth_year=body['birth_year'], gender=body['gender'], height=body['height'], skin_color=body['skin_color'], eye_color=body['eye_color'])
    db.session.add(character)
    db.session.commit()
    response_body = {
        'msg': 'Character has been created.'
    }

    return jsonify(response_body), 200

@app.route('/planets', methods=['GET'])
def get_planets():
    results = list(map(lambda user: user.serialize(), Planets.query.all()))
    
    return jsonify(results), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    results = Planets.query.filter_by(id=planet_id).first()
    
    return jsonify(results.serialize()), 200

@app.route('/users/favorites', methods=['GET'])
def get_favorites():
    favorite_people = FavoritePeople.query.all()
    people = list(map(lambda people: people.serialize(), favorite_people))
    favorite_planets = FavoritePlanets.query.all()
    planets = list(map(lambda planets: planets.serialize(), favorite_planets))

    return jsonify(people, planets), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
