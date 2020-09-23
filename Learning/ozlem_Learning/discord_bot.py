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
    url = f'https://kutab.herokuapp.com/api/v1/tournaments/bp88team/rounds/{round}/pairings'
    headers = {"Authorization": "Token a11cdf6cbe4ad2d515262f136a5b20d79d3245f3"}
    result = requests.get(url, headers = headers).json()
    zoom_url1 = "https://kocun.zoom.us/j/94108431105"
    zoom_url2 = "https://kocun.zoom.us/j/9402351069"
    #print(result)
    teamid_list = []
    id_list = []
    teamdict = {}
    adj_dict = {}
    
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
    
    discordID_list = []
    for d in teamdict:
        for e in range(len(teamdict[d])):
            sql = "SELECT discord_id FROM Participants WHERE team_id = %s AND discord_id IS NOT NULL"
            val = (int(teamdict[d][e]),)
            mycursor.execute(sql,val)
            result = mycursor.fetchall()
            discordID_list .extend(result)
        teamdict[d] = discordID_list[0: len(discordID_list)]
        discordID_list.clear()

    sorted_teamdict = {}
    for i in sorted (teamdict) : 
        sorted_teamdict[i]=teamdict[i]
    
    venue_number = len(sorted_teamdict.keys())
    counter = 0
    zoom_url = ""
    for x in sorted_teamdict:
        sql = "SELECT VenueName from Venues WHERE VenueID = %s"
        val = (x,)
        mycursor.execute(sql,val)
        venue_tup = mycursor.fetchone()
        venue_name = venue_tup[0]
        print(x)
        if counter <= (venue_number/2) :
            zoom_url = zoom_url1
        else:
            zoom_url = zoom_url2
        for y in range(len(sorted_teamdict[x])):
            if y == 0:
                side = 'HA'
            elif y == 1:
                side = 'MA'
            elif y ==2:
                side = 'HK'
            else :
                side = 'MK'
            print("side")
            for z in sorted_teamdict[x][y]:
                print("z")
                sql = "SELECT name,team from Participants WHERE discord_id = %s"
                val = (z,)
                mycursor.execute(sql,val)
                debater = mycursor.fetchone()
                debater_name = debater[0]
                debater_team = debater[1]
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
                embed.add_field(name=f'[Zoom görüşmenize katılmak için buraya tıklayın]({zoom_url})', value = '[Size özel Tabbycat linkiniz](https://www.oxfordlearnersdictionaries.com/)', inline= False)
                embed.add_field(name='Salon', value = venue_name, inline= True)
                embed.add_field(name='Pozisyon', value = side, inline= True)
                user = bot.get_user(z)
                await user.send(embed = embed)
            counter += 1
    """
    venue_id_list = []
    
    for v in result:
        ven = v.get("venue")
        venue_id_list.append(ven.split('/')[-1])
    
    venue_id_list.sort()
    j=0
    for a in venue_id_list:
        sql = "SELECT VenueName from Venues WHERE VenueID = %s"
        val = (a,)
        mycursor.execute(sql,val)
        venue_tup = mycursor.fetchone()
        venue_name = venue_tup[0]
        
        if j <= (venue_number/2) :
            zoom_url = zoom_url1
        else:
            zoom_url = zoom_url2

        chair_url = result[j].get("adjudicators").get("chair")
        chair_id = chair_url.split('/')[-1]
        sql = "SELECT discord_id,name FROM Participants WHERE id = %s AND discord_id IS NOT NULL"
        val = (chair_id,)
        mycursor.execute(sql,val)
        chair_dc = mycursor.fetchone()[0]
        chair_name = mycursor.fetchone()[1]
        embed = discord.Embed(
            title = f'{round}. TUR KURASI',
            description = f'{chair_name}, baş jüri için gerekli bilgiler:',
            colour = 0xce0203,
        )
        embed.set_footer(text= "Eylül 2020")
        embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/750848362156392531/757684239914500146/Ku_Munazara_turnuva.jpg')
        embed.add_field(name='[Zoom görüşmenize katılmak için buraya tıklayın](zoom_url)', value = '[Size özel Tabbycat linkiniz](https://www.oxfordlearnersdictionaries.com/)', inline= False)
        embed.add_field(name='Salon', value = venue_name, inline= True)
        embed.add_field(name='Pozisyon', value = "Baş Jüri", inline= True)
        user = bot.get_user(chair_dc)
        await user.send(embed = embed)

        for b in (result[j].get("adjudicators").get("panellists")):
            pan_id = b.split('/')[-1]
            sql = "SELECT discord_id,name FROM Participants WHERE id = %s AND discord_id IS NOT NULL"
            val = (pan_id,)
            mycursor.execute(sql,val)
            pan_dc = mycursor.fetchone()[0]
            pan_name = mycursor.fetchone()[1]
            embed = discord.Embed(
                title = f'{round}. TUR KURASI',
                description = f'{pan_name}, yan jüri için gerekli bilgiler:',
                colour = 0xce0203,
            )
            embed.set_footer(text= "Eylül 2020")
            embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/750848362156392531/757684239914500146/Ku_Munazara_turnuva.jpg')
            embed.add_field(name='[Zoom görüşmenize katılmak için buraya tıklayın](https://kocun.zoom.us/j/9402351069)', value = '[Size özel Tabbycat linkiniz](https://www.oxfordlearnersdictionaries.com/)', inline= False)
            embed.add_field(name='Salon', value = venue_name, inline= True)
            embed.add_field(name='Pozisyon', value = "Yan Jüri", inline= True)
            user = bot.get_user(pan_dc)
            await user.send(embed = embed)

        for c in (result[j].get("adjudicators").get("trainees")):
            tra_id = c.split('/')[-1]
            sql = "SELECT discord_id,name FROM Participants WHERE id = %s AND discord_id IS NOT NULL"
            val = (tra_id,)
            mycursor.execute(sql,val)
            tra_dc = mycursor.fetchone()[0]
            tra_name = mycursor.fetchone()[1]
            embed = discord.Embed(
                title = f'{round}. TUR KURASI',
                description = f'{tra_name}, izleyici için gerekli bilgiler:',
                colour = 0xce0203,
            )
            embed.set_footer(text= "Eylül 2020")
            embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/750848362156392531/757684239914500146/Ku_Munazara_turnuva.jpg')
            embed.add_field(name='[Zoom görüşmenize katılmak için buraya tıklayın](https://kocun.zoom.us/j/9402351069)', value = '[Size özel Tabbycat linkiniz](https://www.oxfordlearnersdictionaries.com/)', inline= False)
            embed.add_field(name='Salon', value = venue_name, inline= True)
            embed.add_field(name='Pozisyon', value = "İzleyici", inline= True)
            user = bot.get_user(tra_dc)
            await user.send(embed = embed)
    
        j += 1
    """
    chair_dict = {}
    panel_dict = {}
    tra_dict = {}
    pan_list = []
    tra_list = []

    j=0
    for a in result:
        ven = a.get("venue")
        ven_id = ven.split('/')[-1]
        print(ven_id)
        chair_url = resul[j].get("adjudicators").get("chair")
        chair_id = chair_url.split('/')[-1]
        print(chair_id)
        sql = "SELECT discord_id FROM Participants WHERE id = %s AND discord_id IS NOT NULL"
        val = (chair_id,)
        mycursor.execute(sql,val)
        chair_dc_tup = mycursor.fetchone()
        chair_dc = chair_dc_tup[0]
        chair_dict[ven_id] = chair_dc
        for b in (result[j].get("adjudicators").get("panellists")):
            pan_id = b.split('/')[-1]
            sql = "SELECT discord_id FROM Participants WHERE id = %s AND discord_id IS NOT NULL"
            val = (pan_id,)
            mycursor.execute(sql,val)
            pan_dc_tup = mycursor.fetchone()
            pan_dc = pan_dc_tup[0]
            pan_list.append(pan_dc)
        panel_dict[ven_id] = pan_list[0: len(pan_list)]
        
        for c in (result[j].get("adjudicators").get("trainees")):
            tra_id = c.split('/')[-1]
            sql = "SELECT discord_id FROM Participants WHERE id = %s AND discord_id IS NOT NULL"
            val = (tra_id,)
            mycursor.execute(sql,val)
            tra_dc = mycursor.fetchone()[0]
            tra_list.append(tra_dc)
        tra_dict[ven_id] = tra_list
        j += 1
    
    sort_chair_dict = {}
    sort_panel_dict = {}
    sort_tra_dict = {}

    for a in sorted (chair_dict):
        sort_chair_dict[a] = chair_dict[a]
    for b in sorted (panel_dict):
        sort_panel_dict[b] = panel_dict[b]
    for c in sorted (tra_dict):
        sort_tra_dict[c] = tra_dict[c]
    
    counter=0
    for d in sort_chair_dict:
        sql = "SELECT VenueName from Venues WHERE VenueID = %s"
        val = (d,)
        mycursor.execute(sql,val)
        venue_tup = mycursor.fetchone()
        venue_name = venue_tup[0]
        if counter <= (venue_number/2) :
            zoom_url = zoom_url1
        else:
            zoom_url = zoom_url2
        sql = "SELECT name from Participants WHERE discord_id = %s"
        val = (sort_chair_dict[d],)
        mycursor.execute(sql,val)
        chair_name_tup = mycursor.fetchone()
        chair_name = chair_name_tup[0]
        embed = discord.Embed(
            title = f'{round}. TUR KURASI',
            description = f'{chair_name}, baş jüri için gerekli bilgiler:',
            colour = 0xce0203,
        )
        embed.set_footer(text= "Eylül 2020")
        embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/750848362156392531/757684239914500146/Ku_Munazara_turnuva.jpg')
        embed.add_field(name=f'[Zoom görüşmenize katılmak için buraya tıklayın]({zoom_url})', value = '[Size özel Tabbycat linkiniz](https://www.oxfordlearnersdictionaries.com/)', inline= False)
        embed.add_field(name='Salon', value = venue_name, inline= True)
        embed.add_field(name='Pozisyon', value = "Baş Jüri", inline= True)
        user = bot.get_user(chair_dict[d])
        await user.send(embed = embed)
    counter += 1

    counter=0
    for e in sort_panel_dict:
        sql = "SELECT VenueName from Venues WHERE VenueID = %s"
        val = (e,)
        mycursor.execute(sql,val)
        venue_tup = mycursor.fetchone()
        venue_name = venue_tup[0]
        if counter <= (venue_number/2) :
            zoom_url = zoom_url1
        else:
            zoom_url = zoom_url2
        for f in sort_panel_dict[e]:
            sql = "SELECT name from Participants WHERE discord_id = %s"
            val = (sort_panel_dict[e][f],)
            mycursor.execute(sql,val)
            pan_name_tup = mycursor.fetchone()
            pan_name = pan_name_tup[0]
            embed = discord.Embed(
                title = f'{round}. TUR KURASI',
                description = f'{pan_name}, yan jüri için gerekli bilgiler:',
                colour = 0xce0203,
            )
            embed.set_footer(text= "Eylül 2020")
            embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/750848362156392531/757684239914500146/Ku_Munazara_turnuva.jpg')
            embed.add_field(name= f'[Zoom görüşmenize katılmak için buraya tıklayın]({zoom_url})', value = '[Size özel Tabbycat linkiniz](https://www.oxfordlearnersdictionaries.com/)', inline= False)
            embed.add_field(name='Salon', value = venue_name, inline= True)
            embed.add_field(name='Pozisyon', value = "Yan Jüri", inline= True)
            user = bot.get_user(panel_dict[e][f])
            await user.send(embed = embed)
        counter += 1
    
    counter = 0
    for g in sort_tra_dict:
        sql = "SELECT VenueName from Venues WHERE VenueID = %s"
        val = (g,)
        mycursor.execute(sql,val)
        venue_tup = mycursor.fetchone()
        venue_name = venue_tup[0]
        if counter <= (venue_number/2) :
            zoom_url = zoom_url1
        else:
            zoom_url = zoom_url2
        for h in sort_tra_dict[g][h]:
            sql = "SELECT name from Participants WHERE discord_id = %s"
            val = (sort_tra_dict[g][h],)
            mycursor.execute(sql,val)
            tra_name_tup = mycursor.fetchone()
            tra_name = tra_name_tup[0]
            embed = discord.Embed(
                title = f'{round}. TUR KURASI',
                description = f'{tra_name}, izleyici için gerekli bilgiler:',
                colour = 0xce0203,
            )
            embed.set_footer(text= "Eylül 2020")
            embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/750848362156392531/757684239914500146/Ku_Munazara_turnuva.jpg')
            embed.add_field(name=f'[Zoom görüşmenize katılmak için buraya tıklayın]({zoom_url})', value = '[Size özel Tabbycat linkiniz](https://www.oxfordlearnersdictionaries.com/)', inline= False)
            embed.add_field(name='Salon', value = venue_name, inline= True)
            embed.add_field(name='Pozisyon', value = "İzleyici", inline= True)
            user = bot.get_user(tra_dc)
            await user.send(embed = embed)
        counter += 1

bot.run(TOKEN)
