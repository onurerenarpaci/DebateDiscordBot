import mysql.connector
import os, requests, sys
from dotenv import load_dotenv

load_dotenv()

header = {"Authorization": os.getenv("TOKEN") }
mydb = mysql.connector.connect(
  host="localhost",
  user="onur",
  password="koc2020",
  database="firstdatabase"
)

mycursor = mydb.cursor()

mycursor.execute("CREATE TABLE Venues (VenueID INT, VenueName VARCHAR(64))")
url_venues = "https://kutab.herokuapp.com/api/v1/tournaments/bp88team/venues"
venue_list = requests.get(url_venues, headers = header).json()
venue = ()
venues = []
for x in venue_list:
    venue = (x["id"], x["name"])
    venues.append(venue)

sql = "INSERT INTO Venues (VenueID, VenueName) VALUES (%s, %s)"

mycursor.executemany(sql, venues)
mydb.commit()
print(mycursor.rowcount," venues was inserted.")

