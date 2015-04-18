from flask_login import UserMixin
from database import db


class User(UserMixin, db.Model):
    __tablename__ = 'user_account'

    id = db.Column('id', db.Integer, primary_key=True)
    name = db.Column('name', db.String)
    password_hash = db.Column('password_hash', db.String)
    role = db.Column('role', db.String)

    @staticmethod
    def get(user_id):
        return User.query.get(user_id)

    @staticmethod
    def save_changes():
        db.session.commit()