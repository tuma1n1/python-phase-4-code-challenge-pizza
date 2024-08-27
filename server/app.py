#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from sqlalchemy.orm import sessionmaker, Session
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

#Session = sessionmaker(bind=db.engine)
#session = Session()
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db.engine)

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

SessionLocal = None

@app.before_first_request
def create_session():
    global SessionLocal
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db.engine)


@app.route("/", methods=['GET'])
def index():
    return "<h1>Code challenge</h1>"

@app.route("/restaurants", methods=['GET'])
def get_restaurants():
    session = SessionLocal()
    restaurants = session.query(Restaurant).all()
    # restaurants = Restaurant.query.all()
    return jsonify([r.to_dict() for r in restaurants])

@app.route("/restaurants/<int:id>", methods=['GET'])
def get_restaurant_by_id(id):
    session = SessionLocal()
    restaurant = session.get(Restaurant, id)
    # restaurant = Restaurant.query.get(id)
    if restaurant:
        return jsonify({
            'id': restaurant.id,
            'name': restaurant.name,
            'address': restaurant.address,
            'restaurant_pizzas': [
                {
                    'id': rp.id,
                    'price': rp.price,
                    'pizza_id': rp.pizza_id,
                    'restaurant_id': rp.restaurant_id
                }
                for rp in restaurant.restaurant_pizzas
            ]
        }), 200
    else:
        return jsonify({'error': 'Restaurant not found'}), 404
    
@app.route('/restaurants/<int:id>', methods=['DELETE'])
def delete_restaurant(id):
    # session = SessionLocal()
    session = db.session
    restaurant = session.get(Restaurant, id)
    # restaurant = Restaurant.query.get(id)
    if restaurant:
        session.delete(restaurant)
        session.commit()
        # db.session.delete(restaurant)
        # db.session.commit()
        return '', 204
    return jsonify({"error": "Restaurant not found"}), 404

@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    session = SessionLocal()
    pizzas = session.query(Pizza).all()
    # pizzas = Pizza.query.all()
    return jsonify([pizza.to_dict() for pizza in pizzas])

@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza():
    data = request.json
    price = data.get('price')
    pizza_id = data.get('pizza_id')
    restaurant_id = data.get('restaurant_id')

    if not (1 <= price <= 30):
        return jsonify({"errors": ["validation errors"]}), 400
    
    session = SessionLocal()
    restaurant_pizza = RestaurantPizza(price=price, pizza_id=pizza_id, restaurant_id=restaurant_id)
    session.add(restaurant_pizza)
    session.commit() 
    # db.session.add(restaurant_pizza)
    # db.session.commit()

    # pizza = Pizza.query.get(pizza_id)  # Fetch pizza details
    # restaurant = Restaurant.query.get(restaurant_id)
    pizza = session.get(Pizza, pizza_id)
    restaurant = session.get(Restaurant, restaurant_id)
    return jsonify({
        'id': restaurant_pizza.id,
        'price': restaurant_pizza.price,
        'pizza_id': restaurant_pizza.pizza_id,
        'restaurant_id': restaurant_pizza.restaurant_id,
        'pizza': pizza.to_dict() if pizza else None,  # Include pizza details in response
        'restaurant': restaurant.to_dict() if restaurant else None
    }), 201
    # return jsonify(restaurant_pizza.to_dict()), 201


if __name__ == "__main__":
    app.run(port=5555, debug=True)
