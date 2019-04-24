# -*- coding: UTF-8 -*-
#
# 邮件发送服务
# ==========
#

from flask import Flask
from flask_mail import Mail, Message


class MailAlarm:

    def __init__(self, passwd=""):

        self.app = Flask(__name__)
        self.app.config.update(
                DEBUG=False,
                MAIL_SERVER='smtp.live.com',
                MAIL_PROT=25,
                MAIL_USE_TLS=True,
                MAIL_USE_SSL=False,
                MAIL_USERNAME='shenwei0329@hotmail.com',
                MAIL_PASSWORD=passwd,
                MAIL_DEBUG=True,
                MAIL_ASCII_ATTACHMENTS=False,
            )
        self.app.app_context().push()
        self.mail = Mail(self.app)
        self.msg = Message("Caution information by AI@Home V 0.8", sender="shenwei0329@hotmail.com", recipients=["shenwei0329@hotmail.com"])

    def sendmail(self, body="Alarm!!!", html="<b>Alarm!!!</b>"):

        self.msg.body = body
        self.msg.html = html
        self.mail.send(self.msg)


#
# Eof
#
