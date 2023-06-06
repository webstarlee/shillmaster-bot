from bson import json_util
import json
from flask_restful import Resource, reqparse
from flask import jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from util.logz import create_logger
from db import admins_collection
from werkzeug.security import generate_password_hash, check_password_hash
from util.parse_json import parse_json

class Info(Resource):
    def __init__(self):
        self.logger = create_logger()

    @jwt_required()  # Requires dat token
    def get(self):
        current_user = get_jwt_identity()
        return jsonify(
            _id=current_user["_id"]["$oid"],
            fullname=current_user["fullname"],
            username=current_user["username"],
            user_id=current_user["user_id"],
        )

class SignIn(Resource):
    def __init__(self):
        self.logger = create_logger()

    parser = reqparse.RequestParser()
    parser.add_argument('username', type=str, required=True, help='This field cannot be left blank')
    parser.add_argument('password', type=str, required=True, help='This field cannot be left blank')

    def post(self):
        data = SignIn.parser.parse_args()
        username = data['username']
        password = data['password']

        user = parse_json(admins_collection.find_one({"username": username}))
        if not user or not check_password_hash(user['password'], password):
            return {'message': 'Wrong username or password.'}, 401
        
        access_token = create_access_token(identity=user)
        print(access_token)
        return_user = {
            "fullname": user["fullname"],
            "username": user["username"],
            "user_id": user["user_id"],
            "token": access_token
        }
        return jsonify(return_user)