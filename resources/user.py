import json
from db import db, func
from flask_restful import Resource, reqparse
from flask import jsonify
from flask_jwt_extended import create_access_token, jwt_required, current_user
from models import Admin, Ban, Group, Pair, Project, Setting, User, Warn
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