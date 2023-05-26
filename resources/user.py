from flask import jsonify
from flask_restful import Resource
from flask_jwt_extended import  jwt_required
from sqlalchemy import func
from models import Ban, Group, Project, User, GroupUser
from util.logz import create_logger
from helpers.list_to_json import list_to_json

class GetUserList(Resource):
    def __init__(self):
        self.logger = create_logger()

    @jwt_required()
    def get(self):
        result = User.query.with_entities(User.username, User.fullname, User.user_id, func.count(Project.no).label('shills')).join(Project, Project.user_id==User.user_id).group_by(User.user_id).all()
        # return list_to_json(result)
        print(result)
    
class GetUserGroups(Resource):
    def __init__(self) -> None:
        self.logger = create_logger()
    @jwt_required()
    def get(self, user_id : str):
        result = []
        group_ids = GroupUser.query.filter_by(user_id=user_id).all()
        for id in group_ids:
            group_list = Group.query.filter_by(group_id=id.group_id).first().title
            result.append({
                "group": group_list
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
            groups = Group.query.filter_by(group_id=ban.group_id).first().title
            result.append({
                "Banned Group": groups
            })  
        return result