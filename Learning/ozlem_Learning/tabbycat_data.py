import requests
import os
import discord
from dotenv import load_dotenv
import json
import mysql.connector
import csv


load_dotenv()

mydb = mysql.connector.connect(
    host="localhost",
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    database="debates")

mycursor = mydb.cursor()

round = 1
url_part = f'https://kutab.herokuapp.com/api/v1/tournaments/bp88team/rounds/{round}/pairings'

headers = {"Authorization": os.getenv("TOKEN") } 
result = requests.get(url_part, headers = headers).json()
teamid_list = []
id_list = []
teamdict = {}
adj_dict = {}


#print(result)

#the code that gives team ids in a venue as a dictionary
i=0
for x in result:

   for y in range(4):
      string = (result[i].get("teams")[y].get("team"))
      teamid_list.append(string.split('/')[-1])
   ven = x.get("venue")
   ven_id = ven.split('/')[-1]
   teamdict[ven_id] = teamid_list[0:4]
   teamid_list.clear()
   i +=1
#print(teamdict)
print("--------------------------")
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
   adj_dict[ven_id] = id_list[0:len(id_list)]
   id_list.clear()
   j +=1
#print(adj_dict)

#mycursor.execute("SELECT email FROM Participants WHERE id=18")

mails_list = []

#the code that crate a dictionary of adjudicators mails in each room
for d in adj_dict:

   for e in range(len(adj_dict[d])):
      sql = "SELECT email FROM Participants WHERE id = %s"
      val = (adj_dict[d][e],)
      mycursor.execute(sql,val)
      result = mycursor.fetchall()
      mails_list.extend(result)
   adj_dict[d] = mails_list[0: len(mails_list)]
   mails_list.clear()

#the code that create a dictionary of speakers mails in each room
for d in teamdict:

   for e in range(len(teamdict[d])):
      sql = "SELECT email FROM Participants WHERE team_id = %s"
      val = (teamdict[d][e],)
      mycursor.execute(sql,val) 
      result = mycursor.fetchall()
      mails_list.extend(result)
   teamdict[d] = mails_list[0: len(mails_list)]
   mails_list.clear()
 
#the code that merge two dictionaries
final_dict = teamdict.copy()
for x in final_dict:
   final_dict[x] = teamdict[x] + adj_dict[x]
#print(final_dict)
#print("---------------")

#the code that sort final_dict
sorted_dict={}

for i in sorted (final_dict) : 
   sorted_dict[i]=final_dict[i]

#print(sorted_dict)

#the code that creates csv files
venue_number=len(sorted_dict.keys())
countr = 0
csvval1=csv.writer(open("csvfile1.csv","w"))
csvval2=csv.writer(open("csvfile2.csv","w"))
room=[]
csvval1.writerow(['Pre-assign Room Name'] + ['Email Address'])
csvval2.writerow(['Pre-assign Room Name'] + ['Email Address'])
for x,y in sorted_dict.items():
   sql = "SELECT VenueName from Venues WHERE VenueID = %s"
   val = (int(x),)
   mycursor.execute(sql,val)
   venue_tup = mycursor.fetchall()
   venue_name = str(venue_tup[0][0])
   room.append(venue_name)
   for a in y:  
      parts=str(a)   
      room.append(parts[2:-3])

      if countr<=(venue_number/2) :
         csvval1.writerows([room])
      else:
         csvval2.writerows([room])
      room.clear()
   countr += 1
   









      





