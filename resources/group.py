import json
from db import db, func, and_
from flask_restful import Resource, reqparse
from flask import jsonify
from flask_jwt_extended import jwt_required
from models import Project, Group, GroupUser
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