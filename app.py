from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restful import Api
from flask_cors import CORS
from datetime import timedelta
import resources
from util.parse_json import parse_json

app = Flask(__name__)
CORS(app)

app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
# Setup the Flask-JWT-Extended extension
app.config["JWT_SECRET_KEY"] = "Dese.Decent.Pups.BOOYO0OST"  # Change this!
jwt = JWTManager(app)
api = Api(app)

api.add_resource(resources.SignIn, '/api/signin')
api.add_resource(resources.Info, '/api/info')
# User api part
api.add_resource(resources.GetUserList, '/api/users')
api.add_resource(resources.GetUserDetail, '/api/user/<user_id>')
api.add_resource(resources.DeleteUserWarn, '/api/user/<user_id>/<group_id>/warn')
api.add_resource(resources.SetUserUnban, '/api/user/<user_id>/<group_id>/unban')
api.add_resource(resources.SetUserBan, '/api/user/ban')
# Group api part
api.add_resource(resources.GetGroupList, '/api/groups')
api.add_resource(resources.GetGroupDetail, '/api/group/<group_id>')
api.add_resource(resources.GetGroupSetting, '/api/group/<group_id>/setting')
# Project api part
api.add_resource(resources.GetProjectList, '/api/projects')
api.add_resource(resources.UpdateProject, '/api/project/update')
# Leader Board api part
api.add_resource(resources.GetLeaderBoards, '/api/leaderboards')

if __name__ == '__main__':
    app.run(debug=True, port=5000)  # important to mention debug=True