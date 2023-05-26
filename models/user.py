from db import db

class User(db.Model):
    __tablename__ = 'users'

    no = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(80), nullable=True)
    username = db.Column(db.String(80), unique=True)
    user_id = db.Column(db.String(80), unique=True)

    def __init__(self, username, fullname, user_id):
        self.username = username
        self.fullname = fullname
        self.user_id = user_id

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return '<User %r>' % self.username

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_user_id(cls, user_id):
        return cls.query.filter_by(user_id=user_id).first()