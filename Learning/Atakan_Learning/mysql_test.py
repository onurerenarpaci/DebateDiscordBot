import mysql.connector
import os, requests, sys, csv
from dotenv import load_dotenv

load_dotenv()

headers = {"Authorization": os.getenv("TABBYCAT_TOKEN")}
mydb = mysql.connector.connect(
    host="localhost",
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    database="debate")

mycursor = mydb.cursor()   

# sql = "Select name, channel_type, type, id from private_rooms where name = %s or name = %s "
# val = (, "Independent")
# mycursor.execute(sql, val)

sql = "select team from participants where  name = 'independent' "
mycursor.execute(sql)
myresult= mycursor.fetchall()
for x in myresult:
    print(x[0] == None)
