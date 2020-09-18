import os, discord
from dotenv import load_dotenv
from discord.ext import commands
import mysql.connector
import messages
load_dotenv()
dirname = os.path.dirname(__file__)

headers = {"Authorization": os.getenv("TABBYCAT_TOKEN")}
mydb = mysql.connector.connect(
    host="localhost",
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    database="debate")

mycursor = mydb.cursor()

TOKEN = os.getenv('DISCORD_TOKEN')
admin = int(os.getenv("ADMIN_ID"))
bot = commands.Bot(command_prefix="!")
guild_id = 0

@bot.event
async def on_ready():
    global guild_id
    print(f"{bot.user.name} has connected to Discord!")    
    
@bot.command(name='kayıt')
async def register(ctx, unique_id):
    user = ctx.author
    sql = "update Participants set discord_id = %s where unique_id = %s"
    val = (user.id, unique_id)
    mycursor.execute(sql,val)

    sql = "select team,name from Participants where unique_id = %s"
    val = (unique_id,)
    mycursor.execute(sql,val)
    myresult = mycursor.fetchone()
    print(myresult[0],myresult[1])
    if(mycursor.rowcount >= 1):
        mydb.commit()   
        await user.create_dm()
        await user.dm_channel.send(embed=messages.register_message)
        await user.edit(nick=myresult[0]+" - "+myresult[1])
        await ctx.send("Kayıt başarılı.")
    else:
        await ctx.send("Kayıt başarısız, id bulunamadı.")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument) :
        if(str(error.param) == "unique_id"):
            await ctx.send("Kayıt yapabilmek için kayıt komutundan sonra id'nizi yazın. Örnek: !kayıt 123456")
        else:
            await send_error_message(ctx, error)
    elif isinstance(error, discord.ext.commands.CommandOnCooldown):
        await ctx.send(f"Çok hızlı yazdınız. Lütfen {int(error.retry_after)} saniye sonra tekrar deneyiniz.")
    else:
        await send_error_message(ctx, error)



#@bot.command(name='test')
#    async def test(ctx):







async def send_error_message(ctx, error):
    user = bot.get_user(admin)
    await user.create_dm()
    await user.dm_channel.send(f"{ctx.message}\n{ctx.message.author.nick}\n{ctx.args}\n!{ctx.command}\n{error}")



bot.run(TOKEN)