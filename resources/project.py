import json
import db
from flask_restful import Resource, reqparse
from flask import jsonify
from flask_jwt_extended import jwt_required
from helpers import price_format, multiple
from util.encoder import AlchemyEncoder
from util.logz import create_logger
from util.msg import MSG_FIELD_DEFAULT
from util.parse_json import parse_json

class GetProjectList(Resource):
    def __init__(self):
        self.logger = create_logger()
    
    parser = reqparse.RequestParser()
    parser.add_argument('page_num', type=str, required=True, help=MSG_FIELD_DEFAULT)
    parser.add_argument('items_per_page', type=str, required=True, help=MSG_FIELD_DEFAULT)
    parser.add_argument('sort_by_key', type=str, required=True, help=MSG_FIELD_DEFAULT)
    parser.add_argument('sort_by_order', type=str, required=True, help=MSG_FIELD_DEFAULT)
    parser.add_argument('search', type=str, required=True, help=MSG_FIELD_DEFAULT)

    @jwt_required()  # Requires dat token
    def post(self):
        data = GetProjectList.parser.parse_args()
        page_num = data['page_num']
        items_per_page = data['items_per_page']
        sort_by_key = data['sort_by_key']
        sort_by_order = data['sort_by_order']
        search = data['search']

        order = 1
        if sort_by_order == "desc": order = -1
        
        pipeline = [

            {
                "$lookup": {
                    "from": "pairs",
                    "localField": "pair_address",
                    "foreignField": "pair_address",
                    "as": "pair"
                }
            },
            {
                "$lookup": {
                    "from": "users",
                    "localField": "user_id",
                    "foreignField": "user_id",
                    "as": "user"
                }
            },
            {
                "$unwind": {
                    "path": "$pair",
                }
            },
            {
                "$unwind": {
                    "path": "$user",
                }
            },
            { 
                "$sort": { sort_by_key: order} 
            },
            { "$limit": int(page_num) + int(items_per_page) },
            { "$skip": int(page_num) },
            
        ]
        match_pipeline = [
             { 
                "$match": {
                    "$or":[
                        {"chain": { "$regex": f"{search}*" }},
                        {"token": { "$regex": f"{search}*" }} ,
                        {"pair_url": { "$regex": f"{search}*" }} ,
                        {"pair_address": { "$regex": f"{search}*" }},
                        {"symbol": { "$regex": f"{search}*" }}
                    ]
                }
            }
        ]

        if search:
            pipeline = match_pipeline + pipeline

        raw_projects = db.Project.aggregate(pipeline)
        
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
                "current_marketcap": raw["pair"]["marketcap"],
                "username": raw["user"]["username"]
            })
        count = len(list( db.Project.find()))
        return parse_json({
            "total_count": count,
            "projects": projects
        })
    
class UpdateProject(Resource):
    def __init__(self):
        self.logger = create_logger()
    
    parser = reqparse.RequestParser()
    parser.add_argument('token', type=str, required=True, help=MSG_FIELD_DEFAULT)
    parser.add_argument('pair_address', type=str, required=True, help=MSG_FIELD_DEFAULT)
    parser.add_argument('ath', type=str, required=True, help=MSG_FIELD_DEFAULT)
    parser.add_argument('status', type=str, required=True, help=MSG_FIELD_DEFAULT)

    @jwt_required()  # Requires dat token
    def post(self):
        data = UpdateProject.parser.parse_args()
        token = data['token']
        pair_address = data['pair_address']
        ath = data['ath']
        status = data['status']

        db.Project.update_one({"token": token, "pair_address": pair_address}, {"$set":{"ath": ath, "status": status}})
        return "return_data"