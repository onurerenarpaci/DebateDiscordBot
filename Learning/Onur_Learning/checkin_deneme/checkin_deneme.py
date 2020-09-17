# bot.py
import os
import asyncio
import discord
import time
from dotenv import load_dotenv
import aiohttp
import tabbyurl
import mysql.connector

mydb = mysql.connector.connect(
	host="localhost",
	user="onur",
	password="koc2020",
	database="firstdatabase"
)

mycursor = mydb.cursor()

channelId = 739551824612294687 #Checkin channel id
checkinStatus = False # True = Open, False = Close
checkinMessage = None
guild = None # discord.utils.get(client.guilds, name=GUILD)
checkinDuration = 1 # 30 minutes

headers = {"Authorization" : "Token 35792636ef40d2194607066b63e49e3ad3a2076c"}

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('GUILD_NAME')

client = discord.Client()

@client.event
async def on_ready():
	global guild
	guild = discord.utils.get(client.guilds, name=GUILD)
	print(
		f'{client.user} has connected to the following guild:\n'
		f'{guild.name}(id: {guild.id})\n'
	)

@client.event
async def on_message(message):
	if message.author == client.user:
		return
		
	if message.content == "!check-in":
		await checkin(message)
	
async def checkin(message):
	# adds the checkin messaege and green reaction
	global checkinMessage
	global checkinStatus
	checkinStatus = True
	message = await guild.get_channel(channelId).send("Check-in yapmak için alttaki 🟩 butonuna basın")
	await message.add_reaction("🟩")
	checkinMessage = message.id
    
    # waits for the indicated duration
	timeElapsed = 0
	timestamp = time.time()
	while timeElapsed < checkinDuration:
		await asyncio.sleep(10)
		timeElapsed = int((time.time()-timestamp)/60)
    
    # deletes the message, closes the checkin, updates the tabbycat
	await message.delete()
	checkinStatus = False
	await guild.get_channel(channelId).send("Check-in süresi doldu.")
	await checkinUpdate()

@client.event	
async def on_reaction_add(reaction, user):
	if (not checkinStatus) or (not reaction.message.id == checkinMessage) or (not str(reaction.emoji) == "🟩") or user == client.user:
		return
	
	print(f'user id={user.id}')

	val = (str(user.id),)
	mycursor.execute("SELECT checkin FROM Participants WHERE discord_id = %s", val)
	myresult = mycursor.fetchall()

	if(mycursor.rowcount < 1):
		print(f'user is not registered: id={str(user.id)} name={str(user.name)}')
		return

	if myresult[0][0]:
		return
    
	val = (True, str(user.id))
	mydb.commit()
	mycursor.execute("UPDATE Participants SET checkin = %s WHERE discord_id = %s", val)
	mydb.commit()

	if user.dm_channel == None: 
		await user.create_dm()
	await user.dm_channel.send("You have succesfully checked-in.")

    
async def checkinUpdate():
	mycursor.execute("SELECT id FROM Participants WHERE (checkin = True AND role = 'speaker')")
	myresult = mycursor.fetchall()
	session = aiohttp.ClientSession()
    
	for x in myresult:
		url = f'{tabbyurl.url}/api/v1/tournaments/{tabbyurl.tournament}/speakers/{x[0]}/checkin'
		async with session.put(url, headers=headers) as resp:
			print(f'id={x[0]} status={resp.status}')
			print(await resp.text())

	mycursor.execute("SELECT id FROM Participants WHERE (checkin = True AND role = 'jury')")
	myresult = mycursor.fetchall()

	for x in myresult:
		url = f'{tabbyurl.url}/api/v1/tournaments/{tabbyurl.tournament}/adjudicators/{x[0]}/checkin'
		async with session.put(url, headers=headers) as resp:
			print(f'id={x[0]} status={resp.status}')
			print(await resp.text())

	await session.close()

client.run(TOKEN)

