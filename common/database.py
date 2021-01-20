import pymongo


class Database(object):
    ##URI = "mongodb://127.0.0.1:27017"
    URI = "mongodb+srv://admin:v7EzRvWi4mKfy9Qq@cluster0.mljvh.mongodb.net/simplefantasy?retryWrites=true&w=majority"
    DATABASE = None

    @staticmethod
    def initialize():
        client = pymongo.MongoClient(Database.URI)
        Database.DATABASE = client["simplefantasy"]

    @staticmethod
    def insert(collection, data):
        Database.DATABASE[collection].insert(data)

    @staticmethod
    def insert_many(collection, data):
        Database.DATABASE[collection].insert_many(data)


    @staticmethod
    def find(collection, query):
        return Database.DATABASE[collection].find(query)

    @staticmethod
    def find_one(collection, query):
        return Database.DATABASE[collection].find_one(query)
