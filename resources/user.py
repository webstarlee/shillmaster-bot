import json
import db
from flask_restful import Resource, reqparse
from flask import jsonify
from flask_jwt_extended import jwt_required
from util.logz import create_logger
from util.msg import MSG_FIELD_DEFAULT
from util.parse_json import parse_json

class GetUserList(Resource):
    def __init__(self):
        self.logger = create_logger()

    @jwt_required()  # Requires dat token
    def get(self):
        raw_users = db.User.aggregate([
            {
                "$lookup": {
                    "from" : "projects",
                    "localField": "user_id",
                    "foreignField": "user_id",
                    "as": "shills"
                }
            }
        ])
        users = []
        for raw in raw_users:
            users.append({
                "_id": str(raw["_id"]),
                "fullname": raw["fullname"],
                "username": raw["username"],
                "user_id": raw["user_id"],
                "shills": len(raw["shills"])
            })
        return parse_json(users)

class GetUserDetail(Resource):
    def __init__(self):
        self.logger = create_logger()

    @jwt_required()  # Requires dat token
    def get(self, user_id):
        user = db.User.find_one({"user_id": user_id})
        if not user:
            return {'result': 'error', 'message': "user can not find"}

        raw_projects = db.Project.aggregate([
            {
                "$match": {
                    "user_id": user_id
                },
            },
            {

                "$lookup": {
                    "from": "pairs",
                    "localField": "pair_address",
                    "foreignField": "pair_address",
                    "as": "pair"
                },
            },
            {
                "$unwind": {"path": "$pair"}
            },
            {
                "$sort": {"created_at": 1}
            }
        ])
        projects = []
        for raw in raw_projects:
            projects.append({
                "_id": str(raw["_id"]),
                "ath": raw["ath"],
                "chain": raw["chain"],
                "created_at": str(raw["created_at"]),
                "group_id": raw["group_id"],
                "marketcap": raw["marketcap"],
                "pair_address": raw["pair_address"],
                "pair_url": raw["pair_url"],
                "status": raw["status"],
                "symbol": raw["symbol"],
                "token": raw["token"],
                "user_id": raw["user_id"],
                "current_marketcap": raw["pair"]["marketcap"]
            })
        raw_groups = db.GroupUser.aggregate([
            {
                "$match": {
                    "user_id": user_id
                }
            },
            {
                "$lookup": {
                    "from": "groups",
                    "localField": "group_id",
                    "foreignField": "group_id",
                    "as": "group"
                }
            },
            {
                "$unwind": {
                    "path": "$group"
                }
            }
        ])
        groups = []
        for raw in raw_groups:
            groups.append({
                "group_id": raw["group"]["group_id"],
                "title": raw["group"]["title"],
            })

        raw_warns = db.Warn.aggregate([
            {
                "$match": {"user_id":user_id}
            },
            {
                "$lookup": {
                    "from": "groups",
                    "localField": "group_id",
                    "foreignField": "group_id",
                    "as": "group"
                }
            },
            {
                "$unwind": {
                    "path": "$group"
                }
            }
        ])
        warns = []
        for raw in raw_warns:
            warns.append({
                "group_id": raw["group"]["group_id"],
                "title": raw["group"]["title"],
                "count": raw["count"]
            })

        raw_bans = db.Ban.aggregate([
            {
                "$match": {"user_id":user_id}
            },
            {
                "$lookup": {
                    "from": "groups",
                    "localField": "group_id",
                    "foreignField": "group_id",
                    "as": "group"
                }
            },
            {
                "$unwind": {
                    "path": "$group"
                }
            }
        ])
        bans = []
        for raw in raw_bans:
            bans.append({
                "group_id": raw["group"]["group_id"],
                "title": raw["group"]["title"],
            })
        return parse_json({
            "fullname": user["fullname"],
            "username": user["username"],
            "user_id": user["user_id"],
            "total_shills": len(projects),
            "latest_shills": projects,
            "groups": groups,
            "warns": warns,
            "bans": bans
        })
#        

class DeleteUserWarn(Resource):
    def __init__(self):
        self.logger = create_logger()

    @jwt_required()  # Requires dat token
    def delete(self, user_id, group_id):
        warn = db.Warn.find_one({"user_id": user_id, "group_id": group_id})
        if not warn:
            return {"result": "not exist"}
        db.Warn.find_one_and_delete({"user_id": user_id, "group_id": group_id})
        return {"result": "success"}

class SetUserUnban(Resource):
    def __init__(self):
        self.logger = create_logger()

    @jwt_required()  # Requires dat token
    def get(self, user_id, group_id):
        ban = db.Ban.find_one({"user_id":user_id, "group_id": group_id})

        if not ban:
            return {'message': 'Ban not found'}, 401
        else:
            db.Ban.find_one_and_delete({"user_id":user_id, "group_id": group_id})

        exist_task = db.Task.find_one({"user_id": user_id, "group_id": group_id})
        if not exist_task:
            db.Task.insert_one({"task":"unban", "user_id": user_id, "group_id": group_id})
        else:
            return {"result": "already exist task"}
        
        return {"result": "success"}

class SetUserBan(Resource):
    def __init__(self):
        self.logger = create_logger()

    parser = reqparse.RequestParser()
    parser.add_argument('user_id', type=str, required=True, help=MSG_FIELD_DEFAULT)
    parser.add_argument('group_id', type=str, required=True, help=MSG_FIELD_DEFAULT)
    
    @jwt_required()
    def post(self):
        data = SetUserBan.parser.parse_args()
        user_id = data['user_id']
        group_id = data['group_id']
        filter_query = {"user_id": user_id, "group_id": group_id}

        ban = db.Ban.find_one(filter_query)
        if not ban:
            is_group_user = db["group_users"].find_one(filter_query)
            if not is_group_user:
                return {"result": "error", "msg": "It is not Group User"}
            
            exist_task = db.Task.find_one(filter_query)
            if not exist_task:
                db.Task.insert_one({"task":"ban", "user_id": user_id, "group_id": group_id})
                return {"result": "success"}
        else:
            return {"result": "error", "msg": "Already exist task"}