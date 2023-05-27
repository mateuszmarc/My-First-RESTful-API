import random

from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False
db = SQLAlchemy(app)

api_key = '1234567'


# Cafe TABLE Configuration
def not_found():
    return {
        "Not Found": "Sorry, we don't have a cafe at that location."
    }


def added_successfully():
    return {
        "success": "Successfully added the new cafe"
    }


def failed_patch():
    return {
        "Failed": "Sorry we don't have cafe with passed id."
    }


def delete_success():
    return {
        "Success": "Cafe deleted successfully."
    }


def wrong_api():
    return {
        "Error": "Wrong Api key provided."
    }


class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name)
                for column in self.__table__.columns}


@app.route("/")
def home():
    return render_template("index.html")


@app.route('/random')
def get_random_cafe():
    all_cafes = db.session.query(Cafe).all()
    random_cafe = random.choice(all_cafes)
    cafe_dict = random_cafe.to_dict()
    return jsonify(cafe_dict)


@app.route('/all')
def show_all():
    all_cafes = db.session.query(Cafe).all()
    dict_cafes = [cafe.to_dict() for cafe in all_cafes]
    return jsonify(cafes=dict_cafes)


@app.route('/search')
def search_by_location():
    location = request.args.get('loc')
    cafes_for_location = db.session. \
        execute(db.select(Cafe).filter_by(location=location.title())).all()
    print(cafes_for_location)
    if cafes_for_location:
        return jsonify(cafes=[cafe[0].to_dict() for cafe in cafes_for_location])
    else:
        return jsonify(error=not_found())


@app.route('/add', methods=['POST'])
def add():
    if request.method == 'POST':
        new_cafe = Cafe(name=request.form.get('name'),
                        map_url=request.form.get('map_url'),
                        img_url=request.form.get('image_url', ),
                        location=request.form.get('location'),
                        seats=request.form.get('seats'),
                        has_toilet=int(request.form.get('has_toilet')),
                        has_wifi=int(request.form.get('has_wifi')),
                        has_sockets=int(request.form.get('has_sockets')),
                        can_take_calls=int(request.form.get('can_take_calls')),
                        coffee_price=request.form.get('coffee_price'))
        db.session.add(new_cafe)
        db.session.commit()
        return jsonify(result=added_successfully())


@app.route('/update-price/<int:cafe_id>', methods=['GET', 'PATCH'])
def update_price(cafe_id):
    if request.method == 'PATCH':
        cafe_ids = [cafe.id for cafe in db.session.query(Cafe).all()]
        if cafe_id in cafe_ids:
            cafe_to_update = Cafe.query.get(cafe_id)
            new_price = request.args.get('new_price')
            cafe_to_update.coffee_price = new_price
            db.session.commit()
            return jsonify(result=added_successfully())
        else:
            return jsonify(result=failed_patch())


@app.route('/report-closed/<cafe_id>', methods=['DELETE', 'GET'])
def delete_cafe(cafe_id):
    if request.method == 'DELETE':
        all_cafes_ids = [int(cafe.id) for cafe in db.session.query(Cafe).all()]
        if int(cafe_id) in all_cafes_ids:
            if api_key == request.args.get('Api_key'):
                cafe_to_close = Cafe.query.get(cafe_id)
                db.session.delete(cafe_to_close)
                db.session.commit()
                return jsonify(result=delete_success())
            else:
                return jsonify(error=wrong_api())

        else:
            return jsonify(result=failed_patch())


if __name__ == '__main__':
    app.run(debug=True)
