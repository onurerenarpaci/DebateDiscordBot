import os, discord
from dotenv import load_dotenv
from discord.ext import commands
import mysql.connector
import messages

load_dotenv()


TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = "deneme-turnuva-atakan"  

admin = int(os.getenv("ADMIN_ID"))
bot = commands.Bot(command_prefix="!")

@bot.event
async def on_ready():
    global guild
    guild = discord.utils.get(bot.guilds, name=GUILD)
    print(f"{bot.user.name} has connected to Discord!")    


@bot.command(name='test')
async def test(ctx):
   for x in guild.roles:
       print(x.name)


bot.run(TOKEN)