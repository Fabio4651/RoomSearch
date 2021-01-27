import os
from pathlib import Path

from flask import Flask, jsonify, render_template, request, redirect, url_for, session
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_uploads import IMAGES, UploadSet, configure_uploads

app = Flask(__name__)

app.secret_key = "SECRET_TESTING"

app.config['SECRET_KEY'] = '_1#y6G"F7Q2z\n\succ/'
app.config['APPLICATION_ROOT'] = "/"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_TYPE'] = 'sqlalchemy'

# set optional bootswatch theme
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'

files = UploadSet('files', IMAGES)

app.config['UPLOADED_FILES_ALLOW'] = set(['png', 'jpg', 'jpeg', 'pdf'])
app.config['UPLOADED_FILES_DEST'] = 'static/upload'
configure_uploads(app, files)

db = SQLAlchemy(app)

app.config['SESSION_SQLALCHEMY'] = db
app.config['APPLICATION_ROOT'] = "/"

sess = Session(app)


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
    map_position_x = db.Column(db.Float(16))
    map_position_y = db.Column(db.Float(16))
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
def index():
    return render_template('pesquisarsala.html')


@app.route('/list_sala')
def list_sala():
    r = Room.query.all()
    return render_template('/list.html', data=r)


@app.route('/search_sala', methods=['GET'])
def all_sala():
    r = Room.query.all()
    names = [room.name for room in r]
    return jsonify(names)


@app.route('/list_user')
def list_user():
    u = User.query.all()
    return render_template('/listuser.html', data=u)


@app.route('/insert_user')
def insert_user():
    u = User.query.all()
    return render_template('adduser.html')


@app.route('/insert_user2', methods=['POST'])
def insert_user2():
    nome = request.form['nome']
    email = request.form['email']
    password = request.form['password']

    new_user = User(nome=nome, email=email, password=password)

    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('list_user'))


@app.route('/insert_sala')
def insert_sala():
    # hor = request.files['horario']
    # return hor.filename
    r = Room.query.all()
    return render_template('addsala.html')


@app.route('/insert_sala2', methods=['POST'])
def insert_sala2():
    name = request.form['name']
    capacity = request.form['capacity']
    room_type = request.form['type']
    floor_id = request.form['piso']
    info = request.form['info']
    map_position_x = request.form['x_pos']
    map_position_y = request.form['y_pos']
    schedule_file = request.files['horario']
    filename = 'static/img/dummy.pdf'

    if request.method == 'POST' and schedule_file:
        filename = files.save(request.files['horario'])

    new_room = Room(name=name, capacity=capacity, map_position_x=map_position_x, map_position_y=map_position_y,
                    room_type=room_type, info=info, floor_id=floor_id, schedule_file=filename)

    db.session.add(new_room)
    db.session.commit()

    return redirect(url_for('list_sala'))


@app.route('/delete_sala', methods=['POST'])
def delete_sala():
    data = request.args.get('id_sala')
    # delete_room = Room(id=id_room)
    data_file = str(data) + '.pdf'
    Room.query.filter_by(id=data).delete()

    my_file = Path(os.path.join(app.config['UPLOADED_FILES_DEST'], data_file))
    if my_file.exists():
        os.remove(os.path.join(app.config['UPLOADED_FILES_DEST'], data_file))
    db.session.commit()
    return redirect(url_for('list_sala'))


@app.route('/delete_user', methods=['POST'])
def delete_user():
    data = request.args.get('id_user')
    User.query.filter_by(id=data).delete()
    db.session.commit()
    return redirect(url_for('list_user'))


@app.route("/update_user", methods=['POST'])
def update_user():
    data = request.args.get('id_user')
    update = User.query.filter_by(id=data)

    return render_template('edituser.html', update=update)


@app.route('/edit_user', methods=['POST'])
def edit_user():
    data = request.form['id']
    update = User.query.filter_by(id=data).first()
    bd_doc = update.schedule_file
    schedule_file = request.files['horario']

    if request.method == 'POST' and 'nome' in request.form:
        update.nome = request.form['nome']

    if request.method == 'POST' and 'email' in request.form:
        update.email = request.form['email']

    if request.method == 'POST' and 'password' in request.form:
        update.password = request.form['password']

    db.session.commit()
    return redirect(url_for('list_user'))


@app.route("/update_sala", methods=['POST'])
def update_sala():
    data = request.args.get('id_sala')
    update = Room.query.filter_by(id=data).first()

    return render_template('editsala.html', update=update)


@app.route('/edit_sala', methods=['POST'])
def edit_sala():
    data = request.form['id']
    update = Room.query.filter_by(id=data).first()
    bd_doc = update.schedule_file
    schedule_file = request.files['horario']

    if request.method == 'POST' and 'name' in request.form:
        update.name = request.form['name']

    if request.method == 'POST' and 'capacity' in request.form:
        update.capacity = request.form['capacity']

    if request.method == 'POST' and 'x_pos' in request.form:
        update.map_position_x = request.form['x_pos']

    if request.method == 'POST' and 'y_pos' in request.form:
        update.map_position_y = request.form['y_pos']

    if request.method == 'POST' and 'piso' in request.form:
        update.floor_id = request.form['piso']

    if request.method == 'POST' and 'info' in request.form:
        update.info = request.form['info']

    if request.method == 'POST' and 'type' in request.form:
        update.room_type = request.form['type']

    update.schedule_file = bd_doc
    if request.method == 'POST' and schedule_file:
        update.schedule_file = 'static/upload/' + files.save(request.files['horario'])

    db.session.commit()
    return redirect(url_for('list_sala'))


@app.route('/admin')
def admin():
    return render_template('/admin/index.html')


@app.route('/admin_login')
def admin_login():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    querydata = User.query.filter_by(email=email, password=password).first()
    session['username'] = querydata.nome
    # session['profile'] = querydata.img
    return redirect(url_for('list_sala'))


@app.route('/logout')
def logout():
    session.pop('username', None)
    session.clear()
    return redirect(url_for('admin_login'))


@app.route('/floor', methods=['GET'])
def floorlist():
    floors = Floor.query.all()
    return jsonify([{'id': f.id, 'number': f.number, 'image_file': f.image_file, 'info': f.info} for f in floors])


@app.route("/room", methods=['GET'])
def room_get():
    name = request.args.get('search')
    r = Room.query.filter_by(name=name).all()[0]
    return render_template(
        'index.html',
        id=r.id,
        name=r.name,
        room_type=r.room_type,
        map_position_x=r.map_position_x,
        map_position_y=r.map_position_y,
        capacity=r.capacity,
        floor_id=r.floor_id,
        schedule_file=r.schedule_file,
        info=r.info
    )


if __name__ == '__main__':
    app.run(debug=True)
