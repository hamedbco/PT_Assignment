from flask import Flask
from flask_mail import Mail, Message
from config import MailConfig

app = Flask(__name__)

def sendMail(getUserEmailResult, automobile, part, link):
    try:
        emailList = list()
        for email in getUserEmailResult:
            emailList.append(email[0])

        app.config['MAIL_SERVER'] = MailConfig.MAIL_SERVER
        app.config['MAIL_PORT'] = MailConfig.MAIL_PORT
        app.config['MAIL_USERNAME'] = MailConfig.MAIL_USERNAME
        app.config['MAIL_PASSWORD'] = MailConfig.MAIL_PASSWORD
        app.config['MAIL_USE_SSL'] = MailConfig.MAIL_USE_TLS

        mail = Mail()
        mail.init_app(app)

        for email in getUserEmailResult:
            # Email Content
            msg = Message('Pedram Taheri',
                          sender=MailConfig.SENDER,
                          recipients=emailList)
            msg.body = f"Hi Dear User\nA New File was Upload for a AutoMobile Part\nFile Infomations\nAutoMobile's Name: {automobile[0]}\nPart's Name: {part[0]}\nDownload File Link: {link}"
            mail.send(msg)

    except Exception as e:
        print('Can Not Send Email!')
