import os, discord
from dotenv import load_dotenv
from discord.ext import commands
import mysql.connector
load_dotenv()
dirname = os.path.dirname(__file__)

headers = {"Authorization": os.getenv("TABBYCAT_TOKEN")}
mydb = mysql.connector.connect(
    host="localhost",
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    database="debate")

mycursor = mydb.cursor()
GUILD = "draw deneme"#os.getenv("DISCORD_GUILD")
TOKEN = os.getenv('DISCORD_TOKEN')
admin = int(os.getenv("ADMIN_ID"))
bot = commands.Bot(command_prefix="!")

@bot.event
async def on_ready():
    global guild
    guild = discord.utils.get(bot.guilds, name=GUILD)
    print(f"{bot.user.name} has connected to Discord!")    
    
@bot.command(name='kayıt')
async def register(ctx, unique_id):
    user = ctx.author
    sql = "update Participants set discord_id = %s, checkin = %s where unique_id = %s"
    val = (user.id, True, unique_id)
    mycursor.execute(sql,val)

    if(mycursor.rowcount == 1):
        mydb.commit()
        sql = "select team, name, role, institution from Participants where unique_id = %s"
        val = (unique_id,)
        mycursor.execute(sql,val)
        user_info = mycursor.fetchone()
        print(user_info[0],user_info[1])
        if user_info[2] == "speaker":

            #editting name
            team_name = user_info[0].split(" ")
            user_name = user_info[1].split(" ")
            teams_turn = True
            i,j = 0,0
            total_lenght = 1
            while total_lenght < 28:
                if teams_turn and i < len(team_name):
                    total_lenght += (len(team_name[i])+1)
                    i += 1
                    teams_turn = False
                elif j < len(user_name):
                    total_lenght += (len(user_name[j])+1)
                    j += 1
                    teams_turn = True
                elif teams_turn == False and j == len(user_name):
                    teams_turn = True
                if j == len(user_name) and i == len(team_name):
                    break
                    
            team = " ".join(team_name[0:i])
            name = " ".join(user_name[0:j])
            if total_lenght > 32:
                dif = total_lenght - 32
                if len(team) > 15:
                    team = team[0:-dif]
                else:
                    name = name[0:-dif]
            final = team + " - " + name

            await user.edit(nick=final)
            for role in guild.roles:    
                if(role.name == "Konuşmacı"):
                    await user.add_roles(role)
                    break
        elif user_info[2] == "jury":
            await user.edit(nick=user_info[1])
            for role in guild.roles:
                if (role.name == 'Jüri'):
                    await user.add_roles(role)
                    break
                
        sql = "Select name, channel_type, type, id from private_rooms where name = %s or name = %s "
        val = (user_info[0], user_info[3])
        mycursor.execute(sql, val)

        room_info = mycursor.fetchall()
        for room in room_info:
            if room[1] == "text_channel":
                await guild.get_channel(room[3]).set_permissions(user, read_messages=True, send_messages=True)
            else:
                await guild.get_channel(room[3]).set_permissions(user, view_channel=True, connect=True, speak=True, stream=True)
        await user.create_dm()
      #  await user.dm_channel.send(embed=ge)
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



@bot.command(name='geribildirim')
async def feedback(ctx):
    await ctx.send("```Size ait Tabbycat bağlantısını kullanarak geri bildirim verebilirsiniz.```")







async def send_error_message(ctx, error):
    user = bot.get_user(admin)
    await user.create_dm()
    await user.dm_channel.send(f"{ctx.message}\n{ctx.message.author.nick}\n{ctx.args}\n!{ctx.command}\n{error}")



bot.run(TOKEN)



mydb.commit()
mycursor.close()
mydb.close()
print("Connection closed.")

