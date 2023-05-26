from db import db

class Group(db.Model):
    __tablename__ = 'groups'

    no = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=True)
    link = db.Column(db.String(80), unique=True, nullable=True)
    group_id = db.Column(db.String(80), unique=True)

    def __repr__(self):
        return '<Group %r>' % self.title

class GroupUser(db.Model):
    __tablename__ = 'group_users'

    no = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.String(80))
    user_id = db.Column(db.String(80))

    def __repr__(self):
        return '<GUser %r>' % self.group_id