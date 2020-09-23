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

sql = "Select name, channel_type, type, id from private_rooms where name = %s or name = %s "
val = ("Dorwini2on", "3Dorwinion DG")
mycursor.execute(sql,val)
print("row count",mycursor.rowcount)

# sql = "select team from participants where  name = 'independent' "
# mycursor.execute(sql)
# sql = "select name, institution from participants where unique_id = %s"
# val = ("817485",)
# mycursor.execute(sql, val)
myresult= mycursor.fetchall()
for x in myresult:
    print("Ses")
    print(x)
