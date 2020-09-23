# bot.py
import os
import asyncio
import discord
from discord.ext import commands
import time
from dotenv import load_dotenv
import aiohttp
import tabbyurl
import mysql.connector
import math

mydb = mysql.connector.connect(
	host="localhost",
	user="onur",
	password="koc2020",
	database="firstdatabase"
)

mycursor = mydb.cursor()

checkinId = 739551824612294687 #Checkin channel id
announcementId = 739551824612294687 # announcement channel id
checkinStatus = False # True = Open, False = Close
checkinMessage = None
guild = None # discord.utils.get(bot.guilds, name=GUILD)
checkinDuration = 1 # 30 minutes
cutMessageList = []
motion_messages = {
	"1": "1. Tur Maçının Konusu:",
	"2": "2. Tur Maçının Konusu:",
	"3": "3. Tur Maçının Konusu:",
	"4": "4. Tur Maçının Konusu:",
	"5": "5. Tur Maçının Konusu:",
	"6": "Çeyrek Final Konusu:",
	"7": "Yarı Final Konusu:",
	"8": "Final Konusu:",
}

headers = {"Authorization" : "Token 35792636ef40d2194607066b63e49e3ad3a2076c"}

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('GUILD_NAME')

bot = commands.Bot(command_prefix="!")

@bot.event
async def on_ready():
	global guild
	guild = discord.utils.get(bot.guilds, name=GUILD)
	print(
		f'{bot.user} has connected to the following guild:\n'
		f'{guild.name}(id: {guild.id})\n'
	)

# @bot.event
# async def on_message(message):
# 	if message.author == bot.user:
# 		return
		
# 	if message.content == "!check-in":
# 		await checkin(message)
	
# 	if message.content == "!beingcut":
# 		await beingcut()

@bot.command()	
async def checkin(ctx):
	# adds the checkin messaege and green reaction
	global checkinMessage
	global checkinStatus
	checkinStatus = True
	message = await guild.get_channel(checkinId).send("Check-in yapmak için alttaki 🟩 butonuna basın")
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
	await guild.get_channel(checkinId).send("Check-in süresi doldu.")
	await checkinUpdate()

@bot.event	
async def on_reaction_add(reaction, user):
	if (not checkinStatus) or (not reaction.message.id == checkinMessage) or (not str(reaction.emoji) == "🟩") or user == bot.user:
		return
	
	print(f'user id={user.id}')

	val = (user.id,)
	mycursor.execute("SELECT checkin FROM Participants WHERE discord_id = %s", val)
	myresult = mycursor.fetchall()

	if(mycursor.rowcount < 1):
		print(f'user is not registered: id={str(user.id)} name={str(user.name)}')
		return

	if myresult[0][0]:
		return
    
	val = (True, user.id)
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

@bot.command()
async def beingcut(ctx):
	global cutMessageList
	alttabs = "".join("-" for x in range(75))
	linebreak = "\n" # f stringin içindeki curly bracketlarda backslah konulamıyormuş
	
	val = (False, False, "speaker")
	mycursor.execute("SELECT name, team, institution FROM Participants WHERE checkin = %s AND cut_status = %s AND role = %s;", val)
	myresult = mycursor.fetchall()

	teamtable = [[f'{x[0][:25]:<30}{x[1][:20]:<25}{x[2][:20]:<20}' for x in myresult[y*20:(y*20+20)]] for y in range(int(math.ceil(len(myresult)/20)))]
	team_title = f'{"İsim":<30}{"Takım":<25}{"Okul":20}\n'
	
	title_1 = f'✂️ Düşürülmek üzere olan takımlar ✂️'
	title_2 = f'✂️ Düşürülmek üzere olan juriler ✂️'

	val = (False, False, "jury")
	mycursor.execute("SELECT name, institution FROM Participants WHERE checkin = %s AND cut_status = %s AND role = %s;", val)
	myresult = mycursor.fetchall()

	jurytable = [[f'{x[0][:25]:<30}{x[1][:20]:<20}' for x in myresult[y*20:(y*20+20)]] for y in range(int(math.ceil(len(myresult)/20)))]
	jury_title = f'{"İsim":<30}{"Okul":20}\n'

	await guild.get_channel(announcementId).delete_messages(cutMessageList)
	
	cutMessageList.clear()

	if len(teamtable[0]) >= 1:
		message = await guild.get_channel(announcementId).send(title_1)
		cutMessageList.append(message)

		firstCodeBlock = True

		for x in teamtable:
			if firstCodeBlock:
				message = await guild.get_channel(announcementId).send(f'```{team_title}{alttabs}\n{linebreak.join(x)}```')
				cutMessageList.append(message)
				firstCodeBlock = False
			else:
				message = await guild.get_channel(announcementId).send(f'```{linebreak.join(x)}```')
				cutMessageList.append(message)

	if len(jurytable[0]) >= 1:	
		message = await guild.get_channel(announcementId).send(title_2)
		cutMessageList.append(message)

		firstCodeBlock = True

		for x in jurytable:
			if firstCodeBlock:
				message = await guild.get_channel(announcementId).send(f'```{jury_title}{alttabs[:50]}\n{linebreak.join(x)}```')
				cutMessageList.append(message)
				firstCodeBlock = False
			else:
				message = await guild.get_channel(announcementId).send(f'```{linebreak.join(x)}```')
				cutMessageList.append(message)

@bot.command(name='manual_checkin')
async def manual_checkin(ctx, discord_id):

	val = (True, int(discord_id))
	mydb.commit()
	mycursor.execute("UPDATE Participants SET checkin = %s WHERE discord_id = %s", val)
	mydb.commit()

	if(mycursor.rowcount <= 0):
		print(f'user is not registered or already checked-in. id= {discord_id}')
		return

	val = (int(discord_id),)
	mycursor.execute("SELECT id FROM Participants WHERE discord_id = %s", val)
	myresult = mycursor.fetchall()
	session = aiohttp.ClientSession()

	url = f'{tabbyurl.url}/api/v1/tournaments/{tabbyurl.tournament}/speakers/{myresult[0][0]}/checkin'
	async with session.put(url, headers=headers) as resp:
		print(f'id={myresult[0][0]} status={resp.status}')
		print(await resp.text())
	
	await session.close()

@bot.command(name='motion')
async def motion_release(ctx, round):
	print("motion_release")
	session = aiohttp.ClientSession()
	url = f'{tabbyurl.url}/api/v1/tournaments/{tabbyurl.tournament}/motions/{round}'
	async with session.get(url, headers=headers) as resp:
		print(resp.status)
		result = await resp.json()

	await session.close()
	
	message = await releaseCountdown()
	msg = motion_messages[round]
	await message.edit(content=msg)
	if len(result["info_slide"]) > 0:
		msg = f'**```Ön Bilgi: {result["info_slide"]}```**'
		await guild.get_channel(announcementId).send(msg)
		message = await releaseCountdown()

	msg = f'**```Konu: {result["text"]}```**\n'
	await message.edit(content=msg)

	await prepCountdown()


async def prepCountdown():
	duration = 15*60
	clock = (15,0)
	message = await guild.get_channel(announcementId).send(f"Kalan hazırlık süresi: `{int(clock[0]):02}:{int(clock[1]):02}`")
	timestamp = time.time()
	timedelta = 0
	while duration > timedelta:
		await asyncio.sleep(5)
		timedelta = time.time() - timestamp
		clock = divmod(max(0,(duration - timedelta)),60)
		msg = f"Kalan hazırlık süresi: `{int(clock[0]):02}:{int(clock[1]):02}`"
		await message.edit(content=msg)
	await message.edit(content='Süre Doldu! @everyone')

async def releaseCountdown():
	duration = 60
	clock = (1,0)
	message = await guild.get_channel(announcementId).send(f"Konunun açıklanmasına: `{int(clock[0]):02}:{int(clock[1]):02}`\n@everyone")
	timestamp = time.time()
	timedelta = 0
	while duration > timedelta:
		await asyncio.sleep(5)
		timedelta = time.time() - timestamp
		clock = divmod(max(0,(duration - timedelta)),60)
		msg = f"Konunun açıklanmasına: `{int(clock[0]):02}:{int(clock[1]):02}`\n@everyone"
		await message.edit(content=msg)
	return message


bot.run(TOKEN)
mydb.commit()
mycursor.close()
mydb.close()
print('Kapatıldı')


