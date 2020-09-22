# bot.py
import os
import asyncio
import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('GUILD_NAME')

client = discord.Client()

checkinMessage = None

@client.event
async def on_ready():
	guild = discord.utils.get(client.guilds, name=GUILD)
	print(
		f'{client.user} has connected to the following guild:\n'
		f'{guild.name}(id: {guild.id})\n'
	)

@client.event
async def on_message(message):
	if message.author == client.user:
		return
	
	if message.content == "!countdown":
		await countdown(message)
		
	if message.content == "!check-in":
		await checkin(message)

@client.event
async def on_reaction_add(reaction, user):
	if user == client.user:
		return

	if checkinMessage == None:
		return
	
	if str(reaction.emoji) == "🟩" and reaction.message.id == checkinMessage:  
		if user.dm_channel == None: 
			await user.create_dm()
		await user.dm_channel.send("You have succesfully checked-in.")

	
async def countdown(message):
	minutes = 14
	seconds = 0
	message = await message.channel.send(f"`{minutes:02}:{seconds:02}` minutes left.")
	while not (minutes <= 0 and seconds <= 0):
		await asyncio.sleep(5)
		if seconds == 0:
			minutes = minutes - 1
			seconds = 55
			msg = f"`{minutes:02}:{seconds:02}` minutes left."
			await message.edit(content=msg)
		else: 
			seconds = seconds - 5
			msg = f"`{minutes:02}:{seconds:02}` minutes left."
			await message.edit(content=msg)
	await message.edit(content='Time is up!')
	
async def checkin(message):
	global checkinMessage
	message = await message.channel.send("Press the green button to check-in")
	await message.add_reaction("🟩")
	checkinMessage = message.id
	

client.run(TOKEN)

