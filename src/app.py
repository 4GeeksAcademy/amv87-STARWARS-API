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

@app.route('/users/<int:user_id>/favorites', methods=['GET'])
def get_user_favorites(user_id):
    user = User.query.filter_by(id=user_id).first()
    response_body = {
        "favorite_characters": [item.serialize() for item in user.favorite_people],
        "favorite_planets": [item.serialize() for item in user.favorite_planets]
    }

    return jsonify(response_body), 200

@app.route('/people', methods=['GET'])
def get_people():
    results = list(map(lambda user: user.serialize(), People.query.all()))

    return jsonify(results), 200

@app.route('/people/<int:people_id>', methods=['GET'])
def get_character(people_id):
    results = People.query.filter_by(id=people_id).first()

    return jsonify(results.serialize()), 200

@app.route('/planets', methods=['GET'])
def get_planets():
    results = list(map(lambda user: user.serialize(), Planets.query.all()))
    
    return jsonify(results), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    results = Planets.query.filter_by(id=planet_id).first()
    
    return jsonify(results.serialize()), 200

@app.route('/users/<int:user_id>/favorites/people/<int:people_id>', methods=['POST'])
def add_favorite_character(user_id, people_id):
    user = User.query.filter_by(id=user_id).first()
    character = People.query.filter_by(id=people_id).first()
    new_favorite = FavoritePeople(user=user, character=character)
    db.session.add(new_favorite)
    db.session.commit()
    response_body = {
        'msg': 'Favorite character has been added.'
    }

    return jsonify(response_body), 201

@app.route('/users/<int:user_id>/favorites/planets/<int:planet_id>', methods=['POST'])
def add_favorite_planet(user_id, planet_id):
    user = User.query.filter_by(id=user_id).first()
    planet = Planets.query.filter_by(id=planet_id).first()
    new_favorite = FavoritePlanets(user=user, planet=planet)
    db.session.add(new_favorite)
    db.session.commit()
    response_body = {
        'msg': 'Favorite planet has been added.'
    }

    return jsonify(response_body), 201

@app.route('/users/<int:user_id>/favorites/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_character(user_id, people_id):
    delete_favorite = FavoritePeople.query.filter_by(user_id=user_id, character_id=people_id).first()
    db.session.delete(delete_favorite)
    db.session.commit()
    response_body = {
        'msg': 'Favorite character has been deleted.'
    }

    return jsonify(response_body), 200

@app.route('/users/<int:user_id>/favorites/planets/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(user_id, planet_id):
    delete_favorite = FavoritePlanets.query.filter_by(user_id=user_id, planet_id=planet_id).first()
    db.session.delete(delete_favorite)
    db.session.commit()
    response_body = {
        'msg': 'Favorite planet has been deleted.'
    }

    return jsonify(response_body), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
