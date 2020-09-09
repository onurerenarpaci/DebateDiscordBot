import mysql.connector
import os, requests, sys
from dotenv import load_dotenv

load_dotenv()

headers = {"Authorization": os.getenv("TABBYCAT_TOKEN")}
mydb = mysql.connector.connect(
    host="localhost",
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    database="munazara")

mycursor = mydb.cursor()

mycursor.execute("CREATE TABLE speakers (name VARCHAR(64), email VARCHAR(64), team VARCHAR(64), institution VARCHAR(64), id INT, url_key VARCHAR(64), checkin BOOLEAN, discord_id VARCHAR(64), unique_id VARCHAR(8))")

f = open("unique_ids.txt","r")
unique_ids = f.readlines()
f.close()

def unique_id_generator():
    yield from unique_ids

unique_generator = unique_id_generator()

teams = requests.get("https://kutab.herokuapp.com/api/v1/tournaments/bp88team/teams",headers=headers).json()
instit = requests.get("https://kutab.herokuapp.com/api/v1/institutions", headers=headers).json()

institutions = {}
for x in instit:
   institutions[x["id"]] = x["code"]

speakers = []
speaker = ()
for team in teams:
    for _speaker in team["speakers"]:
        speaker = (_speaker["name"], 
        _speaker["email"],
        team['short_name'],
        institutions[int(team["institution"].split("/")[-1])],
        _speaker["id"],
        _speaker["url_key"],
        False,
        "NULL",
        next(unique_generator)[0:-1] )
        print(speaker)
        speakers.append(speaker)

sql = "INSERT INTO speakers (name, email, team, institution, id, url_key, checkin, discord_id, unique_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"

mycursor.executemany(sql, speakers)
mydb.commit()
print(mycursor.rowcount," was inserted.")