from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restful import Api
from models import Admin
from datetime import timedelta
import resources
from config import sql_config
from helpers import admin_mysql

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = sql_config
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
# Setup the Flask-JWT-Extended extension
app.config["JWT_SECRET_KEY"] = "Dese.Decent.Pups.BOOYO0OST"  # Change this!
jwt = JWTManager(app)
api = Api(app)

@jwt.user_identity_loader
def user_identity_lookup(admin):
    return admin.no

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return Admin.query.filter_by(no=identity).one_or_none()

with app.app_context():
    from db import db
    db.init_app(app)
    db.create_all()
    admin_mysql()

api.add_resource(resources.SignIn, '/api/signin')
api.add_resource(resources.Info, '/api/info')
# User api part
api.add_resource(resources.GetUserList, '/api/users')
api.add_resource(resources.GetUserGroupList, '/api/user/<user_id>/groups')
api.add_resource(resources.GetUserShillList, '/api/user/<user_id>/shills')
api.add_resource(resources.GetUserBannedGroupList, '/api/user/<user_id>/bans')
api.add_resource(resources.SetUserUnban, '/api/user/unban')
api.add_resource(resources.SetUserBan, '/api/user/ban')
# Group api part
api.add_resource(resources.GetGroupList, '/api/groups')
api.add_resource(resources.GetGroupUserList, '/api/group/<group_id>/users')

if __name__ == '__main__':
    app.run(debug=True)  # important to mention debug=True