createDataBase = "CREATE DATABASE firstdatabase"

showDataBases = "SHOW DATABASES"

createTable = "CREATE TABLE Speakers ( SpeakerId int NOT NULL AUTO_INCREMENT, Name varchar(255) NOT NULL, email varchar(255), url_key varchar(255), PRIMARY KEY (SpeakerId))"

showTables = "SHOW TABLES"

insertInto = "INSERT INTO Speakers (Name, email, url_key) VALUES (%s, %s, %s)"

deleteAll = "DELETE FROM Speakers"

