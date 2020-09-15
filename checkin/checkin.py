import aiohttp
import asyncio
import tabbyurl

channelId = "" #Checkin channel id
checkinStatus = False # True = Open, False = Close
checkinMessage = None
guild = None # discord.utils.get(client.guilds, name=GUILD)
checkinDuration = 30 # 30 minutes

async def checkin():
    # adds the checkin messaege and green reaction
    global checkinMessage
    global checkinStatus
    checkinStatus = True
	message = await guild.get_channel(channelId).send("Check-in yapmak için alttaki 🟩 butonuna basın")
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
    await guild.get_channel(channelId).send("Check-in süresi doldu.")
    await checkinUpdate


async def on_reaction_add(reaction, user):
    if (not checkinStatus) or (not reaction.message.id == checkinMessage) or (not str(reaction.emoji) == "🟩") or user == client.user:
	    return

    val = (str(user.id))
    mycursor.execute("SELECT checkin FROM Participants WHERE discord_id == %s", val)
    myresult = mycursor.fetchall()

    if myresult[0][0]:
        return
    
    val = (True, str(user.id))
    mycursor.execute("UPDATE Participants SET checkin = %s WHERE discord_id = %s", val)
    myresult = mycursor.fetchall()

    if user.dm_channel == None: 
		await user.create_dm()
	await user.dm_channel.send("You have succesfully checked-in.")

    
async def checkinUpdate():
    mycursor.execute("SELECT id FROM Participants WHERE checkin = True AND role = speaker")
    myresult = mycursor.fetchall()
    session = aiohttp.ClientSession()
    
    for x in myresult:
        url = f'{tabbyurl.url}/api/v1/tournaments/{tabbyurl.tournament}/speakers/{x[0]}/checkin'
        async with session.put(url, headers=headers) as resp:
            print(f'id={x[0]} status={resp.status}')
            print(await resp.text())

    mycursor.execute("SELECT id FROM Participants WHERE checkin = True AND role = jury")
    myresult = mycursor.fetchall()

    for x in myresult:
        url = f'{tabbyurl.url}/api/v1/tournaments/{tabbyurl.tournament}/adjudicators/{x[0]}/checkin'
        async with session.put(url, headers=headers) as resp:
            print(f'id={x[0]} status={resp.status}')
            print(await resp.text())

    session.close()




