from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restful import Api
from resources.admin import SignIn, Info, Admin
from config import sql_config
from helpers import admin_mysql

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = sql_config
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Setup the Flask-JWT-Extended extension
app.config["JWT_SECRET_KEY"] = "Dese.Decent.Pups.BOOYO0OST"  # Change this!
jwt = JWTManager(app)
api = Api(app)

@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.id

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return Admin.query.filter_by(id=identity).one_or_none()

with app.app_context():
    from db import db
    db.init_app(app)
    db.create_all()
    admin_mysql()

api.add_resource(SignIn, '/api/signin')
api.add_resource(Info, '/api/info')

if __name__ == '__main__':
    app.run(debug=True)  # important to mention debug=True