from db import db

class User(db.Model):
    __tablename__ = 'users'

    no = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(80), nullable=True)
    username = db.Column(db.String(80), unique=True)
    user_id = db.Column(db.String(80), unique=True)