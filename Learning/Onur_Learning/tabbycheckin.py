import aiohttp
import asyncio

url = "https://kutab.herokuapp.com/api/v1/tournaments/bp88team/speakers/85/checkin"
headers = {"Authorization" : "Token 35792636ef40d2194607066b63e49e3ad3a2076c"}

session = aiohttp.ClientSession()

# async with aiohttp.ClientSession() as session:
#     async with session.put(url, headers=headers) as resp:
#         print(resp.status)
#         print(await resp.text())

async def main():

    #await session.put(url, headers=headers)
    async with session.put(url, headers=headers) as resp:
        print(resp.status)
        print(await resp.text())
    
    await session.close()

loop = asyncio.get_event_loop()
loop.run_until_complete(main())


# import requests



# result = requests.put(url, headers=headers)

# print(result.json())