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
    
    j=0
    for a in result:
        chair_url = result[j].get("adjudicators").get("chair")
        id_list.append(chair_url.split('/')[-1])
    for b in (result[j].get("adjudicators").get("panellists")):
        id_list.append(b.split('/')[-1])
    for c in (result[j].get("adjudicators").get("trainees")):
        id_list.append(c.split('/')[-1])
    ven = a.get("venue")
    ven_id = ven.split('/')[-1]
    adj_dict[ven_id] = id_list[0:len(id_list)]
    id_list.clear()
    j += 1

    discordID_list = []
    for d in teamdict:
        for e in range(len(teamdict[d])):
            sql = "SELECT discord_id FROM Participants WHERE team_id = %s AND discord_id IS NOT NULL"
            val = (int(teamdict[d][e]),)
            mycursor.execute(sql,val)
            result = mycursor.fetchall()
            discordID_list.extend(result)
        teamdict[d] = discordID_list[0: len(discordID_list)]
        discordID_list.clear()
    
    for x in teamdict:
        sql = "SELECT VenueName from Venues WHERE VenueID = %s"
        val = (x,)
        mycursor.execute(sql,val)
        venue_tup = mycursor.fetchone()
        venue_name = venue_tup[0]
        for y in range(len(teamdict[x])):
            if y == 0:
                side = 'HA'
            elif y == 1:
                side = 'MA'
            elif y ==2:
                side = 'HK'
            else :
                side = 'MK'
            for z in teamdict[x][y]:
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
                embed.add_field(name='[Zoom görüşmenize katılmak için buraya tıklayın](https://kocun.zoom.us/j/9402351069)', value = '[Size özel Tabbycat linkiniz](https://www.oxfordlearnersdictionaries.com/)', inline= False)
                embed.add_field(name='Salon', value = venue_name, inline= True)
                embed.add_field(name='Pozisyon', value = side, inline= True)
                user = bot.get_user(z)
                await user.send(embed = embed)



"""
@bot.command(name = "kayıt")
async def register(ctx,unique_id):
    user = ctx.author
    sql = "update Participants set discord_id = %s where unique_id = %s"
    val = (user.id, unique_id,)
    mycursor.execute(sql,val)

    sql = "select team,name from Participants where unique_id = %s"
    val = (unique_id,)
    mycursor.execute(sql,val)
    myresult = mycursor.fetchone()
    if(mycursor.rowcount >= 1):
        mydb.commit()
        await ctx.send("Kayıt başarılı.")
    else:
        await ctx.send("Kayıt başarısız, id bulunamadı.")
    


@bot.command(name="hello")
async def nine_nine(ctx):
    response = "hi 2jjj"
    await ctx.send(response)
"""
"""
@bot.command(name = "msg")
async def on_message(ctx):

    embed = discord.Embed(
        title = 'Başlık',
        description = 'Bu bir tanım',
        colour = discord.Colour.red()
    )   

    embed.set_footer(text = 'bu bir footer')
    embed.set_image(url='https://www.freeiconspng.com/uploads/letter-i-icon-png-14.png')
    embed.set_thumbnail(url='https://teknodestek.com.tr/wp-content/uploads/2020/04/Zoom-kapak.jpg')
    embed.set_author(name= 'yazar adı',
    icon_url='https://kadikoyehliyet.org/wp-content/uploads/2018/11/icon.png')
    embed.add_field(name='alan adı inline false', value = 'alan değeri', inline= False)
    embed.add_field(name='alan adı inline true1', value = 'alan değeri', inline= True)
    embed.add_field(name='alan adı inline true2', value = 'alan değeri', inline= True)

    await ctx.send(embed = embed)

"""



bot.run(TOKEN)
