import http.client
import json
import pandas as pd

##import pymongo

##URI = "mongodb://127.0.0.1:27017"
URI = "mongodb+srv://admin:QXqzybmY39mXjJQ5@cluster0.mljvh.mongodb.net/simplefantasy?authSource=admin"
DATABASE = None

##client = pymongo.MongoClient(URI)
##DATABASE = client["simplefantasy"]

conn = http.client.HTTPSConnection("api.sportradar.us")

a = "/golf/trial/pga/v3/en/2022/tournaments/schedule.json?api_key=nqgmtaevy5r3eb8haq6jwzqh"
b = "/leaderboard.json?api_key=nqgmtaevy5r3eb8haq6jwzqh"
conn.request("GET", a)


res = conn.getresponse()
data = res.read()
data = (data.decode("utf-8"))
data = json.loads(data)

data = data["tournaments"]
tourneys = pd.DataFrame.from_dict(data)
tourneys = tourneys[tourneys["event_type"] == "stroke"]
tourneys = tourneys[["id","name","start_date","end_date","venue"]]
venues = tourneys["venue"]
venues = venues.to_dict()
venues = pd.DataFrame.from_dict(venues).transpose()
venues = venues[["name"]]
venues = venues.rename(columns={"name": "Course"})
tourneys = tourneys.rename(columns={"id": "event_id","name":"Event","start_date":"Start_Date","end_date":"End_Date"})
tourneys = tourneys[["event_id","Event","Start_Date","End_Date"]]
tourneys['Course'] = venues['Course'].values

