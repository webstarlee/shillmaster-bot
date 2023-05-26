from db import db

class Setting(db.Model):
    __tablename__ = 'settings'

    no = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.String(80), default="global")
    top_users = db.Column(db.PickleType, nullable=True)
    shill_mode = db.Column(db.Boolean, default=False, nullable=False)
    ban_mode = db.Column(db.Boolean, default=False, nullable=False)

    def __repr__(self):
        return '<Setting %r>' % self.group_id