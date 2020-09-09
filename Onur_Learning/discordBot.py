# bot.py
import os
import asyncio
import discord
import time
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('GUILD_NAME')

client = discord.Client()

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
	
	if message.content == 'hello!':
		await message.channel.send(f'Hello, {message.author.name}!')
	
	if message.content == "!countdown":
		await countdown(message)
		
	if message.content == "!check-in":
		await checkin(message)
	
async def countdown(message):
	duration = 14*60
	minutes = 14
	seconds = 0
	message = await message.channel.send(f"`{minutes:02}:{seconds:02}` minutes left.")
	timestamp = time.time()
	while not (minutes <= 0 and seconds <= 0):
		await asyncio.sleep(5)
		timedelta = time.time() - timestamp
		clock = divmod((duration - timedelta),60)
		msg = f"`{int(clock[0]):02}:{int(clock[1]):02}` minutes left."
		await message.edit(content=msg)
	await message.edit(content='Time is up!')
	
async def checkin(message):
	message = await message.channel.send("Press the green button to check-in")
	await message.add_reaction("🟩")
	await asyncio.sleep(10)
	message = await message.channel.fetch_message(message.id)
	green_reaction = str(message.reactions[0].emoji)
	print(green_reaction)#next(x for x in message.reactions if str(x.emoji) == "🟩")
	users = await message.reactions[0].users().flatten()#green_reaction.users().flatten()
	#print(x.name for x in users) 
	await message.channel.send(" ".join(x.name for x in users))
	

client.run(TOKEN)

