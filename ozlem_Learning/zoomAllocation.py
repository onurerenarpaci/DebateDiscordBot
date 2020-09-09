import requests

url = "https://kutab.herokuapp.com/api/v1/tournaments/bp88team/rounds/1/pairings"
header = {"Authorization": "Token a11cdf6cbe4ad2d515262f136a5b20d79d3245f3"} 

result = requests.get(url, headers = header)
print(result.json())