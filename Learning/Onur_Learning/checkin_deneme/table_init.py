import mysql.connector
import os, requests, sys
from dotenv import load_dotenv

load_dotenv()

headers = {"Authorization" : "Token 35792636ef40d2194607066b63e49e3ad3a2076c"}
mydb = mysql.connector.connect(
  host="localhost",
  user="onur",
  password="koc2020",
  database="firstdatabase"
)

mycursor = mydb.cursor()    

mycursor.execute("CREATE TABLE Participants (name VARCHAR(64), email VARCHAR(64), role VARCHAR(64) , team VARCHAR(64), team_id VARCHAR(4), institution VARCHAR(64), id INT, url_key VARCHAR(64), checkin BOOLEAN, cut_status BOOLEAN, discord_id VARCHAR(64), unique_id VARCHAR(6)) DEFAULT CHARSET=utf8mb4")

#File names
uniqe_ids_file_name = "unique_ids.txt"
dirname = os.path.dirname(__file__)
f = open(os.path.join(dirname, uniqe_ids_file_name))
unique_ids = f.readlines()
f.close()

def unique_id_generator():
    yield from unique_ids

unique_generator = unique_id_generator()

teams = requests.get("https://kutab.herokuapp.com/api/v1/tournaments/bp88team/teams",headers=headers).json()
instit = requests.get("https://kutab.herokuapp.com/api/v1/institutions", headers=headers).json()

#institutions list
institutions = {}
for x in instit:
   institutions[x["id"]] = x["code"]

#insterting speakers to database
teams_list = []
speakers = []
speaker = ()
for team in teams:
    teams_list.append(team["short_name"])
    for _speaker in team["speakers"]:
        speaker = (_speaker["name"], 
        _speaker["email"],
        "speaker",
        team['short_name'],
        team["id"],
        institutions[int(team["institution"].split("/")[-1])],
        _speaker["id"],
        _speaker["url_key"],
        False,
        False,
        next(unique_generator)[0:-1] )
        print(speaker)
        speakers.append(speaker)

sql = "INSERT INTO Participants (name, email, role, team, team_id, institution, id, url_key, checkin, cut_status, unique_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

mycursor.executemany(sql, speakers)
mydb.commit()
print(mycursor.rowcount," speakers was inserted.")


#insterting adjudicators to database
adjudicators = []
adjudicator = ()

adj_list = requests.get("https://kutab.herokuapp.com/api/v1/tournaments/bp88team/adjudicators",headers=headers).json()

for adj in adj_list:
    adjudicator = (adj["name"],
    adj["email"],
    "jury",
    institutions[int(adj["institution"].split('/')[-1])],
    adj["id"],
    adj["url_key"],
    False,
    False,
    next(unique_generator)[0:-1])
    print(adjudicator)
    adjudicators.append(adjudicator)

sql = "INSERT INTO Participants (name, email, role, institution, id, url_key, checkin, cut_status, unique_id ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"

mycursor.executemany(sql, adjudicators)
mydb.commit()
print(mycursor.rowcount," juries was inserted.")