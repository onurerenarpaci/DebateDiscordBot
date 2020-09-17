import os, discord
from dotenv import load_dotenv
from discord.ext import commands
import mysql.connector
import traceback


load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix="!")
client = discord.Client()


@bot.command(name='kayıt')
async def register(ctx):
    await ctx.author.edit(nick="yeni isim")


bot.run(TOKEN)