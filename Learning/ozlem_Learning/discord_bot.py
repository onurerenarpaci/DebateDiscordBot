import os,discord
import random
from dotenv import load_dotenv
from discord.ext import commands
import mysql.connector
import requests

load_dotenv()
mydb = mysql.connector.connect(
	host="localhost",
	user=os.getenv("MYSQL_USER"),
	password=os.getenv("MYSQL_PASSWORD"),
	database="debates")
	
mycursor = mydb.cursor()

TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
	print(f'{bot.user.name} has connected to Discord!')

@bot.command(name = "draw")
async def draw (ctx, round):
	#the code that import tabbycat debates
	url = f'https://kutab.herokuapp.com/api/v1/tournaments/bp88team/rounds/{round}/pairings'
	headers = {"Authorization": "Token a11cdf6cbe4ad2d515262f136a5b20d79d3245f3"}
	result = requests.get(url, headers = headers).json()
	zoom_url1 = "https://kocun.zoom.us/j/94108431105"
	zoom_url2 = "https://kocun.zoom.us/j/9402351069"
	#print(result)

	teamid_list = []
	id_list = []
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
	counter = 0
	zoom_url = ""
	#the code that send messages to speakers
	for x in sorted_teamdict:
		sql = "SELECT VenueName from Venues WHERE VenueID = %s"
		val = (x,)
		mycursor.execute(sql,val)
		venue_tup = mycursor.fetchall()
		venue_name = venue_tup[0][0]
		if counter <= (venue_number/2) :
			zoom_url = zoom_url1
		else:
			zoom_url = zoom_url2
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
		counter += 1

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
	counter=0
	for d in sort_chair_dict:
		if sort_chair_dict[d] != None:
			sql = "SELECT VenueName from Venues WHERE VenueID = %s"
			val = (d,)
			mycursor.execute(sql,val)
			venue_name_tup = mycursor.fetchall()
			venue_name = venue_name_tup[0][0]
			if counter <= (venue_number/2) :
				zoom_url = zoom_url1
			else:
				zoom_url = zoom_url2
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
			embed.add_field(name='Bina Linki', value = f'[Zoom görüşmenize katılmak için buraya tıklayın]({zoom_url})', inline= False)
			embed.add_field(name='Tabbycat Linki', value = f'[Size özel Tabbycat linkiniz](https://kutab.herokuapp.com/bp88team/{url_key})', inline= False)
			embed.add_field(name='Salon', value = venue_name, inline= True)
			embed.add_field(name='Pozisyon', value = "Baş Jüri", inline= True)
			if sort_chair_dict[d] != None :
				user = bot.get_user(sort_chair_dict[d]) 
				await user.send(embed = embed)
	counter += 1

	counter=0
	for e in sort_panel_dict:
		if len(e) > 0:
			sql = "SELECT VenueName from Venues WHERE VenueID = %s"
			val = (e,)
			mycursor.execute(sql,val)
			venue_name_tup = mycursor.fetchall()
			venue_name = venue_name_tup[0][0]
			if counter <= (venue_number/2) :
				zoom_url = zoom_url1
			else:
				zoom_url = zoom_url2
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
					embed.add_field(name='Bina Linki', value = f'[Zoom görüşmenize katılmak için buraya tıklayın]({zoom_url})', inline= False)
					embed.add_field(name='Tabbycat Linki', value = f'[Size özel Tabbycat linkiniz](https://kutab.herokuapp.com/bp88team/{url_key})', inline= False)
					embed.add_field(name='Salon', value = venue_name, inline= True)
					embed.add_field(name='Pozisyon', value = "Yan Jüri", inline= True) 
					user = bot.get_user(sort_panel_dict[e][f])
					await user.send(embed = embed)
		counter += 1

	counter = 0
	for g in sort_tra_dict:
		if len(g) > 0:
			sql = "SELECT VenueName from Venues WHERE VenueID = %s"
			val = (g,)
			mycursor.execute(sql,val)
			venue_name_tup = mycursor.fetchall()
			venue_name = venue_name_tup[0][0]
			if counter <= (venue_number/2) :
				zoom_url = zoom_url1
			else:
				zoom_url = zoom_url2
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
					embed.add_field(name='Bina Linki', value = f'[Zoom görüşmenize katılmak için buraya tıklayın]({zoom_url})', inline= False)
					embed.add_field(name='Tabbycat Linki', value = f'[Size özel Tabbycat linkiniz](https://kutab.herokuapp.com/bp88team/{url_key})', inline= False)
					embed.add_field(name='Salon', value = venue_name, inline= True)
					embed.add_field(name='Pozisyon', value = "İzleyici", inline= True)
					user = bot.get_user(sort_tra_dict[g][h])
					await user.send(embed = embed)
		counter += 1

bot.run(TOKEN)
