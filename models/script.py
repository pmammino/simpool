import http.client
import json
import pandas as pd

from src.common.database import Database
Database.initialize()
conn = http.client.HTTPSConnection("api.sportradar.us")

a = "/golf-t2/leaderboard/pga/2020/tournaments/"
b = "/leaderboard.json?api_key=nqgmtaevy5r3eb8haq6jwzqh"
conn.request("GET",
             a + "97b4fe0b-a804-418e-91c3-165ef91f4eb6" + b)

res = conn.getresponse()
data = res.read()
data = (data.decode("utf-8"))
data = json.loads(data)
data = data["leaderboard"]
stats = pd.DataFrame.from_dict(data)
stats['Event_Id'] = '97b4fe0b-a804-418e-91c3-165ef91f4eb6'
Database.insert_many("scores_golf", stats.to_dict('records'))
