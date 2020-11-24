
import uuid

from common.database import Database


class Event_Golf(object):
    def __init__(self, event_id, date, event, course, _id=None):
        self.Event_id = event_id
        self.Date = date
        self.Event = event
        self.Course = course
        self._id = uuid.uuid4().hex if _id is None else _id

    def json(self):
        return {
            "_id": self._id,
            "event_id": self.Event_id,
            "Start_Date": self.Start_Date,
            "End_Date": self.End_Date,
            "Course": self.Course
        }

    @staticmethod
    def find_event_course(event_id):
        event_data = Database.find_one('events_golf', query={'event_id': event_id})
        return event_data["Course"]

    @staticmethod
    def find_event_date(event_id):
        event_data = Database.find_one('events_golf', query={'event_id': event_id})
        return event_data["Start_Date"]

    @staticmethod
    def find_event_enddate(event_id):
        event_data = Database.find_one('events_golf', query={'event_id': event_id})
        return event_data["End_Date"]

