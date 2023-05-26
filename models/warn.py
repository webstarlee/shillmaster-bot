from db import db

class Warn(db.Model):
    __tablename__ = 'warns'

    no = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(80))
    group_id = db.Column(db.String(80))
    count = db.Column(db.Integer, default=1)

    def __repr__(self):
        return '<Warn %r: %r>' % self.user_id, self.group_id