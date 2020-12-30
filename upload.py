from flask import Flask, jsonify, render_template, request, redirect, url_for
from flask_uploads import IMAGES, UploadSet, configure_uploads

app = Flask(__name__)

photos = UploadSet('photos', IMAGES)

app.config['UPLOADED_PHOTOS_DEST'] = 'static/upload'
configure_uploads(app, photos)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST' and 'photo' in request.files:
        filename = photos.save(request.files['photo'])
        return filename
    return render_template('upload.html')    

if __name__ == '__main__':
    app.run(debug=True)
