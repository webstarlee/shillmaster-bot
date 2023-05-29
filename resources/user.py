import json
from db import db, func, and_
from flask_restful import Resource, request, reqparse
from flask import jsonify
from flask_jwt_extended import jwt_required
from models import GroupUser, Group, Project, User, Ban
from util.encoder import AlchemyEncoder
from util.logz import create_logger

class GetUserList(Resource):
    def __init__(self):
        self.logger = create_logger()

    @jwt_required()  # Requires dat token
    def get(self):
        project_query = (
            db.session.query(
                Project.user_id,
                func.count(Project.user_id).label("shill_count")
            )
            .group_by(Project.user_id)
            .subquery()
        )
        query = (
            db.session.query(User, project_query.c.shill_count)
            .outerjoin(project_query, User.user_id == project_query.c.user_id)
        )
        
        results = query.all()
        json_output = []
        for result in results:
            single_json = json.dumps(result[0], cls=AlchemyEncoder)
            decoded_json = json.loads(single_json)
            decoded_json['shills'] = result[1]
            json_output.append(decoded_json)

        return jsonify(json_output)
 
class GetUserGroupList(Resource):
    def __init__(self):
        self.logger = create_logger()

    @jwt_required()  # Requires dat token
    def get(self, user_id):
        project_count_query = (
            db.session.query(
                Project.group_id,
                func.count(Project.group_id).label("shill_count")
            )
            .group_by(Project.group_id)
            .subquery()
        )
        
        user_count_query = (
            db.session.query(
                GroupUser.group_id,
                func.count(GroupUser.group_id).label("user_count")
            )
            .group_by(GroupUser.group_id)
            .subquery()
        )
        
        banned_user_query = (
            db.session.query(
                Ban.group_id,
                func.count(Ban.group_id).label("banned_user_count")
            )
            .group_by(Ban.group_id)
            .subquery()
        )
        
        group_query = (
            db.session.query(Group.title, Group.link, Group.group_id, project_count_query.c.shill_count, user_count_query.c.user_count, banned_user_query.c.banned_user_count)
            .outerjoin(project_count_query, Group.group_id == project_count_query.c.group_id)
            .outerjoin(user_count_query, Group.group_id == user_count_query.c.group_id)
            .outerjoin(banned_user_query, Group.group_id == banned_user_query.c.group_id)
            .subquery()
        )
        
        user_project_count_query = (
            db.session.query(
                Project.group_id,
                Project.user_id,
                func.count(Project.no).label("user_shill_count")
            )
            .group_by(Project.group_id, Project.user_id)
            .subquery()
        )
        
        query = (
            db.session.query(GroupUser.user_id, group_query.c, user_project_count_query.c.user_shill_count).filter_by(user_id=user_id)
            .outerjoin(group_query, GroupUser.group_id == group_query.c.group_id)
            .outerjoin(user_project_count_query, and_(user_project_count_query.c.group_id == GroupUser.group_id, user_project_count_query.c.user_id == user_id))
        )
        
        results = query.all()
        
        json_output = []
        for result in results:
            single_json = {
                "group_id": result[3],
                "title": result[1],
                "link": result[2],
                "user_id": result[0],
                "user_shills": result[7],
                "total_shills": result[4],
                "total_users": result[5],
                "banned_users": result[6],
            }
            json_output.append(single_json)
        
        return json_output

class GetUserShillList(Resource):
    def __init__(self):
        self.logger = create_logger()

    @jwt_required()  # Requires dat token
    def get(self, user_id):
        query = (
            db.session.query(Project).filter_by(user_id=user_id).order_by(Project.created_at)
        )
        
        results = query.all()
        json_output = []
        for result in results:
            single_json = json.dumps(result, cls=AlchemyEncoder)
            decoded_json = json.loads(single_json)
            json_output.append(decoded_json)

        return jsonify(json_output)

class GetUserBannedGroupList(Resource):
    def __init__(self):
        self.logger = create_logger()

    @jwt_required()  # Requires dat token
    def get(self, user_id):
        project_count_query = (
            db.session.query(
                Project.group_id,
                func.count(Project.group_id).label("shill_count")
            )
            .group_by(Project.group_id)
            .subquery()
        )
        
        user_count_query = (
            db.session.query(
                GroupUser.group_id,
                func.count(GroupUser.group_id).label("user_count")
            )
            .group_by(GroupUser.group_id)
            .subquery()
        )
        
        banned_user_query = (
            db.session.query(
                Ban.group_id,
                func.count(Ban.group_id).label("banned_user_count")
            )
            .group_by(Ban.group_id)
            .subquery()
        )
        
        group_query = (
            db.session.query(Group.title, Group.link, Group.group_id, project_count_query.c.shill_count, user_count_query.c.user_count, banned_user_query.c.banned_user_count)
            .outerjoin(project_count_query, Group.group_id == project_count_query.c.group_id)
            .outerjoin(user_count_query, Group.group_id == user_count_query.c.group_id)
            .outerjoin(banned_user_query, Group.group_id == banned_user_query.c.group_id)
            .subquery()
        )
        
        query = (
            db.session.query(Ban.user_id, group_query.c).filter_by(user_id=user_id)
            .outerjoin(group_query, Ban.group_id == group_query.c.group_id)
        )
        
        results = query.all()
        
        json_output = []
        for result in results:
            single_json = {
                "group_id": result[3],
                "title": result[1],
                "link": result[2],
                "user_id": result[0],
                "total_shills": result[4],
                "total_users": result[5],
                "banned_users": result[6],
            }
            json_output.append(single_json)

        return jsonify(json_output)