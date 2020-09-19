import os
import random
from dotenv import load_dotenv
from discord.ext import commands
import mysql.connector

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
@bot.command(name = "msg")
async def on_message(ctx):
    mycursor.execute("SELECT discord_id FROM Participants WHERE discord_id IS NOT NULL")

    discord_ids = mycursor.fetchall()

    for x in discord_ids:
        print(x)
        id=str(x)   
        user = bot.get_user(int(id[2:-3]))
        message = "eşitlik istiyorum"
        await user.send(message)    





bot.run(TOKEN)
