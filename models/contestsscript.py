from datetime import  datetime,timedelta
import http.client
import json
import pandas as pd
import uuid
import pymongo


from common.database import Database
Database.initialize()

##import pymongo

##URI = "mongodb://127.0.0.1:27017"
URI = "mongodb+srv://admin:s4xWApCtAtFyjUA8@cluster0.mljvh.mongodb.net/simplefantasy?retryWrites=true&w=majority"
DATABASE = None

client = pymongo.MongoClient(URI)
DATABASE = client["simplefantasy"]

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
tourneys = tourneys[["id", "name", "start_date", "end_date", "venue"]]
venues = tourneys["venue"]
venues = venues.to_dict()
venues = pd.DataFrame.from_dict(venues).transpose()
venues = venues[["name"]]
venues = venues.rename(columns={"name": "Course"})
tourneys = tourneys.rename(
    columns={"id": "event_id", "name": "Event", "start_date": "Start_Date", "end_date": "End_Date"})
tourneys = tourneys[["event_id", "Event", "Start_Date", "End_Date"]]
tourneys['Course'] = venues['Course'].values
tourneys['Start_Date'] = pd.to_datetime(tourneys['Start_Date'])
tourneys['End_Date'] = pd.to_datetime(tourneys['End_Date'])

DATABASE["events_golf"].insert_many(tourneys.to_dict('records'))



mask = (tourneys['Start_Date'] > datetime.now()) & (tourneys['Start_Date'] <= datetime.now() + timedelta(days=7))
tourneys = tourneys.loc[mask]

contests = tourneys[["event_id", "Event"]]
contests.reset_index(drop=True, inplace=True)
contests['Sport'] = str('PGA')
contests['Buy_In'] = int(5)
contests["Max_Entries"] = int(1000)
contests['Contest_Name'] = str("Scratch Golfer - ") + contests['Event'].astype(str)
contests['Contest_Id'] = contests.apply(lambda row: uuid.uuid4().hex, axis=1)

contests2 = tourneys[["event_id", "Event"]]
contests2['Sport'] = str('PGA')
contests2['Buy_In'] = int(10)
contests2["Max_Entries"] = int(1000)
contests2['Contest_Name'] = str("On A Dime - ") + contests2['Event'].astype(str)
contests2['Contest_Id'] = contests2.apply(lambda row: uuid.uuid4().hex, axis=1)

contests3 = tourneys[["event_id", "Event"]]
contests3['Sport'] = str('PGA')
contests3['Buy_In'] = int(25)
contests3["Max_Entries"] = int(1000)
contests3['Contest_Name'] = str("Quarter Pounder - ") + contests3['Event'].astype(str)
contests3['Contest_Id'] = contests3.apply(lambda row: uuid.uuid4().hex, axis=1)

frames = [contests, contests2, contests3]

contestsall = pd.concat(frames)

for index, row in contestsall.iterrows():
    DATABASE["contests"].update_one({'Contest_Id': row['Contest_Id']},
                                    {'$set': {"_id": row['Contest_Id'],
                                        "Contest_Id": row['Contest_Id'],
                                        "Sport": row['Sport'],
                                        "Contest_Name": row['Contest_Name'],
                                        "Event_ID": row['event_id'],
                                        "Buy_In": row['Buy_In'],
                                        "Max_Entires": row['Max_Entries']}},
                                    upsert=True)
