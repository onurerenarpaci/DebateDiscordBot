import requests

url = "https://kutab.herokuapp.com/api/v1/tournaments/bp88team/speakers"
headers = {"Authorization" : "Token 35792636ef40d2194607066b63e49e3ad3a2076c"}

result = requests.get(url, headers=headers)

print(result.json())