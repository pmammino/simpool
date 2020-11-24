import uuid

from common.database import Database


class Golfer(object):
    def __init__(self, Golfer_Id, Golfer_Name, _id = None):
        self.Golfer_Id = Golfer_Id
        self.Golfer_Name = Golfer_Name
        self._id = uuid.uuid4().hex if _id is None else _id

    def json(self):
        return {
        "_id" :  self._id,
        "Golfer_Id" : self.Golfer_Id,
        "Golfer_Name" : self.Golfer_Name
        }

    @classmethod
    def find_golfers(cls):
        golfers = Database.find(collection="players_golf", query={})
        return [cls(**golfer) for golfer in golfers]

    def get_name(self):
        return self.Golfer_Name
