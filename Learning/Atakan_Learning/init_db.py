import mysql.connector
import os, requests, sys, csv
from dotenv import load_dotenv
import discord


load_dotenv()

headers = {"Authorization": os.getenv("TABBYCAT_TOKEN")}
mydb = mysql.connector.connect(
    host="localhost",
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    database="debate")

mycursor = mydb.cursor()    

mycursor.execute("CREATE TABLE Participants (name VARCHAR(64), email VARCHAR(64), role VARCHAR(64) , team VARCHAR(64), team_id INT, institution VARCHAR(64), id INT, url_key VARCHAR(64), checkin BOOLEAN, cut_status BOOLEAN, discord_id BIGINT UNSIGNED, unique_id VARCHAR(6)) DEFAULT CHARSET=utf8mb4")

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
        institutions[int(team["institution"].split("/")[-1])] if team["institution"] != None else "Independent",
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
    institutions[int(adj["institution"].split('/')[-1])] if adj["institution"] != None else "Independent",
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


#initilazing private rooms
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv("DISCORD_GUILD")
client = discord.Client()


mycursor.execute("CREATE TABLE Private_rooms (name VARCHAR(64), channel_type VARCHAR(64), type VARCHAR(64), id BIGINT UNSIGNED) DEFAULT CHARSET=utf8mb4")


@client.event
async def on_ready():
    print(f"{client.user} has connected to Discord!")
    guild = discord.utils.get(client.guilds, name=GUILD)

    instit_category = await guild.create_category("Özel Oda 1")
    prep_category = await guild.create_category("Çalışma Odası 1")
    
    text_channel_row = ()
    voice_channel_row = ()
    instit_room_ids = []
    
    room_count = 1 
    i = 0
    
    for _, ins in institutions.items():
        text_channel = await instit_category.create_text_channel(ins+"-sohbet")
        voice_channel = await instit_category.create_voice_channel(ins+" Ses Kanalı")
        text_channel_row = (ins, "text_channel", "institution", text_channel.id)
        voice_channel_row = (ins, "voice_channel", "institution", voice_channel.id)
        instit_room_ids.append(text_channel_row)
        instit_room_ids.append(voice_channel_row)
        i = i+2
        if i % 50 == 0:
            room_count += 1 
            instit_category = await guild.create_category(f"Özel Oda {room_count}")

    sql = "INSERT INTO Private_rooms (name, channel_type, type, id) VALUES (%s, %s, %s, %s)"
    mycursor.executemany(sql, instit_room_ids)
    print(mycursor.rowcount," institution private channels was inserted.")
    mydb.commit()
    

    team_room_ids = [] 
    room_count = 1
    i = 0

    for team in teams_list:
        voice_channel = await prep_category.create_voice_channel(team+" Ses Kanalı")
        voice_channel_row = (team, "voice_channel", "team", voice_channel.id)
        team_room_ids.append(voice_channel_row)
        i = i+1
        if i % 50 == 0:
            room_count += 1
            prep_category = await guild.create_category(f"Çalışma Odası {room_count}")

    sql = "INSERT INTO Private_rooms (name, channel_type, type, id) VALUES (%s, %s, %s, %s)"
    mycursor.executemany(sql, team_room_ids)
    print(mycursor.rowcount," team private channels was inserted.")
    mydb.commit()

        
        
        

    

client.run(TOKEN)


