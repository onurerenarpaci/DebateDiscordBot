import os
import smtplib
from dotenv import load_dotenv
from email.message import EmailMessage
import imghdr

load_dotenv()
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

msg = EmailMessage()
msg['Subject'] = 'Test subject'
msg['From'] = EMAIL_ADDRESS
msg['To'] = 'onurerenarpaci@hotmail.com'
msg.set_content('Test body')

with open('/home/onur/Desktop/DebateDiscordBot/Learning/Onur_Learning/mail/debate.jpeg', 'rb') as f:
    file_data = f.read
    file_type = imghdr.what(f.name)
    print(file_type)
    file_name = f.name

#msg.add_attachment(file_data, maintype='image', subtype=file_type)
msg.add_attachment(file_data, maintype='image', subtype='jpeg')

with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
    smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    smtp.send_message(msg)