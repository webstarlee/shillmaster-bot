import db
from flask_restful import Resource
from flask import jsonify
from flask_jwt_extended import jwt_required
from util.logz import create_logger
from util.parse_json import parse_json

class GetLeaderBoards(Resource):
    def __init__(self):
        self.logger = create_logger()

    @jwt_required()  # Requires dat token
    def get(self):
        raw_leader_boards = db.LeaderBoard.find()
        leader_boards = []
        for leader_board in raw_leader_boards:
            leader_boards.append({
                "_id": str(leader_board["_id"]),
                "type": leader_board["type"],
                "chat_id": leader_board["chat_id"],
                "message_id": leader_board["message_id"],
                "text": leader_board["text"]
            })
        return parse_json(leader_boards)