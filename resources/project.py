import json
from db import db, func, and_, desc, asc, or_
from flask_restful import Resource, reqparse
from flask import jsonify
from flask_jwt_extended import jwt_required
from models import Project, Group, GroupUser, User, Ban, Setting, Pair
from helpers import price_format, multiple
from util.encoder import AlchemyEncoder
from util.logz import create_logger
from util.msg import MSG_FIELD_DEFAULT

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

        pair_query = (
            db.session.query(
                Pair.marketcap.label("current_marketcap"),
                Pair.pair_address,
            )
            .subquery()
        )
        
        user_query = (
            db.session.query(
                User.username,
                User.user_id,
            )
            .subquery()
        )
        
        search_clause = or_()
        order_clause = asc(f'{sort_by_key}')
        if sort_by_order == "desc":
            order_clause = desc(f'{sort_by_key}')
        
        if search != '':
            search_clause = or_(
                    Project.symbol.like(f'%{search}%'),
                    Project.token.like(f'%{search}%'),
                    Project.chain.like(f'%{search}%'),
                    Project.pair_url.like(f'%{search}%'),
                    Project.pair_address.like(f'%{search}%'),
                    user_query.c.username.like(f'%{search}%')
                )
        
        query = (
                db.session.query(Project, pair_query.c, user_query.c)
                .filter(search_clause)
                .order_by(order_clause)
                .outerjoin(pair_query, Project.pair_address == pair_query.c.pair_address)
                .outerjoin(user_query, Project.user_id == user_query.c.user_id)
                .offset((int(page_num) - 1) * int(items_per_page))
                .limit(int(items_per_page))
            )
        
        results = query.all()

        json_output = []
        for result in results:
            single_json = json.dumps(result[0], cls=AlchemyEncoder)
            decoded_json = json.loads(single_json)
            decoded_json['current_marketcap'] = result[1]
            decoded_json['username'] = result[3]
            json_output.append(decoded_json)
        
        count_query = (
                db.session.query(Project, pair_query.c, user_query.c)
                .filter(search_clause)
                .order_by(order_clause)
                .outerjoin(pair_query, Project.pair_address == pair_query.c.pair_address)
                .outerjoin(user_query, Project.user_id == user_query.c.user_id)
            )
        
        all_project_count = count_query.count()
        
        print(all_project_count)
        
        return_data = {
            "total_count": all_project_count,
            "projects": json_output
        }

        return return_data
    
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

        projects = Project.query.filter_by(token=token).filter_by(pair_address=pair_address).all()
        
        for project in projects:
            project.ath = ath
            project.status = status
            db.session.commit()

        return "return_data"