from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from flask_mail import Mail, Message
from dotenv import load_dotenv
import os

load_dotenv('.envfile')

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "sources.db")}'
app.config['JWT_SECRET_KEY'] = os.environ['JWT_SECRET_KEY']

app.config['MAIL_SERVER'] = 'smtp.mailtrap.io'
app.config['MAIL_USERNAME'] = os.environ['MAIL_USERNAME']
app.config['MAIL_PASSWORD'] = os.environ['MAIL_PASSWORD']


db = SQLAlchemy(app)
ma = Marshmallow(app)
jwt = JWTManager(app)
mail = Mail(app)


@app.cli.command('db_create')
def create_db():
    db.create_all()
    print("Database created")


@app.cli.command('db_drop')
def create_db():
    db.drop_all()
    print("Database dropped")

@app.cli.command('db_seed')
def create_db():
    indeed = Source(
        source_name='indeed',
        source_url='https://www.indeed.com',
        source_type="job_board",
        average_jobs=3_112_734,
        source_country="US"
        )
    
    adidas = Source(
        source_name='adidas',
        source_url='https://careers.adidas-group.com',
        source_type="company",
        average_jobs=110,
        source_country="WORLDWIDE"
        )

    db.session.add(indeed)
    db.session.add(adidas)

    test_user = User(
        first_name="Abc",
        last_name="Def",
        email="abc@abc.com",
        password="password",
    )
    db.session.add(test_user)
    db.session.commit()
    print("Database Seed Complete..")

@app.route('/not_found')
def not_found():
    return jsonify(message="Not Found"), 404

@app.route('/')
def index():
    return jsonify(message="Hello world")


@app.route('/parameters')
def parameters():
    name = request.args.get('name')
    age = int(request.args.get('age'))
    if age < 18:
        return jsonify(message=f"Sorry {name}! You are not old enough"), 401
    else:
        return jsonify(message=f"{name}! You are old enough")


@app.route('/url_variables/<string:name>/<int:age>')
def url_variables(name: str, age: int):
    if age < 18:
        return jsonify(message=f"Sorry {name}! You are not old enough [From URL paramenters]"), 401
    else:
        return jsonify(message=f"{name}! You are old enough [From URL Parameters]")


@app.route('/sources', methods=['GET'])
@jwt_required
def sources():
    source_list = Source.query.all()
    result = sources_schema.dump(source_list)
    return jsonify(result)

@app.route('/register', methods=['POST'])
def register():
    email = request.form['email']
    test = User.query.filter_by(email=email).first()
    if test:
        return jsonify(message="That email already exists"), 409
    else:
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        password = request.form['password']
        user = User(
            first_name=first_name,
            last_name=last_name,
            password=password
        )
        db.session.add(user)
        db.session.commit()
        return jsonify(message="User Created Successfully"), 200

@app.route('/login', methods=['POST'])
def login():
    if request.is_json:
        email = request.json['email']
        password = request.json['password']
    else:
        email = request.form['email']
        password = request.form['password']
    
    test = User.query.filter_by(email=email, password=password).first()
    if test:
        access_token = create_access_token(identity=email)
        return jsonify(message="Login succeeded!", access_token=access_token)
    else:
        return jsonify(message="Bad email or password"), 401

@app.route('/retrieve_password/<string:email>', methods=['GET'])
@jwt_required
def retrieve_password(email: str):
    user = User.query.filter_by(email=email).first()
    if user:
        msg = Message(f"Your planetory API PW is {user.password}",
        sender="admin@source.com",
        recipients=[email]
        )
        mail.send(msg)
        return jsonify(message=f"Password sent to {email}")
    else:
        return jsonify(message=f"Email does not access"), 401


@app.route('/source_details/<int:source_id>', methods=['GET'])
@jwt_required
def source_details(source_id: int):
    source = Source.query.filter_by(source_id=source_id).first()
    if source:
        result = source_schema.dump(source)
        return jsonify(result)
    else:
        return jsonify(message="Source does not exist"), 404


@app.route('/add_source', methods=['POST'])
@jwt_required
def add_source():
    source_name = request.form['source_name']
    test = Source.query.filter_by(source_name=source_name).first()
    if test:
        return jsonify(message="Sourcename already exists"), 409
    else:
        source_url = request.form['source_url']
        source_type = request.form['source_type']
        average_jobs = int(request.form['average_jobs'])
        source_country = request.form['source_country']
        new_source = Source(
            source_name=source_name,
            source_url=source_url,
            source_type=source_type,
            average_jobs=average_jobs,
            source_country=source_country
        )
        db.session.add(new_source)
        db.session.commit()
        return jsonify(message="New source added"), 201


@app.route('/update_source', methods=["PUT"])
@jwt_required
def update_source():
    source_id = int(request.form['source_id'])
    source = Source.query.filter_by(source_id=source_id).first()
    if source:
        source.source_url = request.form['source_url']
        source.source_type = request.form['source_type']
        source.average_jobs = int(request.form['average_jobs'])
        source.source_country = request.form['source_country']
        db.session().commit()
        return jsonify(message="Source is updated"), 202 
    else:
        return jsonify(message="Source Does not exist"), 404


@app.route('/delete_source/<int:source_id>', methods=["DELETE"])
@jwt_required
def delete_source(source_id: int):
    source = Source.query.filter_by(source_id=source_id).first()
    if source:
        db.session.delete(source)
        db.session().commit()
        return jsonify(message="Source is Deleted"), 202 
    else:
        return jsonify(message="Source Does not exist"), 404

# database models

class User(db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)


class Source(db.Model):
    __tablename__ = 'sources'
    source_id = Column(Integer, primary_key=True)
    source_name = Column(String)
    source_url = Column(String)
    source_type = Column(String)
    average_jobs = Column(Integer)
    source_country = Column(String)

class UserShchema(ma.Schema):
    class Meta:
        fields = ("id", "first_name", "last_name", "email", "password")

class SourceSchema(ma.Schema):
    class Meta:
        fields = ("source_id", "source_name", "source_url", "source_type", "average_jobs", "source_country")

user_schema = UserShchema()
users_schema = UserShchema(many=True)


source_schema = SourceSchema()
sources_schema = SourceSchema(many=True)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=3000)