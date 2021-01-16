from flask import Flask, jsonify, render_template, request
from flask_admin import Admin
from flask_sqlalchemy import SQLAlchemy
from flask_admin.contrib.sqla import ModelView

app = Flask(__name__)

app.secret_key = "SECRET_TESTING"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.db'

# set optional bootswatch theme
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'


db = SQLAlchemy(app)


class Floor(db.Model):
    __tablename__ = 'floor'
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer)
    image_file = db.Column(db.String(256))
    info = db.Column(db.Text)

    def __repr__(self):
        return repr(id)


class Room(db.Model):
    __tablename__ = 'room'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    map_position_x = db.Column(db.Float)
    map_position_y = db.Column(db.Float)
    room_type = db.Column(db.String(256))
    capacity = db.Column(db.Integer)
    schedule_file = db.Column(db.String(256))
    info = db.Column(db.Text)

    floor_id = db.Column(db.Integer, db.ForeignKey(Floor.id))

    def __repr__(self):
        return repr(id)


db.create_all()

admin = Admin(app, name='microblog', template_mode='bootstrap3')
admin.add_view(ModelView(Floor, db.session))
admin.add_view(ModelView(Room, db.session))


@app.route('/')
def hello_world():
    return render_template('home.html')


@app.route('/t')
def index():
    return render_template('index.html')


@app.route('/floor', methods=['GET'])
def floorlist():
    floors = Floor.query.all()
    return jsonify([{'id': f.id, 'number': f.number, 'image_file': f.image_file, 'info': f.info} for f in floors])


@app.route('/room', methods=['GET'])
def room_get():
    name = request.args.get('search')
    r = Room.query.filter_by(name=name).all()
    if len(r) < 1:
        return jsonify({}), 404
    r = r[0]
    return jsonify({'id': r.id, 'room_type': r.room_type, 'map_position_x': r.map_position_x,
                    'map_position_y': r.map_position_y, 'capacity': r.capacity
                    })


@app.route("/room", methods=['POST'])
def item_save():
    try:
        new_item = Room(**request.form)
        db.session.add(new_item)
        db.session.commit()
    except BaseException as error:
        return str(error), 400
    return "success", 200


if __name__ == '__main__':
    app.run()
