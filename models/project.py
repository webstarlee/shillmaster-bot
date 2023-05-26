from db import db
from datetime import datetime

class Project(db.Model):
    __tablename__ = 'projects'

    no = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(80), nullable=False)
    group_id = db.Column(db.String(80), nullable=False)
    chain = db.Column(db.String(80), nullable=False)
    token = db.Column(db.String(80), nullable=False)
    symbol = db.Column(db.String(80), nullable=False)
    pair_address = db.Column(db.String(80), nullable=False)
    pair_url = db.Column(db.String(250), nullable=False)
    marketcap = db.Column(db.String(80), nullable=False)
    ath = db.Column(db.String(80), nullable=False)
    status = db.Column(db.String(80), default="active")
    created_at = db.Column(db.DateTime(), default=datetime.utcnow)

    def __repr__(self):
        return '<Project %r>' % self.symbol