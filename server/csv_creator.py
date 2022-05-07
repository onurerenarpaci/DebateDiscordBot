import requests
import os
import discord
from dotenv import load_dotenv
import json
import mysql.connector
import csv
import math

load_dotenv()

mydb = mysql.connector.connect(
	host="localhost",
	user=os.getenv("MYSQL_USER"),
	password=os.getenv("MYSQL_PASSWORD"),
	database="##################")

mycursor = mydb.cursor()
tabbyurl = os.getenv("URL")
tournament = os.getenv("TOURNAMENT")

zoom_list = ["https://##################", "https://##################", "https://##################"]

round = int(input('Enter round number: '))
url_part = f'{tabbyurl}/api/v1/tournaments/{tournament}/rounds/{round}/pairings'

headers = {"Authorization": os.getenv("TABBYCAT_TOKEN") } 
result = requests.get(url_part, headers = headers).json()
teamid_list = []
id_list = []
teamdict = {}
adj_dict = {}


#the code that gives team ids in a venue as a dictionary
i=0
for x in result:

	for y in range(4):
		string = (result[i].get("teams")[y].get("team"))
		teamid_list.append(string.split('/')[-1])
	ven = x.get("venue")
	ven_id = ven.split('/')[-1]
	teamdict[ven_id] = teamid_list.copy()
	teamid_list.clear()
	i +=1

#the code that gives personal ids of adjudicators in a venue as a dictionary
j=0
for a in result:
	chair_url = result[j].get("adjudicators").get("chair")
	id_list.append(chair_url.split('/')[-1])
	for b in (result[j].get("adjudicators").get("panellists")):
		id_list.append(b.split('/')[-1])
	for c in (result[j].get("adjudicators").get("trainees")):
		id_list.append(c.split('/')[-1])
	ven = a.get("venue")
	ven_id = ven.split('/')[-1]
	adj_dict[ven_id] = id_list.copy()
	id_list.clear()
	j +=1

mails_list = []

#the code that crate a dictionary of adjudicators mails in each room
for d in adj_dict:

	for e in range(len(adj_dict[d])):
		sql = "SELECT email FROM Participants WHERE id = %s"
		val = (adj_dict[d][e],)
		mycursor.execute(sql,val)
		result = mycursor.fetchall()
		mails_list.extend(result[0])
	adj_dict[d] = mails_list.copy()
	mails_list.clear()

#the code that create a dictionary of speakers mails in each room
for d in teamdict:

	for e in range(len(teamdict[d])):
		sql = "SELECT email FROM Participants WHERE team_id = %s"
		val = (teamdict[d][e],)
		mycursor.execute(sql,val) 
		result = mycursor.fetchall()
		mails_list.extend(x[0] for x in result)
	teamdict[d] = mails_list.copy()
	mails_list.clear()

#the code that merge two dictionaries
final_dict = teamdict.copy()
for x in final_dict:
	final_dict[x] = teamdict[x] + adj_dict[x]


#the code that sort final_dict
venue_links={}

for i in sorted(final_dict) : 
	venue_links[i]=final_dict[i]

print(venue_links)

#the code that creates csv files
venue_number=len(venue_links.keys())
countr = 0
csvlist = []
zoomnumber = math.ceil(len(venue_links)/8)
for x in range(zoomnumber):
	csvlist.append(csv.writer(open(f"csvfile{x+1}.csv","w")))


for x in csvlist:
	x.writerow(['Pre-assign Room Name','Email Address'])


venue_id_list = list(venue_links.keys()).copy()

for x in range(zoomnumber):
	for a in venue_id_list[8*x:8*x+8]:
		sql = "SELECT VenueName from Venues WHERE VenueID = %s"
		val = (int(a),)
		mycursor.execute(sql,val)
		venue_tup = mycursor.fetchall()
		venue_name = str(venue_tup[0][0])

		sql = "UPDATE Venues SET zoom_link = %s WHERE VenueID = %s"
		val = (zoom_list[x],int(a))
		mycursor.execute(sql,val)
		mydb.commit()

		for email in venue_links[a]:
			csvlist[x].writerow([venue_name, email])
