import json
from db import db, groups_collection
from flask_restful import Resource, reqparse
from flask import jsonify
from flask_jwt_extended import jwt_required
from util.logz import create_logger
from util.parse_json import parse_json


class GetGroupList(Resource):
    def __init__(self):
        self.logger = create_logger()

    @jwt_required()  # Requires dat token
    def get(self):
        groups = db["groups"].aggregate([
            {
                "$lookup":
                    {
                        "from": "group_users",
                        "localField": "group_id",
                        "foreignField": "group_id",
                        "as": "users"
                    }
            },
            {
                "$lookup":
                    {
                        "from": "projects",
                        "localField": "group_id",
                        "foreignField": "group_id",
                        "as": "projects"
                    }
            },
        ])
        return_groups = []
        for group in groups:
            return_groups.append({
                "_id": str(group["_id"]),
                "group_id": group["group_id"],
                "link": group["link"],
                "title": group["title"],
                "shills": len(group["projects"]),
                "users": len(group["users"])
            })
        return (parse_json(return_groups))


class GetGroupDetail(Resource):
    def __init__(self):
        self.logger = create_logger()

    @jwt_required()  # Requires dat token
    def get(self, group_id):
        group = groups_collection.find_one({"group_id": group_id})
        if not group:
            return {'result': 'error', 'message': "group can not find"}

        raw_projects = db["projects"].aggregate([
            {
                "$match": {
                    "group_id": group_id
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
            # {
            #     "$unwind": {"path": "$pair"}
            # },
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
                "created_at": raw["created_at"],
                "group_id": raw["group_id"],
                "marketcap": raw["marketcap"],
                "pair_address": raw["pair_address"],
                "pair_url": raw["pair_url"],
                "status": raw["status"],
                "symbol": raw["symbol"],
                "token": raw["token"],
                "user_id": raw["user_id"],
                # "current_marketcap": raw["pair"][0]["marketcap"]
            })

        raw_users = db["group_users"].aggregate([
            {
                "$match": {
                    "group_id": group_id
                },
            },
            {

                "$lookup": {
                    "from": "users",
                    "localField": "user_id",
                    "foreignField": "user_id",
                    "as": "user"
                },
            },
            {
                "$unwind":
                {"path": "$user"}
            }
        ])
        users = []
        for raw in raw_users:
            users.append({
                "_id": str(raw["user"]["_id"]),
                "fullname": raw["user"]["fullname"],
                "username": raw["user"]["username"],
                "user_id": raw["user"]["user_id"],
            })

        raw_bans = db["bans"].aggregate([
            {
                "$match": {
                    "group_id": group_id
                },
            },
            {

                "$lookup": {
                    "from": "users",
                    "localField": "user_id",
                    "foreignField": "user_id",
                    "as": "user"
                },
            },
            {
                "$unwind":
                {"path": "$user"}
            }
        ])
        ban = []
        for raw in raw_bans:
            ban.append({
                "fullname": raw["user"]["fullname"],
                "username": raw["user"]["username"],
                "user_id": raw["user"]["user_id"],
            })

        setting = db["settings"].find_one({"group_id": group_id})
        if not setting:
            setting = db["settings"].insert_one({
                "group_id": group_id,
                "shill_mode": False,
                "ban_mode": False
            })
        group_detail = {
            "title": group["title"],
            "link": group["link"],
            "group_id": group_id,
            "total_shills": len(projects),
            "latest_shills": projects,
            "users": users,
            "bans": ban,
            "setting": {
                "_id": str(setting["_id"]),
                "ban_mode": setting["ban_mode"],
                "shill_mode": setting["shill_mode"]
            }
        }

        return parse_json(group_detail)

        # class GetGroupSetting(Resource):
        #     def __init__(self):
        #         self.logger = create_logger()

        #     parser = reqparse.RequestParser()
        #     parser.add_argument('shill_mode', type=bool,
        #                         required=True, help=MSG_FIELD_DEFAULT)
        #     parser.add_argument('ban_mode', type=bool,
        #                         required=True, help=MSG_FIELD_DEFAULT)

        #     @jwt_required()  # Requires dat token
        #     def get(self, group_id):
        #         setting = Setting.query.filter_by(group_id=group_id).one_or_none()
        #         if not setting:
        #             setting = Setting(
        #                 group_id=group_id,
        #                 shill_mode=False,
        #                 ban_mode=False,
        #             )
        #             db.session.add(setting)
        #             db.session.commit()

        #         single_json = json.dumps(setting, cls=AlchemyEncoder)
        #         decoded_json = json.loads(single_json)

        #         return decoded_json

        #     @jwt_required()  # Requires dat token
        #     def post(self, group_id):
        #         data = GetGroupSetting.parser.parse_args()
        #         shill_mode = data['shill_mode']
        #         ban_mode = data['ban_mode']

        #         setting = Setting.query.filter_by(group_id=group_id).one_or_none()
        #         if not setting:
        #             setting = Setting(
        #                 group_id=group_id,
        #                 shill_mode=False,
        #                 ban_mode=False,
        #             )
        #             db.session.add(setting)
        #             db.session.commit()

        #         setting.shill_mode = shill_mode
        #         setting.ban_mode = ban_mode
        #         db.session.commit()

        #         single_json = json.dumps(setting, cls=AlchemyEncoder)
        #         decoded_json = json.loads(single_json)

        #         return decoded_json
