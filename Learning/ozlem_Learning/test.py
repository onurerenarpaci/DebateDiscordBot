import os
import random
from dotenv import load_dotenv
from discord.ext import commands
import mysql.connector
import requests

load_dotenv()
mydb = mysql.connector.connect(
  host="localhost",
  user=os.getenv("MYSQL_USER"),
  password=os.getenv("MYSQL_PASSWORD"),
  database="debates")

mycursor = mydb.cursor()

sql = "SELECT name, team FROM Participants WHERE discord_id = %s"
val = (693078237756129321,)
mycursor.execute(sql,val)
debater = mycursor.fetchone()

print(debater[0])
#print(debater_team)


