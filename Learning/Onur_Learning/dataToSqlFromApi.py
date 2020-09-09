import mysql.connector
import sqlcommands
import requests

url = "https://kutab.herokuapp.com/api/v1/tournaments/bp88team/speakers"
headers = {"Authorization" : "Token 35792636ef40d2194607066b63e49e3ad3a2076c"}

result = requests.get(url, headers=headers).json()

mydb = mysql.connector.connect(
  host="localhost",
  user="onur",
  password="koc2020",
  database="firstdatabase"
)

mycursor = mydb.cursor()

for x in result:
    name = x["name"]
    email = x["email"]
    urlkey = x["url_key"]
    val = (name, email, urlkey)
    mycursor.execute(sqlcommands.insertInto, val)
    mydb.commit()

mycursor.execute("SELECT * FROM Speakers")

myresult = mycursor.fetchall()

for x in myresult:
  print(x)