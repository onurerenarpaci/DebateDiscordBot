import discord
import datetime


register_message = discord.Embed(
    colour = discord.Colour(0xcc0200), #F2F2F2 #cc0200 #8C2730
    timestamp=datetime.datetime.utcfromtimestamp(1600352953)
) 

register_message.set_image(url="https://media.discordapp.net/attachments/750073975379460251/756139668197867651/logo_uzun.jpg")
register_message.set_author(name="Koç Açık 2020 Çevrimiçi", icon_url="https://media.discordapp.net/attachments/750073975379460251/756152643877077032/sadece_logo.jpg")
register_message.add_field(name="Koç Açık 2020 Çevrimiçi'ye hoşgeldin.", value="Turnuva kaydın tamamlandı. Turnuva sırasındaki herhangi bir problemini \"Yardım\" kanallarını kullanarak bize iletebilirsin.\nBol şans!", inline=False)


