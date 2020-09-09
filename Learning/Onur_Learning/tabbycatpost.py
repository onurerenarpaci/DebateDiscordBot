import requests
import json

url = "https://kutab.herokuapp.com/api/v1/tournaments/bp88team/rounds/1/pairings"
url2 = "https://kutab.herokuapp.com/api/v1/tournaments/bp88team/teams/8"
headers = {"Authorization" : "Token 35792636ef40d2194607066b63e49e3ad3a2076c"}
data = {  
  "name": "Özlem Şerifoğulları",
  "email": "ozlemserifogullari@gmail.com",
  "anonymous": False,
  "categories": []}

data_json = json.dumps(data)

result = requests.get(url2, headers=headers)

print(result.json())