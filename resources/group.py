import json
from db import db, func, and_
from flask_restful import Resource, reqparse
from flask import jsonify
from flask_jwt_extended import jwt_required
from models import Project, Group, GroupUser, User
from util.encoder import AlchemyEncoder
from util.logz import create_logger

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


class GetGroupUserList(Resource):
    def __init__(self):
        self.logger = create_logger()

    @jwt_required()  # Requires dat token
    def get(self, group_id):
        project_count_query = (
            db.session.query(
                Project.user_id,
                func.count(Project.user_id).label("shill_count")
            )
            .group_by(Project.user_id)
            .subquery()
        )
        
        user_query = (
            db.session.query(User.fullname, User.username, User.user_id, project_count_query.c.shill_count)
            .outerjoin(project_count_query, User.user_id == project_count_query.c.user_id)
            .subquery()
        )
        
        group_project_count_query = (
            db.session.query(
                Project.group_id,
                Project.user_id,
                func.count(Project.no).label("group_shill_count")
            )
            .group_by(Project.group_id, Project.user_id)
            .subquery()
        )
        
        query = (
            db.session.query(GroupUser.group_id, user_query.c, group_project_count_query.c.group_shill_count).filter_by(group_id=group_id)
            .outerjoin(user_query, GroupUser.user_id == user_query.c.user_id)
            .outerjoin(group_project_count_query, and_(group_project_count_query.c.user_id == GroupUser.user_id, group_project_count_query.c.group_id == group_id))
        )
        
        results = query.all()
        
        json_output = []
        for result in results:
            single_json = {
                "group_id": result[0],
                "fullname": result[1],
                "username": result[2],
                "user_id": result[3],
                "total_shills": result[4],
                "group_shills": result[5],
            }
            json_output.append(single_json)
        
        return json_output