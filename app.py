# Imports necessary libraries
from flask import Flask, render_template, request, redirect, jsonify, make_response
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json
import uuid
from datetime import datetime, timedelta
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
# jwt imports
import jwt

# Define the app
app = Flask(__name__)


# secret key
app.config['SECRET_KEY'] = 'Internetix' #didn't used env because of convinience


# database name
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# intializing sqlalchemy
db = SQLAlchemy(app)

# databse model


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(70), unique=True)
    password = db.Column(db.String(80))

# limiter configs


limiter = Limiter(app, key_func=get_remote_address,
                  default_limits=['5 per minute'])


# Jwt decorator

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # cheking token exist or not

        if 'x-access-token' in request.headers:
        	token = request.headers['x-access-token']

        if not token:
            return jsonify({'message': 'please provide token'}), 401

        try:
            # decoding token
            data = jwt.decode(token, app.config['SECRET_KEY'],algorithms=["HS256"])
            current_user = User.query.filter_by(
                public_id=data['public_id']).first()

        except Exception as e:
            return jsonify({
                'message': 'Token invalid',
                'error': e
            }), 401

        return f(current_user, *args, **kwargs)

    return decorated


@app.get('/user')
@token_required
def get_all_users(current_user):
    # querying the database
    # for all the entries in it
    users = User.query.all()

    # converting the query objects
    # to list of jsons
    output = []
    for user in users:
        # appending the user data json
        # to the response list
        output.append({
            'public_id': user.public_id,
            'name': user.name,
            'email': user.email
        })

    return jsonify({'users': output})


@app.post('/login')
def login():
    # creates dictionary of form data
    auth = request.form
    print(auth)

    if not auth or not auth.get('email') or not auth.get('password'):
        # returns 401 if any email or / and password is missing
        return make_response(
            'Could not verify',
            401,
            {'WWW-Authenticate': 'Basic realm ="Login required !!"'}
        )

    user = User.query\
        .filter_by(email=auth.get('email'))\
        .first()

    if not user:
        # returns 401 if user does not exist
        return make_response(
            'Could not verify',
            401,
            {'WWW-Authenticate': 'Basic realm ="User does not exist !!"'}
        )

    if check_password_hash(user.password, auth.get('password')):
        # generates the JWT Token
        token = jwt.encode({
            'public_id': user.public_id,
            'exp': datetime.utcnow() + timedelta(minutes=30)
        }, app.config['SECRET_KEY'])

        return make_response(jsonify({'token': token}), 201)
    # returns 403 if password is wrong
    return make_response(
        'Could not verify',
        403,
        {'WWW-Authenticate': 'Basic realm ="Wrong Password !!"'}
    )


# signup route
@app.post('/signup')
def signup():
    # creates a dictionary of the form data
    data = request.form
    # gets name, email and password
    name, email = data.get('name'), data.get('email')
    password = data.get('password')

    # checking for existing user
    user = User.query\
        .filter_by(email=email)\
        .first()
    if not user:
        # database ORM object
        user = User(
            public_id=str(uuid.uuid4()),
            name=name,
            email=email,
            password=generate_password_hash(password)
        )
        # insert user
        db.session.add(user)
        db.session.commit()

        return make_response('Successfully registered.', 201)
    else:
        # returns 202 if user already exists
        return make_response('User already exists. Please Log in.', 202)


# Get a welcoming message once you start the server.
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/takepictures')
def takepictures():
    return render_template('takepictures.html')


@app.route('/showimage/<filename>')
def showimage(filename):
    # return render_template('showimage.html')
    return f"FILE NAME : <strong> {filename} </strong>"


@app.post('/upload')
@limiter.limit("5/minute")
def upload_file():
    try:
        if(request.files['my_file']):
            try:
                file = request.files['my_file']
                upload_directory = f"{os.getcwd()}/uploads"
                filepath = os.path.exists(upload_directory)
                if not filepath:
                    os.mkdir(upload_directory)
                    file.save(
                        f"{upload_directory}/{secure_filename(file.filename)}")
                else:
                    # return f"{url :/showimage/{file.filename}'}"
                    file.save(
                        f"{upload_directory}/{secure_filename(file.filename)}")

                    return json.dumps({"url": f"/showimage/{file.filename}"})
            except Exception as e:
                return json.dumps("{message: something went wrong}")
        else:
            return json.dumps("{message:provide a file}")

    except Exception as e:
        return json.dumps(f'{e}, Provide a file')

@app.post('/uploadWithAuth')
@token_required
@limiter.limit("5/minute")
def upload_file_with_auth(current_user):
    try:
        if(request.files['my_file']):
            try:
                file = request.files['my_file']
                upload_directory = f"{os.getcwd()}/uploads"
                filepath = os.path.exists(upload_directory)
                if not filepath:
                    os.mkdir(upload_directory)
                    file.save(
                        f"{upload_directory}/{secure_filename(file.filename)}")
                else:
                    # return f"{url :/showimage/{file.filename}'}"
                    file.save(
                        f"{upload_directory}/{secure_filename(file.filename)}")

                    return json.dumps({"url": f"/showimage/{file.filename}"})
            except Exception as e:
                return json.dumps("{message: something went wrong}")
        else:
            return json.dumps("{message:provide a file}")

    except Exception as e:
        return json.dumps(f'{e}, Provide a file')


@app.post('/capture')
def capture():
    file = request.files['capture_img']
    if(file):
        upload_directory = f"{os.getcwd()}/static/imguploads"
        filepath = os.path.exists(upload_directory)
        if not filepath:
            os.mkdir(upload_directory)
            file.save(f"{upload_directory}/{secure_filename(file.filename)}")
        else:
            file.save(f"{upload_directory}/{secure_filename(file.filename)}")
    return jsonifyk({"message":"image uploaded"})


@app.get('/showallpictures')
def showallpictures():
    list_of_images = os.listdir('static/imguploads')
    url_list = []
    for images in list_of_images:
        url = f"imguploads/{images}"
        url_list.append(url)

    return render_template('getallpictures.html',src=url_list)
    
# If the file is run directly,start the app.
if __name__ == '__main__':
    app.run()
