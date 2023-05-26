from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, current_user
from util.logz import create_logger
from models import Group, GroupUser, User, GroupUser, Project, Ban

class GetGroupList(Resource):
    def __init__(self):
        self.logger = create_logger()

    @jwt_required()
    def get(self):
        groups = Group.query.order_by(Group.no).all()
        result = []
        for group in groups:
            user_count = GroupUser.query.filter_by(group_id=group.group_id).count()
            shill_count = Project.query.filter_by(group_id=group.group_id).count()
            data = {
                "group_id": group.group_id,
                "group_title": group.title,
                "group_link": group.link,
                "users": user_count,
                "shills": shill_count,
            }
            result.append(data)
        
        return result
    
class GetUsersByGroup(Resource):
    def __init__(self):
        self.logger = create_logger()
        
    parser = reqparse.RequestParser()
    parser.add_argument('no', type=str, required=True, location=['headers', 'values'], help='This field cannot be left blank')

    @jwt_required()
    def post(self):
        req = GetUsersByGroup.parser.parse_args()
        users = GroupUser.query.filter_by(group_id=req["no"]).all()
        res=[]
        for user in users:
            userinfo = User.query.filter_by(user_id=user.user_id).first()
            res.append({
                "fullname" : userinfo.fullname,
                "username" : userinfo.username,
                "user_id"  : userinfo.user_id
            })
        return res 
        
class GetShillsByGroup(Resource):
    def __init__(self):
        self.logger = create_logger()
        
    parser = reqparse.RequestParser()
    parser.add_argument('no', type=str, required=True, location=['headers', 'values'], help='This field cannot be left blank')

    @jwt_required()
    def post(self):
        req = GetShillsByGroup.parser.parse_args()
        projects = Project.query.filter_by(group_id=req["no"]).all()
        res=[]
        for project in projects:
            res.append({
                "token" : project.token
            })
        return res 
    
class GetBannedUsersByGroup(Resource):
    def __init__(self):
        self.logger = create_logger()
        
    parser = reqparse.RequestParser()
    parser.add_argument('no', type=str, required=True, location=['headers', 'values'], help='This field cannot be left blank')
    
    @jwt_required()
    def post(self):
        req = GetUsersByGroup.parser.parse_args()
        users = Ban.query.filter_by(group_id=req["no"]).all()
        res=[]
        for user in users:
            userinfo = User.query.filter_by(user_id=user.user_id).first()
            res.append({
                "fullname" : userinfo.fullname,
                "username" : userinfo.username,
                "user_id"  : userinfo.user_id
            })
        return res