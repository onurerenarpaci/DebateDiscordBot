import os
import asyncio
import discord
from discord.ext import commands
import time
from dotenv import load_dotenv
import aiohttp
import mysql.connector
import math

load_dotenv()
headers = {"Authorization": os.getenv("TABBYCAT_TOKEN")}

mydb = mysql.connector.connect(
	host="localhost",
	user=os.getenv("MYSQL_USER"),
	password=os.getenv("MYSQL_PASSWORD"),
	database="debate")

mycursor = mydb.cursor()

tabbyurl = os.getenv("URL")
tournament = os.getenv("TOURNAMENT")
checkinId =  int(os.getenv("CHECKIN_CHANNEL_ID"))#Checkin channel id
announcementId = int(os.getenv("ANNOUNCEMENT_CHANNEL_ID")) # announcement channel id
checkinStatus = False # True = Open, False = Close
checkinMessage = None
checkinDuration = 30 # 30 minutes
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

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

bot = commands.Bot(command_prefix="!")

@bot.event
async def on_ready():
	global guild
	guild = discord.utils.get(bot.guilds, name=GUILD)
	print(
		f'{bot.user} has connected to the following guild:\n'
		f'{guild.name}(id: {guild.id})\n'
	)

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
		url = f'{tabbyurl}/api/v1/tournaments/{tournament}/speakers/{x[0]}/checkin'
		async with session.put(url, headers=headers) as resp:
			print(f'id={x[0]} status={resp.status}')
			print(await resp.text())

	mycursor.execute("SELECT id FROM Participants WHERE (checkin = True AND role = 'jury')")
	myresult = mycursor.fetchall()

	for x in myresult:
		url = f'{tabbyurl}/api/v1/tournaments/{tournament}/adjudicators/{x[0]}/checkin'
		async with session.put(url, headers=headers) as resp:
			print(f'id={x[0]} status={resp.status}')
			print(await resp.text())

	await session.close()

@bot.command()
async def cutteams(ctx):
	sql = "UPDATE Participants SET cut_status = %s WHERE checkin = %s AND role = %s"
	val = (True, False, "speaker")
	mycursor.execute(sql, val)
	mydb.commit()

	sql = "UPDATE Participants SET checkin = %s"
	val = (False,)
	mycursor.execute(sql, val)
	mydb.commit()

	print("Teams have been cut.")	

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
	mycursor.execute("SELECT id, role FROM Participants WHERE discord_id = %s", val)
	myresult = mycursor.fetchall()
	
	session = aiohttp.ClientSession()
	role = "speakers" if myresult[0][1] == "speaker" else "adjudicators"
	url = f'{tabbyurl}/api/v1/tournaments/{tournament}/{role}/{myresult[0][0]}/checkin'
	async with session.put(url, headers=headers) as resp:
		print(f'id={myresult[0][0]} status={resp.status}')
		print(await resp.text())
	
	await session.close()

@bot.command(name='motion')
async def motion_release(ctx, round):
	print("motion_release")
	session = aiohttp.ClientSession()
	url = f'{tabbyurl}/api/v1/tournaments/{tournament}/motions/{round}'
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


@bot.command(name='geribildirim')
async def feedback(ctx):
	await ctx.send("```Size ait Tabbycat bağlantısını kullanarak geri bildirim verebilirsiniz.```")

@bot.command(name = "draw")
async def draw (ctx, round):
	#the code that import tabbycat debates
	url = f'{tabbyurl}/api/v1/tournaments/{tournament}/rounds/{round}/pairings'
	session = aiohttp.ClientSession()
	async with session.get(url, headers=headers) as resp:
		print(resp.status)
		result = await resp.json()
	await session.close()

	#print(result)

	duration = 60
	clock = (1,0)
	message = await guild.get_channel(announcementId).send(f"Kuranın açıklanmasına: `{int(clock[0]):02}:{int(clock[1]):02}`\n@everyone")
	timestamp = time.time()
	timedelta = 0
	while duration > timedelta:
		await asyncio.sleep(5)
		timedelta = time.time() - timestamp
		clock = divmod(max(0,(duration - timedelta)),60)
		msg = f"Kuranın açıklanmasına: `{int(clock[0]):02}:{int(clock[1]):02}`\n@everyone"
		await message.edit(content=msg)
	await message.delete()

	teamid_list = []
	teamdict = {}

	#the code that takes team ids from tabbycat data and create a venue-team id list dictionary
	i=0
	for x in result:
		for y in range(4):
			string = (result[i].get("teams")[y].get("team"))
			teamid_list.append(string.split('/')[-1])
		ven = x.get("venue")
		ven_id = ven.split('/')[-1]
		teamdict[ven_id] = teamid_list[0:4]
		teamid_list.clear()
		i +=1
	
	#the code that convert venue-team id list dictionary to venue-discord id list dictionary
	discordID_list = []
	for d in teamdict:
		for e in range(len(teamdict[d])):
			sql = "SELECT discord_id FROM Participants WHERE team_id = %s"
			val = (teamdict[d][e],)
			#(following line has an error)
			mycursor.execute(sql,val)
			speakers = mycursor.fetchall()
			discordID_list.extend(x[0] for x in speakers)
		teamdict[d] = discordID_list.copy()
		discordID_list.clear()

	#the code that sort venue-discord id list dictionary
	sorted_teamdict = {}
	for i in sorted (teamdict) : 
		sorted_teamdict[i]=teamdict[i]

	venue_number = len(sorted_teamdict.keys())

	zoom_url = ""
	#the code that send messages to speakers
	for x in sorted_teamdict:
		sql = "SELECT VenueName, zoom_link from Venues WHERE VenueID = %s"
		val = (x,)
		mycursor.execute(sql,val)
		venue_tup = mycursor.fetchall()
		venue_name = venue_tup[0][0]
		zoom_url = venue_tup[0][1]

		for y in range(len(sorted_teamdict[x])):
			if y == 0 or y ==1:
				side = 'MK'
			elif y == 2 or y ==3:
				side = 'HK'
			elif y ==4 or y == 5:
				side = 'MA'
			else :
				side = 'HA'

			if sorted_teamdict[x][y] != None:
				sql = "SELECT name from Participants WHERE discord_id = %s AND role = %s"
				val = (sorted_teamdict[x][y],'speaker')
				mycursor.execute(sql,val)
				debater_name_tup = mycursor.fetchall()
				debater_name = debater_name_tup[0][0]
				sql = "SELECT team from Participants WHERE discord_id = %s AND role = %s"
				val = (sorted_teamdict[x][y],'speaker')
				mycursor.execute(sql,val)
				debater_team_tup = mycursor.fetchall()
				debater_team = debater_team_tup[0][0]
				sql = "SELECT url_key from Participants WHERE discord_id = %s AND role = %s"
				val = (sorted_teamdict[x][y],'speaker')
				mycursor.execute(sql,val)
				url_key_tup = mycursor.fetchall()
				url_key = str(url_key_tup[0][0])
				embed = discord.Embed(
					title = f'{round}. TUR KURASI',
					description = f'{debater_name}, {debater_team} takımı için gerekli bilgiler:',
					colour = 0xce0203
				)   
				embed.set_footer(text = 'Eylül 2020')
				#embed.set_image(url='https://cdn.discordapp.com/attachments/750848362156392531/757671571438567584/Ku_Munazara.jpg')
				embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/750848362156392531/757684239914500146/Ku_Munazara_turnuva.jpg')
				embed.set_author(name= 'KU AÇIK 2020 ÇEVRİMİÇİ',
				icon_url='https://cdn.discordapp.com/attachments/750848362156392531/757672480239386714/Ku_Munazara_icon.jpg')
				embed.add_field(name='Bina Linki', value = f'[Zoom görüşmenize katılmak için buraya tıklayın]({zoom_url})', inline= False)
				embed.add_field(name='Tabbycat Linki', value = f'[Size özel Tabbycat linkiniz](https://kutab.herokuapp.com/bp88team/{url_key})', inline= False)
				embed.add_field(name='Salon', value = venue_name, inline= True)
				embed.add_field(name='Pozisyon', value = side, inline= True)
				user = bot.get_user(sorted_teamdict[x][y])
				await user.send(embed = embed)


	chair_dict = {}
	panel_dict = {}
	tra_dict = {}
	pan_list = []
	tra_list = []

	#the code that create venue-chair discord id list, venue-panellists discord id list, venue-trainees discord id list dictionaires
	j=0
	for a in result:
		ven = a.get("venue")
		ven_id = ven.split('/')[-1]
		chair_url = result[j].get("adjudicators").get("chair")
		chair_id = chair_url.split('/')[-1]
		sql = "SELECT discord_id FROM Participants WHERE id = %s"
		val = (chair_id,)
		mycursor.execute(sql,val)
		chair_dc_tup = mycursor.fetchall()
		chair_dc = chair_dc_tup[0][0]
		chair_dict[ven_id] = chair_dc

		for b in (result[j].get("adjudicators").get("panellists")):
			pan_id = b.split('/')[-1]
			sql = "SELECT discord_id FROM Participants WHERE id = %s"
			val = (pan_id,)
			mycursor.execute(sql,val)
			pan_dc_tup = mycursor.fetchall()
			pan_dc = pan_dc_tup[0][0]
			pan_list.append(pan_dc)
		panel_dict[ven_id] = pan_list[0: len(pan_list)]
		pan_list.clear()

		for c in (result[j].get("adjudicators").get("trainees")):
			tra_id = c.split('/')[-1]
			sql = "SELECT discord_id FROM Participants WHERE id = %s"
			val = (tra_id,)
			mycursor.execute(sql,val)
			tra_dc_tup = mycursor.fetchall()
			tra_dc = tra_dc_tup[0][0]
			tra_list.append(tra_dc)
		tra_dict[ven_id] = tra_list[0: len(tra_list)]
		tra_list.clear()
		
		j += 1

	venue_number = len(chair_dict.keys())
	sort_chair_dict = {}
	sort_panel_dict = {}
	sort_tra_dict = {}

	#the code that sort three dictionaries
	for a in sorted (chair_dict):
		sort_chair_dict[a] = chair_dict[a]
	for b in sorted (panel_dict):
		sort_panel_dict[b] = panel_dict[b]
	for c in sorted (tra_dict):
		sort_tra_dict[c] = tra_dict[c]
 
	#the code that send messages

	for d in sort_chair_dict:
		if sort_chair_dict[d] != None:
			sql = "SELECT VenueName, zoom_link from Venues WHERE VenueID = %s"
			val = (d,)
			mycursor.execute(sql,val)
			venue_tup = mycursor.fetchall()
			venue_name = venue_tup[0][0]
			zoom_url = venue_tup[0][1]

			sql = "SELECT name from Participants WHERE discord_id = %s AND role = %s"
			val = (sort_chair_dict[d],'jury')
			mycursor.execute(sql,val)
			chair_name_tup = mycursor.fetchall()
			chair_name = chair_name_tup[0][0]
			sql = "SELECT url_key from Participants WHERE discord_id = %s AND role = %s"
			val = (sort_chair_dict[d],'jury')
			mycursor.execute(sql,val)
			url_key_tup = mycursor.fetchall()
			url_key = str(url_key_tup[0][0])
			embed = discord.Embed(
				title = f'{round}. TUR KURASI',
				description = f'{chair_name}, baş jüri için gerekli bilgiler:',
				colour = 0xce0203,
			)
			embed.set_footer(text= "Eylül 2020")
			embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/750848362156392531/757684239914500146/Ku_Munazara_turnuva.jpg')
			embed.set_author(name= 'KU AÇIK 2020 ÇEVRİMİÇİ',
			icon_url='https://cdn.discordapp.com/attachments/750848362156392531/757672480239386714/Ku_Munazara_icon.jpg')
			embed.add_field(name='Bina Linki', value = f'[Zoom görüşmenize katılmak için buraya tıklayın]({zoom_url})', inline= False)
			embed.add_field(name='Tabbycat Linki', value = f'[Size özel Tabbycat linkiniz](https://kutab.herokuapp.com/bp88team/{url_key})', inline= False)
			embed.add_field(name='Salon', value = venue_name, inline= True)
			embed.add_field(name='Pozisyon', value = "Baş Jüri", inline= True)
			if sort_chair_dict[d] != None :
				user = bot.get_user(sort_chair_dict[d]) 
				await user.send(embed = embed)



	for e in sort_panel_dict:
		if len(e) > 0:
			sql = "SELECT VenueName, zoom_link from Venues WHERE VenueID = %s"
			val = (e,)
			mycursor.execute(sql,val)
			venue_tup = mycursor.fetchall()
			venue_name = venue_tup[0][0]
			zoom_url = venue_tup[0][1]

			for f in range(len(sort_panel_dict[e])):
				if sort_panel_dict[e][f] != None:
					sql = "SELECT name from Participants WHERE discord_id = %s AND role = %s"
					val = (sort_panel_dict[e][f], 'jury')
					mycursor.execute(sql,val)
					pan_name_tup = mycursor.fetchall()
					pan_name = pan_name_tup[0][0]
					sql = "SELECT url_key from Participants WHERE discord_id = %s AND role = %s"
					val = (sort_panel_dict[e][f], 'jury')
					mycursor.execute(sql,val)
					url_key_tup = mycursor.fetchall()
					url_key = str(url_key_tup[0][0])
					embed = discord.Embed(
						title = f'{round}. TUR KURASI',
						description = f'{pan_name}, yan jüri için gerekli bilgiler:',
						colour = 0xce0203,
					)
					embed.set_footer(text= "Eylül 2020")
					embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/750848362156392531/757684239914500146/Ku_Munazara_turnuva.jpg')
					embed.set_author(name= 'KU AÇIK 2020 ÇEVRİMİÇİ',
					icon_url='https://cdn.discordapp.com/attachments/750848362156392531/757672480239386714/Ku_Munazara_icon.jpg')					
					embed.add_field(name='Bina Linki', value = f'[Zoom görüşmenize katılmak için buraya tıklayın]({zoom_url})', inline= False)
					embed.add_field(name='Tabbycat Linki', value = f'[Size özel Tabbycat linkiniz](https://kutab.herokuapp.com/bp88team/{url_key})', inline= False)
					embed.add_field(name='Salon', value = venue_name, inline= True)
					embed.add_field(name='Pozisyon', value = "Yan Jüri", inline= True) 
					user = bot.get_user(sort_panel_dict[e][f])
					await user.send(embed = embed)



	for g in sort_tra_dict:
		if len(g) > 0:
			sql = "SELECT VenueName, zoom_link from Venues WHERE VenueID = %s"
			val = (g,)
			mycursor.execute(sql,val)
			venue_tup = mycursor.fetchall()
			venue_name = venue_tup[0][0]
			zoom_url = venue_tup[0][1]

			for h in range(len(sort_tra_dict[g])):
				if sort_tra_dict[g][h] != None:
					sql = "SELECT name from Participants WHERE discord_id = %s AND role = %s"
					val = (sort_tra_dict[g][h], 'jury')
					mycursor.execute(sql,val)
					tra_name_tup = mycursor.fetchall()
					tra_name = tra_name_tup[0][0]
					sql = "SELECT url_key from Participants WHERE discord_id = %s AND role = %s"
					val = (sort_tra_dict[g][h], 'jury')
					mycursor.execute(sql,val)
					url_key_tup = mycursor.fetchall()
					url_key = str(url_key_tup[0][0])
					embed = discord.Embed(
						title = f'{round}. TUR KURASI',
						description = f'{tra_name}, izleyici için gerekli bilgiler:',
						colour = 0xce0203,
					)
					embed.set_footer(text= "Eylül 2020")
					embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/750848362156392531/757684239914500146/Ku_Munazara_turnuva.jpg')
					embed.set_author(name= 'KU AÇIK 2020 ÇEVRİMİÇİ',
					icon_url='https://cdn.discordapp.com/attachments/750848362156392531/757672480239386714/Ku_Munazara_icon.jpg')
					embed.add_field(name='Bina Linki', value = f'[Zoom görüşmenize katılmak için buraya tıklayın]({zoom_url})', inline= False)
					embed.add_field(name='Tabbycat Linki', value = f'[Size özel Tabbycat linkiniz](https://kutab.herokuapp.com/bp88team/{url_key})', inline= False)
					embed.add_field(name='Salon', value = venue_name, inline= True)
					embed.add_field(name='Pozisyon', value = "İzleyici", inline= True)
					user = bot.get_user(sort_tra_dict[g][h])
					await user.send(embed = embed)
		counter += 1



bot.run(TOKEN)
mydb.commit()
mycursor.close()
mydb.close()
print('Kapatıldı')


