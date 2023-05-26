from db import db
from datetime import datetime

class Pair(db.Model):
    __tablename__ = 'pairs'

    no = db.Column(db.Integer, primary_key=True)
    chain = db.Column(db.String(80), nullable=False)
    token = db.Column(db.String(80), nullable=False)
    symbol = db.Column(db.String(80), nullable=False)
    pair_address = db.Column(db.String(80), nullable=False, unique=True)
    pair_url = db.Column(db.String(250), nullable=False)
    marketcap = db.Column(db.String(80), nullable=False)
    status = db.Column(db.String(80), default="active")
    updated_at = db.Column(db.DateTime(), default=datetime.utcnow)

    def __repr__(self):
        return '<Pair %r>' % self.symbol