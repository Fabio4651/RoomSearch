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

class MicroBlogModelView(ModelView):
    # edit_template = 'microblog_edit.html'
    # create_template = 'microblog_create.html'
    list_template = 'back.html'

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
    return render_template('pesquisarsala.html')

    
@app.route('/list')
def list():
    return render_template('back.html')
    
    
@app.route('/admin')
def admin():
    return render_template('/admin/index.html')

#@app.route('/admin/room')
#def room():
#   return render_template('/admin/microblog_listlist.html')    
    

@app.route('/t')
def index():
    return render_template('index2.html')


@app.route('/floor', methods=['GET'])
def floorlist():
    floors = Floor.query.all()
    return jsonify([{'id': f.id, 'number': f.number, 'image_file': f.image_file, 'info': f.info} for f in floors])

#
# @app.route('/room', methods=['GET'])
# def room_get():
#     name = request.args.get('search')
#     r = Room.query.filter_by(name=name).all()
#     if len(r) < 1:
#         return jsonify({}), 404
#     r = r[0]


    #name = request.args.get('search')
    #r = Room.query.filter_by(name=name).all()
   # if len(r) < 1:
    #    return jsonify({}), 404
    #r = r[0]
   # return jsonify({'id': r.id, 'room_type': r.room_type, 'map_position_x': r.map_position_x,
                  #  'map_position_y': r.map_position_y, 'capacity': r.capacity
                 #   })


@app.route("/room", methods=['GET'])
def room_get():
    name = request.args.get('search')
    r = Room.query.filter_by(name=name).all()[0]
    return render_template('index2.html',
        id = r.id,
        room_type = r.room_type,
        map_position_x = r.map_position_x,
        map_position_y = r.map_position_y,
        capacity = r.capacity
    )


if __name__ == '__main__':
    app.run()
