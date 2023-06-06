from db import db

class Task(db.Model):
    __tablename__ = 'tasks'

    no = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(80)) #ban, unban
    user_id = db.Column(db.String(80), nullable=True)
    group_id = db.Column(db.String(80), nullable=True)