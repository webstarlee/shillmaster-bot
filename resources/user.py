import json
from flask import Flask
from flask_restful import Resource
from flask_jwt_extended import  jwt_required
from models import Admin, Ban, Group, Pair, Project, Setting, User, Warn, GroupUser
from util.logz import create_logger

app = Flask(__name__)

class GetUserList(Resource):
    def __init__(self):
        self.logger = create_logger()

    @jwt_required()
    def get(self):
        results = []
        users = User.query.order_by(User.no.desc()).all()
        for user in users:
            shill_count = Project.query.filter_by(user_id=user.user_id).count()
            data = {
                "fullname": user.fullname,
                "username": user.username,
                "user_id": user.user_id,
                "shills": shill_count
            }
            results.append(data)
        return results
    
class GetUserGroups(Resource):
    def __init__(self) -> None:
        self.logger = create_logger()
    @jwt_required()
    def get(self, user_id : str):
        result = []
        group_ids = GroupUser.query.filter_by(user_id=user_id).all()
        for id in group_ids:
            group_list = Group.query.filter_by(group_id=id.group_id).all()
            for group in group_list:
                result.append({
                    "group": group.title
                })
        return result
        
class GetUserShill(Resource):
    def __init__(self) -> None:
        self.logger = create_logger()
    @jwt_required()
    def get(self, user_id: str):
        result = []
        shills = Project.query.filter_by(user_id=user_id).order_by(Project.created_at.desc()).all()
        for shill in shills:
            result.append({
                "chain" : shill.chain,
                "token" : shill.token,
                "symbol"  : shill.symbol
            })
        return result
    
class GetUserBan(Resource):
    def __init__(self) -> None:
        self.logger = create_logger()
    @jwt_required()
    def get(self, user_id: str):
        result = []
        banned = Ban.query.filter_by(user_id=user_id).all()
        for ban in banned:
            groups = Group.query.filter_by(group_id=ban.group_id).all()
            for group in groups:            
                result.append({
                    "Banned Group": group.title
                })  
        return result