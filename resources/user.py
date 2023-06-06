import json
from db import db, func, and_
from flask_restful import Resource, reqparse
from flask import jsonify
from flask_jwt_extended import jwt_required
from models import GroupUser, Group, Project, User, Ban, Task, Warn, Pair
from util.encoder import AlchemyEncoder
from util.logz import create_logger
from util.msg import MSG_FIELD_DEFAULT

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

class GetUserDetail(Resource):
    def __init__(self):
        self.logger = create_logger()

    @jwt_required()  # Requires dat token
    def get(self, user_id):
        user = User.query.filter_by(user_id=user_id).one_or_none()
        if not user:
            return {'result': 'error', 'message': "user can not find"}
        
        pair_query = (
            db.session.query(Pair.marketcap, Pair.pair_address).subquery()
        )
        
        project_query = (
            db.session.query(Project, pair_query.c).filter_by(user_id=user_id)
            .join(pair_query, Project.pair_address == pair_query.c.pair_address)
            .order_by(Project.created_at)
        )
        
        project_results = project_query.all()
        
        print(project_results)

        total_project_count = Project.query.filter_by(user_id=user_id).count()
        json_output = []
        for latest_project in project_results:
            single_json = json.dumps(latest_project[0], cls=AlchemyEncoder)
            decoded_json = json.loads(single_json)
            decoded_json['current_marketcap'] = latest_project[1]
            json_output.append(decoded_json)
        
        group_query = (
            db.session.query(Group.title, Group.link, Group.group_id).subquery()
        )
        
        query = (
            db.session.query(GroupUser.user_id, group_query.c).filter_by(user_id=user_id)
            .outerjoin(group_query, GroupUser.group_id == group_query.c.group_id)
        )
        
        results = query.all()
        user_groups = []
        
        for result in results:
            single_group = {
                "group_id": result[3],
                "title": result[1],
                "link": result[2],
            }
            user_groups.append(single_group)
        
        warn_query = (
            db.session.query(Warn.user_id, Warn.count, group_query.c).filter_by(user_id=user_id)
            .outerjoin(group_query, Warn.group_id == group_query.c.group_id)
        )
        
        warn_results = warn_query.all()
        
        user_warns = []
        
        for result in warn_results:
            single_warn = {
                "group_id": result[4],
                "title": result[2],
                "link": result[3],
                "count": result[1],
            }
            user_warns.append(single_warn)
            
        ban_query = (
            db.session.query(Ban.user_id, group_query.c).filter_by(user_id=user_id)
            .outerjoin(group_query, Ban.group_id == group_query.c.group_id)
        )
        
        ban_results = ban_query.all()
        
        user_bans = []
        
        for result in ban_results:
            single_ban = {
                "group_id": result[3],
                "title": result[1],
                "link": result[2],
            }
            user_bans.append(single_ban)
        
        user_detail = {
            "fullname": user.fullname,
            "username": user.username,
            "user_id": user.user_id,
            "total_shills": total_project_count,
            "latest_shills": json_output,
            "groups": user_groups,
            "warns": user_warns,
            "bans": user_bans
        }
        
        return user_detail

class DeleteUserWarn(Resource):
    def __init__(self):
        self.logger = create_logger()

    @jwt_required()  # Requires dat token
    def delete(self, user_id, group_id):
        warn = Warn.query.filter_by(user_id=user_id).filter_by(group_id=group_id).one_or_none()
        
        if not warn:
            return {"result": "not exist"}

        # Delete the row
        db.session.delete(warn)

        # Commit the transaction
        db.session.commit()

        return {"result": "success"}

class SetUserUnban(Resource):
    def __init__(self):
        self.logger = create_logger()

    @jwt_required()  # Requires dat token
    def get(self, user_id, group_id):
        ban = Ban.query.filter_by(user_id=user_id).filter_by(group_id=group_id).one_or_none()
        if not ban:
            return {'message': 'Ban not found'}, 401
        
        exist_task = Task.query.filter_by(user_id=user_id).filter_by(group_id=group_id).one_or_none()
        if not exist_task:
            new_task = Task(
                task="unban",
                user_id=user_id,
                group_id=group_id
            )
            db.session.add(new_task)
            db.session.commit()
        
        db.session.delete(ban)
        db.session.commit()
        
        return {"result": "already exist task"}

class SetUserBan(Resource):
    def __init__(self):
        self.logger = create_logger()

    parser = reqparse.RequestParser()
    parser.add_argument('user_id', type=str, required=True, help=MSG_FIELD_DEFAULT)
    parser.add_argument('group_id', type=str, required=True, help=MSG_FIELD_DEFAULT)
    
    @jwt_required()
    def post(self):
        data = SetUserUnban.parser.parse_args()
        user_id = data['user_id']
        group_id = data['group_id']

        ban = Ban.query.filter_by(user_id=user_id).filter_by(group_id=group_id).one_or_none()
        if not ban:
            is_group_user = GroupUser.query.filter_by(user_id=user_id).filter_by(group_id=group_id).one_or_none()
            if not is_group_user:
                return {"result": "error", "msg": "It is not Group User"}
            
            exist_task = Task.query.filter_by(user_id=user_id).filter_by(group_id=group_id).one_or_none()
            if not exist_task:
                new_task = Task(
                    task="ban",
                    user_id=user_id,
                    group_id=group_id
                )
                db.session.add(new_task)
                db.session.commit()
                
                return {"result": "success"}
        
        return {"result": "error", "msg": "Already exist task"}