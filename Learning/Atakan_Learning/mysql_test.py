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

mycursor.execute("Select MAX(id) from Participants")

myresult= mycursor.fetchone()

print(myresult)
print(type(myresult[0]))

