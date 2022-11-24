from db import db


class WoodModel(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    length = db.Column(db.Float(precision=2), nullable=False)
    width = db.Column(db.Float(precision=2), nullable=False)
    height = db.Column(db.Float(precision=2), nullable=False)
    weight = db.Column(db.Float(precision=2), nullable=False)
    density = db.Column(db.Float(precision=2), nullable=False)
    timestamp = db.Column(db.String, nullable=False)
    color = db.Column(db.String(80), nullable=False)

