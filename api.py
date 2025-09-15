from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api, reqparse, fields, marshal_with, abort

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
api = Api(app)

class UserModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return f"User(name = {self.name}, email = {self.email} )"

user_args = reqparse.RequestParser()
user_args.add_argument('name', type=str, required=True, help="Name of the user is required")
user_args.add_argument('email', type=str, required=True, help="email of the user is required")

userFields = {
    'id': fields.Integer,
    'name': fields.String,
    'email': fields.String
}

class Users(Resource):
    @marshal_with(userFields)
    def get(self):
        users = UserModel.query.all()
        return [str(user) for user in users]
    
    @marshal_with(userFields)
    def post(self):
        args = user_args.parse_args()
        user = UserModel(name=args['name'], email=args['email'])
        db.session.add(user)
        db.session.commit()
        users = UserModel.query.all()
        return users, 201 #http status code
    
class User(Resource):  # <-- Rename from 'user' to 'User'
    @marshal_with(userFields)
    def get(self, id):
        user = UserModel.query.filter_by(id=id).first()
        if not user:
            abort(404, message="Could not find user with the given id")
        return user
    
    @marshal_with(userFields)
    def patch(self, id):
        args = user_args.parse_args()
        user = UserModel.query.filter_by(id=id).first()
        if not user:
            abort(404, message="Could not find user with the given id")
        if args["name"]:
            user.name = args["name"]
        if args["email"]:
            user.email = args["email"]
        db.session.commit()
        return user
    
    @marshal_with(userFields)
    def delete(self, id):
        user = UserModel.query.filter_by(id=id).first()
        if not user:
            abort(404, message="Could not find user with the given id")
        db.session.delete(user)
        db.session.commit()
        users = UserModel.query.all()
        return users
    
 
    
api.add_resource(Users, '/api/users/')
api.add_resource(User, '/api/users/<int:id>')  # <-- Now matches the class name

@app.route('/')
def home():
    return '<h1>API Home</h1>'

if __name__ == '__main__':
    app.run(debug=True)
