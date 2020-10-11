import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import mysql.connector
from dotenv import load_dotenv


load_dotenv()

subject = "Koç Deneme Turnuvası"
sender_email = "gsukayit@kutabteam.com"
password = "bizimDomain+1575"
logo_link = "https://media.discordapp.net/attachments/750073975379460251/756139668197867651/logo_uzun.jpg"
invite = "https://discord.gg/9wDF7C"
guide = "https://docs.google.com/document/d/1VX-_sNknvweAnf1vRZ45uAM0TdKWSLuGPC7Jx3w3SRg/edit?usp=sharing"


headers = {"Authorization": os.getenv("TABBYCAT_TOKEN")}
mydb = mysql.connector.connect(
    host="localhost",
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    database="debate")

mycursor = mydb.cursor()   



#info = {"name" : "Atakan Kara", "invite" : "https://www.google.com", "guide" : "https://www.youtube.com", "tabby_url" : "https://kutabteam.com", "unique_id" : "123456"}




text = """\
Merhaba {}


Koç Açık 2020 Çevrimiçi'ye hoşgeldin. Turnuva süreci discord üzerinden yürüyecek. 
Sunucuya <a href="{}">buradan</a> katılabilirsin. Turnuva sürecinde işine yarayabilecek teknik destek rehberine <a href="{}">buradan</a>  ulaşabilirsin. 
Bu turnuvada Tabbycat kullanacağız. Sana özel Tabbycat adresin <a href="{}">{}</a>  Kayıt olmak için, discord sunucusuna girdiğin zaman şunu yazman gerekecek:

!kayıt {}

İyi eğlenceler ve turnuvada başarılar
Koç Açık 2020 Çevrimiçi Tab Ekibi
"""
html = """\
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">

<head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
  <title>Kutabteam</title>
  <style type="text/css">
  body {{margin: 0; padding: 0; min-width: 100%!important;}}
  img {{height: auto;}}
  .content {{width: 100%; max-width: 600px;}}
  .header {{padding: 40px 30px 20px 30px;}}
  .innerpadding {{padding: 10px;}}
  .subhead {{font-size: 15px; color: #ffffff; font-family: sans-serif; letter-spacing: 10px;}}
  .h1, .h2, .bodycopy {{color: #153643; font-family: sans-serif;}}
  .h1 {{font-size: 33px; line-height: 38px; font-weight: bold;}}
  .h2 {{padding: 0 0 15px 0; font-size: 24px; line-height: 28px; font-weight: bold;}}
  .bodycopy {{font-size: 16px; line-height: 22px;}}
  .button {{text-align: center; font-size: 18px; font-family: sans-serif; font-weight: bold; padding: 0 30px 0 30px;}}

  .footer {{padding: 20px 30px 15px 30px;}}
  .footercopy {{font-family: sans-serif; font-size: 14px; color: #ffffff;}}
  .footercopy a {{color: #ffffff; text-decoration: underline;}}

  @media only screen and (max-width: 550px), screen and (max-device-width: 550px) {{
  body[yahoo] .hide {{display: none!important;}}
  body[yahoo] .buttonwrapper {{background-color: transparent!important;}}
  body[yahoo] .button {{padding: 0px!important;}}
  body[yahoo] .button a {{background-color: #e05443; padding: 15px 15px 13px!important;}}
  body[yahoo] .unsubscribe {{display: block; margin-top: 20px; padding: 10px 50px; background: #2f3942; border-radius: 5px; text-decoration: none!important; font-weight: bold;}}
  }}
    a{{
      text-decoration: none;
    }}
  </style>
</head>

<body yahoo bgcolor="white">
<table width="100%" bgcolor="white" border="0" cellpadding="0" cellspacing="0">
<tr>
  <td>
    <table bgcolor="white" class="content" align="center" cellpadding="0" cellspacing="0" border="0">
     <tr>
        <td class="innerpadding borderbottom">
          <img class="fix" src="{}" width="100%" border="0" alt="" />
        </td>
      </tr>
      <tr>
        <td class="innerpadding">
          <table width="100%" border="0" cellspacing="0" cellpadding="0">
            <tr>
              <td class="h2">
                Merhaba {},
              </td>
            </tr>
            <tr>
              <td class="bodycopy">
                Koç Açık 2020 Çevrimiçi'ye hoşgeldin. Turnuva süreci discord üzerinden yürüyecek. Sunucuya <a href="{}">buradan</a> katılabilirsin. Turnuva sürecinde işine yarayabilecek teknik destek rehberine <a href="{}">buradan</a>  ulaşabilirsin. Bu turnuvada Tabbycat kullanacağız. Sana özel Tabbycat adresin <a href="{}">{}</a>  Kayıt olmak için, discord sunucusuna girdiğin zaman şunu yazman gerekecek:
              </td>

            </tr>

            <tr height='50'></tr>

              <tr>

        <td>
          <table  align="center"  class="buttonwrapper" bgcolor="#e05443" border="0" cellspacing="0" cellpadding="0" >
                        <tr>
                          <td class="button" height="55">
                            !kayıt {}
                          </td>
                        </tr>
                      </table>

          </td>

          </tr>

          </table>

        </td>

      </tr>

<tr height='50'></tr>
      <tr>
        <td class="innerpadding bodycopy">
            İyi eğlenceler ve turnuvada başarılar
        </td>
      </tr>
      <tr>
        <td class="innerpadding bodycopy">
            Koç Açık 2020 Çevrimiçi Tab Ekibi
        </td>
      </tr>
      <tr>
        <td class="footer" bgcolor="#44525f">
          <table width="100%" border="0" cellspacing="0" cellpadding="0">
            <tr>
              <td align="center" class="footercopy">
                Kutabteam
              </td>
                <tr height='10'></tr>
                <td align="center" class="footercopy">
                <a align="center" href="https://kutabteam.com" class="unsubscribe"><font color="#ffffff">Unsubscribe</font></a>

              </td>
            </tr>

          </table>
        </td>
      </tr>
    </table>
    </td>
  </tr>
</table>
</body>
</html>

"""

context = ssl.create_default_context()


sql = "Select name, email, url_key, unique_id from Participants"
mycursor.execute(sql)
myresult= mycursor.fetchall()


tabbyurl = os.getenv("URL")
tournament = os.getenv("TOURNAMENT")


with smtplib.SMTP_SSL('smtp.zoho.com', 465, context=context) as server:
    server.login(sender_email, password)
    for x in myresult:
        name = x[0]
        receiver_email = x[1]
        tabby_url = f"{tabbyurl}/{tournament}/privateurls/{x[2]}/"
        unique_id = x[3]

        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = sender_email
        message["To"] = receiver_email

        part1 = MIMEText(text.format(logo_link, name, invite, guide, tabby_url, tabby_url, unique_id), "plain")
        part2 = MIMEText(html.format(logo_link, name, invite, guide, tabby_url, tabby_url, unique_id) , "html")

                
        message.attach(part1)
        message.attach(part2)
        message.add_header('List-Unsubscribe', '<mailto: unsubscribe@kutabteam.com?subject=unsubscribe>')

        server.sendmail(
            sender_email, receiver_email, message.as_string()
        )
        print("send")


print("finished")