from db import db
from werkzeug.security import generate_password_hash, check_password_hash


class Admin(db.Model):
    __tablename__ = 'admins'

    no = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(80))
    username = db.Column(db.String(80), unique=True)
    user_id = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(250))

    def __init__(self, fullname, username, user_id, password):
        self.fullname = fullname
        self.username = username
        self.user_id = user_id
        self.password = self.hash_password(password)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def hash_password(self, password):
        return generate_password_hash(password)
    
    def __repr__(self):
        return '<Admin %r>' % self.username

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_user_id(cls, user_id):
        return cls.query.filter_by(user_id=user_id).first()