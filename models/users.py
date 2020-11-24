import datetime
import uuid

from flask import session

from common.database import Database


class User(object):
    def __init__(self, email, username, name, password, balance = 0, _id=None):
        self.email = email
        self.username = username
        self.name = name
        self.password = password
        self.balance = balance
        self._id = uuid.uuid4().hex if _id is None else _id

    @classmethod
    def get_by_email(cls, email):
        data = Database.find_one("users", {"email": email})
        if data is not None:
            return cls(**data)

    @classmethod
    def get_by_id(cls, _id):
        data = Database.find_one("users", {"_id": _id})
        if data is not None:
            return cls(**data)

    @staticmethod
    def get_balance(username):
        data = Database.find_one("users", {"username": username})
        return data["balance"]

    @staticmethod
    def add_funds(username, amount):
        Database.DATABASE["users"].update_one({"username": username}, {'$inc': {'balance': amount}})

    @staticmethod
    def remove_funds(username, amount):
        Database.DATABASE["users"].update_one({"username": username}, {'$inc': {'balance': -amount}})

    @staticmethod
    def login_valid(email, password):
        user = User.get_by_email(email)
        if user is not None:
            if user.password == password:
                return user.password == password
            else:
                return False
        else:
            return False

    @classmethod
    def register(cls, email, username, name, password):
        user = User.get_by_email(email)
        if user is None:
            new_user = cls(email, username, name, password)
            new_user.save_to_mongo()
            session['email'] = email
        else:
            return False

    @staticmethod
    def login(user_email):
        session['email'] = user_email

    @staticmethod
    def logout():
        session['email'] = None

    def json(self):
        return {
            "email": self.email,
            "username": self.username,
            "name": self.name,
            "password": self.password,
            "balance": self.balance,
            "_id": self._id
        }

    def save_to_mongo(self):
        Database.insert("users", self.json())
