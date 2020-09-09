import os, discord
from dotenv import load_dotenv
from discord.ext import commands
import mysql.connector

load_dotenv()


headers = {"Authorization": os.getenv("TABBYCAT_TOKEN")}
mydb = mysql.connector.connect(
    host="localhost",
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    database="munazara")

mycursor = mydb.cursor()

TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix="!")

@bot.event
async def on_ready():
    print(f"{bot.user.name} has connected to Discord!")

@bot.command(name='register')
async def register(ctx, unique_id):

    sql = "update speakers set discord_id = %s where unique_id = %s"
    val = (ctx.author.id, unique_id)
    mycursor.execute(sql,val)

    if(mycursor.rowcount >= 1):
        mydb.commit()
        await ctx.send("Kayıt başarılı.")
    else:
        await ctx.send("Kayıt başarısız, id bulunamadı.")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument) :  ## IT HANDLES ALL MISSING ARGUMENT EXCEPTIONS.
        await ctx.send("Kayıt yapabilmek için kayıt komutundan sonra id'nizi yazın. Örnek: !kayıt 123456")
bot.run(TOKEN)