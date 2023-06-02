import json
from db import db, func, and_
from flask_restful import Resource, reqparse
from flask import jsonify
from flask_jwt_extended import jwt_required
from models import Project, Group, GroupUser, User, Ban, Setting, Pair
from helpers import price_format, multiple
from util.encoder import AlchemyEncoder
from util.logz import create_logger
from util.msg import MSG_FIELD_DEFAULT

class GetGroupList(Resource):
    def __init__(self):
        self.logger = create_logger()

    @jwt_required()  # Requires dat token
    def get(self):
        project_query = (
            db.session.query(
                Project.group_id,
                func.count(Project.group_id).label("shill_count")
            )
            .group_by(Project.group_id)
            .subquery()
        )
        
        user_query = (
            db.session.query(
                GroupUser.group_id,
                func.count(GroupUser.group_id).label("user_count")
            )
            .group_by(GroupUser.group_id)
            .subquery()
        )
        
        query = (
            db.session.query(Group, project_query.c.shill_count, user_query.c.user_count)
            .outerjoin(project_query, Group.group_id == project_query.c.group_id)
            .outerjoin(user_query, Group.group_id == user_query.c.group_id)
        )
        
        results = query.all()
        json_output = []
        for result in results:
            single_json = json.dumps(result[0], cls=AlchemyEncoder)
            decoded_json = json.loads(single_json)
            decoded_json['shills'] = result[1]
            decoded_json['users'] = result[2]
            json_output.append(decoded_json)

        return jsonify(json_output)

class GetGroupDetail(Resource):
    def __init__(self):
        self.logger = create_logger()

    @jwt_required()  # Requires dat token
    def get(self, group_id):
        group = Group.query.filter_by(group_id=group_id).one_or_none()
        if not group:
            return {'result': 'error', 'message': "group can not find"}
        
        pair_query = (
            db.session.query(Pair.marketcap, Pair.pair_address).subquery()
        )
        
        project_query = (
            db.session.query(Project, pair_query.c).filter_by(group_id=group_id)
            .join(pair_query, Project.pair_address == pair_query.c.pair_address)
            .order_by(Project.created_at)
        )
        
        project_results = project_query.all()

        total_project_count = Project.query.filter_by(group_id=group_id).count()
        json_output = []
        for latest_project in project_results:
            single_json = json.dumps(latest_project[0], cls=AlchemyEncoder)
            decoded_json = json.loads(single_json)
            decoded_json['current_marketcap'] = latest_project[1]
            json_output.append(decoded_json)
        
        user_query = (
            db.session.query(User.fullname, User.username, User.user_id, User.no).subquery()
        )
        
        query = (
            db.session.query(GroupUser.group_id, user_query.c).filter_by(group_id=group_id)
            .outerjoin(user_query, GroupUser.user_id == user_query.c.user_id)
        )
        
        results = query.all()
        group_users = []
        
        for result in results:
            single_user = {
                "no": result[4],
                "user_id": result[3],
                "fullname": result[1],
                "username": result[2],
            }
            group_users.append(single_user)
        
        ban_query = (
            db.session.query(Ban.group_id, user_query.c).filter_by(group_id=group_id)
            .outerjoin(user_query, Ban.user_id == user_query.c.user_id)
        )
        
        ban_results = ban_query.all()
        
        group_bans = []
        
        for result in ban_results:
            single_ban = {
                "user_id": result[3],
                "fullname": result[1],
                "username": result[2],
            }
            group_bans.append(single_ban)
        
        setting = Setting.query.filter_by(group_id=group_id).one_or_none()
        if not setting:
            setting = Setting(
                group_id=group_id,
                shill_mode=False,
                ban_mode=False,
            )
            db.session.add(setting)
            db.session.commit()
        
        single_json = json.dumps(setting, cls=AlchemyEncoder)
        group_setting = json.loads(single_json)
        
        group_detail = {
            "title": group.title,
            "link": group.link,
            "group_id": group.group_id,
            "total_shills": total_project_count,
            "latest_shills": json_output,
            "users": group_users,
            "bans": group_bans,
            "setting": group_setting
        }
        
        return group_detail

class GetGroupSetting(Resource):
    def __init__(self):
        self.logger = create_logger()
        
    parser = reqparse.RequestParser()
    parser.add_argument('shill_mode', type=bool, required=True, help=MSG_FIELD_DEFAULT)
    parser.add_argument('ban_mode', type=bool, required=True, help=MSG_FIELD_DEFAULT)

    @jwt_required()  # Requires dat token
    def get(self, group_id):
        setting = Setting.query.filter_by(group_id=group_id).one_or_none()
        if not setting:
            setting = Setting(
                group_id=group_id,
                shill_mode=False,
                ban_mode=False,
            )
            db.session.add(setting)
            db.session.commit()
        
        single_json = json.dumps(setting, cls=AlchemyEncoder)
        decoded_json = json.loads(single_json)
        
        return decoded_json
    
    @jwt_required()  # Requires dat token
    def post(self, group_id):
        data = GetGroupSetting.parser.parse_args()
        shill_mode = data['shill_mode']
        ban_mode = data['ban_mode']
        
        setting = Setting.query.filter_by(group_id=group_id).one_or_none()
        if not setting:
            setting = Setting(
                group_id=group_id,
                shill_mode=False,
                ban_mode=False,
            )
            db.session.add(setting)
            db.session.commit()
        
        setting.shill_mode = shill_mode
        setting.ban_mode = ban_mode
        db.session.commit()
        
        single_json = json.dumps(setting, cls=AlchemyEncoder)
        decoded_json = json.loads(single_json)
        
        return decoded_json