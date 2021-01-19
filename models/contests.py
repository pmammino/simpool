import datetime
import uuid

from common.database import Database
from models.events_golf import Event_Golf


class Contest(object):
    def __init__(self, Contest_Id, Sport, Contest_Name, Event_ID, Buy_In,Payout_Type, _id = None):
        self.Contest_Id = Contest_Id
        self.Sport = Sport
        self.Contest_Name = Contest_Name
        self.Event_ID = Event_ID
        self.Buy_In = Buy_In
        self.Payout_Type = Payout_Type
        self.Course = Event_Golf.find_event_course(Event_ID)
        self.Start_Date = Event_Golf.find_event_date(Event_ID).date()
        self.End_Date = Event_Golf.find_event_enddate(Event_ID).date()
        self._id = uuid.uuid4().hex if _id is None else _id


    def json(self):
        return {
            "_id": self._id,
            "Contest_Id": self.Contest_Id,
            "Sport": self.Sport,
            "Contest_Name": self.Contest_Name,
            "Event_ID": self.Event_ID,
            "Buy_In": self.Buy_In,
            "Payout_Type": self.Payout_Type
        }

    @classmethod
    def get_from_mongo(cls, contest_id):
        contest_data = Database.find_one('contests', query={'Contest_Id': contest_id})
        return cls(**contest_data)

    @staticmethod
    def get_contest_name(contest_id):
        contest_data = Database.find_one('contests', query={'Contest_Id': contest_id})
        return contest_data["Contest_Name"]

    @staticmethod
    def get_contest_buyin(contest_id):
        contest_data = Database.find_one('contests', query={'Contest_Id': contest_id})
        return contest_data["Buy_In"]

    @staticmethod
    def get_event_id(contest_id):
        contest_data = Database.find_one('contests', query={'Contest_Id': contest_id})
        return contest_data["Event_ID"]


    @classmethod
    def find_by_sport(cls, sport):
        contests = Database.find(collection="contests", query={"Sport": sport})
        return [cls(**contest) for contest in contests]

    @classmethod
    def find_event(cls, event_id):
        event_data = Database.find_one('events_golf', query={'event_id': event_id})
        return cls(**event_data)

