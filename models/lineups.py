import uuid
import datetime

from common.database import Database
from models.contests import Contest
from models.events_golf import Event_Golf


class Lineup(object):
    def __init__(self, Contest_Id, Username, Golfer_1, Golfer_2, Golfer_3, Golfer_4, Golfer_5, Tiebreak, _id=None):
        self.Golfer_1 = Golfer_1
        self.Golfer_2 = Golfer_2
        self.Golfer_3 = Golfer_3
        self.Golfer_4 = Golfer_4
        self.Golfer_5 = Golfer_5
        self.Tiebreak = Tiebreak
        self.Contest_Id = Contest_Id
        self.Contest_Name = Contest.get_contest_name(Contest_Id)
        self.Start_Date = Event_Golf.find_event_date(Contest.get_event_id(Contest_Id)).date()
        self.End_Date = Event_Golf.find_event_enddate(Contest.get_event_id(Contest_Id)).date()
        self.Username = Username
        self.Score = Lineup.score_lineup(self.Golfer_1,self.Golfer_2,self.Golfer_3, self.Golfer_4,self.Golfer_5,self.Contest_Id)
        self._id = uuid.uuid4().hex if _id is None else _id

    def json(self):
        return {
            "_id": self._id,
            "Golfer_1": self.Golfer_1,
            "Golfer_2": self.Golfer_2,
            "Golfer_3": self.Golfer_3,
            "Golfer_4": self.Golfer_4,
            "Golfer_5": self.Golfer_5,
            "Tiebreak": self.Tiebreak,
            "Contest_Id": self.Contest_Id,
            "Username": self.Username,
        }

    def save_to_mongo(self):
        Database.insert("lineups_golf", self.json())

    @staticmethod
    def delete_lineup(id):
        Database.delete_one("lineups_golf", {"_id": id})

    @staticmethod
    def update_lineup(id, Golfer_1, Golfer_2, Golfer_3, Golfer_4, Golfer_5, Tiebreak):
        new = {"$set": {"Golfer_1": Golfer_1,
                        "Golfer_2": Golfer_2,
                        "Golfer_3": Golfer_3,
                        "Golfer_4": Golfer_4,
                        "Golfer_5": Golfer_5,
                        "Tiebreak": Tiebreak}}
        Database.update_one("lineups_golf", {"_id": id}, new)

    @classmethod
    def create_lineup(cls, Contest_Id, Username, Golfer_1, Golfer_2, Golfer_3, Golfer_4, Golfer_5, Tiebreak):
        new_lineup = cls(Contest_Id, Username, Golfer_1, Golfer_2, Golfer_3, Golfer_4, Golfer_5, Tiebreak)
        new_lineup.save_to_mongo()

    @staticmethod
    def validate_lineup(Golfer_1, Golfer_2, Golfer_3, Golfer_4, Golfer_5):
        if ((Golfer_1 == Golfer_2) or
                (Golfer_1 == Golfer_3) or
                (Golfer_1 == Golfer_3) or
                (Golfer_1 == Golfer_4) or
                (Golfer_1 == Golfer_5) or
                (Golfer_2 == Golfer_3) or
                (Golfer_2 == Golfer_4) or
                (Golfer_2 == Golfer_5) or
                (Golfer_3 == Golfer_4) or
                (Golfer_3 == Golfer_5) or
                (Golfer_4 == Golfer_5)):
            return False
        else:
            return True

    @classmethod
    def get_entries(cls, contest_id):
        lineups = Database.find(collection="lineups_golf", query={"Contest_Id": contest_id})
        return [cls(**lineup) for lineup in lineups]

    @classmethod
    def get_contests_username(cls, username):
        lineups = Database.find(collection="lineups_golf", query={"Username": username})
        return [cls(**lineup) for lineup in lineups]

    @classmethod
    def get_lineup(cls, _id):
        lineups = Database.find(collection="lineups_golf", query={"_id": _id})
        return [cls(**lineup) for lineup in lineups]

    @staticmethod
    def score_lineup(Golfer_1, Golfer_2, Golfer_3, Golfer_4, Golfer_5, Contest_id):
        event_id = Contest.get_event_id(Contest_id)
        if Event_Golf.find_event_date(event_id).date() > datetime.date.today():
            total_score = 0
        else:
            golfer_1_id = Database.find_one('players_golf', query={'Golfer_Name': Golfer_1})
            golfer_1_id = golfer_1_id["Golfer_Id"]
            score_1 = Database.find_one("scores_golf", query={'Event_Id' : event_id,
                                                             'id' : golfer_1_id})
            if score_1 is not None:
                score_1 = score_1["score"]
            else:
                score_1 = 100

            golfer_2_id = Database.find_one('players_golf', query={'Golfer_Name': Golfer_2})
            golfer_2_id = golfer_2_id["Golfer_Id"]
            score_2 = Database.find_one("scores_golf", query={'Event_Id' : event_id,
                                                             'id' : golfer_2_id})
            if score_2 is not None:
                score_2 = score_2["score"]
            else:
                score_2 = 100

            golfer_3_id = Database.find_one('players_golf', query={'Golfer_Name': Golfer_3})
            golfer_3_id = golfer_3_id["Golfer_Id"]
            score_3 = Database.find_one("scores_golf", query={'Event_Id' : event_id,
                                                             'id' : golfer_3_id})
            if score_3 is not None:
                score_3 = score_3["score"]
            else:
                score_3 = 100

            golfer_4_id = Database.find_one('players_golf', query={'Golfer_Name': Golfer_4})
            golfer_4_id = golfer_4_id["Golfer_Id"]
            score_4 = Database.find_one("scores_golf", query={'Event_Id' : event_id,
                                                             'id' : golfer_4_id})
            if score_4 is not None:
                score_4 = score_4["score"]
            else:
                score_4 = 100

            golfer_5_id = Database.find_one('players_golf', query={'Golfer_Name': Golfer_5})
            golfer_5_id = golfer_5_id["Golfer_Id"]
            score_5 = Database.find_one("scores_golf", query={'Event_Id' : event_id,
                                                             'id' : golfer_5_id})
            if score_5 is not None:
                score_5 = score_5["score"]
            else:
                score_5 = 100
            total_score = score_1 + score_2 + score_3 + score_4 + score_5
        return total_score
