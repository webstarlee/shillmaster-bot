from db import db

class Ban(db.Model):
    __tablename__ = 'bans'

    no = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(80))
    group_id = db.Column(db.String(80))

    def __repr__(self):
        return '<Ban %r: %r>' % self.user_id, self.group_id