import mysql.connector
import sqlcommands

mydb = mysql.connector.connect(
  host="localhost",
  user="onur",
  password="koc2020",
  database="firstdatabase"
)

mycursor = mydb.cursor()

val = ("Onur Eren Arpaci", "oarpaci18@ku.edu.tr")
mycursor.execute(sqlcommands.insertInto, val)

#mycursor.execute(sqlcommands.deleteAll)

mydb.commit()

for x in mycursor:
  print(x)