import os
from os.path import join, dirname, realpath
from flask import Flask, jsonify, render_template, request, redirect, url_for
from flask_admin import Admin
from flask_sqlalchemy import SQLAlchemy
from flask_admin.contrib.sqla import ModelView
from flask_uploads import IMAGES, UploadSet, configure_uploads
from pathlib import Path

app = Flask(__name__)

app.secret_key = "SECRET_TESTING"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# set optional bootswatch theme
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'

files = UploadSet('files', IMAGES)

app.config['UPLOADED_FILES_ALLOW'] = set(['png', 'jpg', 'jpeg', 'pdf'])
app.config['UPLOADED_FILES_DEST'] = 'static/upload'
configure_uploads(app, files)


db = SQLAlchemy(app)


class Floor(db.Model):
    __tablename__ = 'floor'
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer)
    image_file = db.Column(db.String(256))
    info = db.Column(db.Text)

    def __repr__(self):
        return repr(id)

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(256))
    email = db.Column(db.String(256))
    password = db.Column(db.String(256))

    def __repr__(self):
        return repr(id)

class MicroBlogModelView(ModelView):
    # edit_template = 'microblog_edit.html'
    # create_template = 'microblog_create.html'
    list_template = 'list.html'

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

    def __init__(self, name, capacity, map_position_x, map_position_y, room_type, schedule_file, info, floor_id):
        self.name = name
        self.capacity = capacity
        self.map_position_x = map_position_x
        self.map_position_y = map_position_y
        self.room_type = room_type
        self.schedule_file = schedule_file
        self.info = info
        self.floor_id = floor_id
        

    def __repr__(self):
        return repr(id)


db.create_all()

admin = Admin(app, name='microblog', template_mode='bootstrap3')
admin.add_view(ModelView(Floor, db.session))
admin.add_view(ModelView(Room, db.session))



@app.route('/')
def hello_world():
    return render_template('pesquisarsala.html')

    
@app.route('/list_sala')
def list_sala():
    r = Room.query.all()
    return render_template('/list.html', data=r)

@app.route('/insert_sala')
def insert_sala():
    #hor = request.files['horario']
    #return hor.filename
    r = Room.query.all()
    return render_template('addsala.html')

@app.route('/insert_sala2', methods=['POST'])
def insert_sala2():
    descending = Room.query.order_by(Room.id.desc())
    last_item = descending.first()
    last_id = last_item.id + 1
    r = Room.query.all()
    name = request.form['name']
    capacity = request.form['capacity'] 
    map_position_x = request.form['x_pos']
    map_position_y = request.form['y_pos']
    room_type = request.form['type']
    floor_id = request.form['piso']
    info = request.form['info']
    schedule_file = request.files['horario']

    #print(str(last_id))
    #allowed_file(file.filename):

    if request.method == 'POST' and 'horario' in request.files:
        filename = files.save(request.files['horario'], name=str(last_id) + '.pdf')
    
    new_room = Room(name=name, capacity=capacity, map_position_x=map_position_x, map_position_y=map_position_y, room_type=room_type, info=info, floor_id=floor_id, schedule_file=str(last_id) + '.pdf')

    db.session.add(new_room)
    db.session.commit()

    return redirect(url_for('list_sala'))

@app.route('/delete_sala', methods=['POST'])
def delete_sala():
    data = request.args.get('id_sala')
    #delete_room = Room(id=id_room)
    data_file = str(data)+'.pdf'
    Room.query.filter_by(id=data).delete()

    my_file = Path(os.path.join(app.config['UPLOADED_FILES_DEST'], data_file))
    if my_file.exists():
        os.remove(os.path.join(app.config['UPLOADED_FILES_DEST'], data_file))
    db.session.commit()
    return redirect(url_for('list_sala'))


@app.route('/list_user')
def list_user():
    u = User.query.all()
    return render_template('verusers.html', data=u)
    
    
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
