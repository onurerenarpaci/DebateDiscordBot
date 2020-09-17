import requests
import os
import discord
from dotenv import load_dotenv
import json


load_dotenv()


url_part = "https://kutab.herokuapp.com/api/v1/tournaments/bp88team/rounds/1/pairings"
url_venues = "https://kutab.herokuapp.com/api/v1/tournaments/bp88team/venues"
header = {"Authorization": os.getenv("TOKEN") } 

teamid_list = []
thisdict = {}

venues = requests.get(url_venues, headers = header)
CREATE VenueTable(
   VenueID
   VenueName
)
for x in venues:
   venue_id = x.get("id")
   venue_name = x.get("name")
   INSERT INTO VenueTable(VenueID, VenueName)
   VALUES(venue_id,venue_name)

result = requests.get(url_part, headers = header).json()
i=0
for x in result:
   
   for y in range(4):
      string = (result[i].get("teams")[y].get("team"))
      teamid_list.append(string.split('/')[-1])
   thisdict[x.get('id')] = teamid_list[0:4]
   teamid_list.clear()
   i +=1


print(thisdict)


