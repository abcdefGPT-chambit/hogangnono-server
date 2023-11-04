from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class AptInfo(db.Model):
    __tablename__ = 'apt_info'
    apt_code = db.Column(db.String(255), primary_key=True)
    apt_name = db.Column(db.String(255))