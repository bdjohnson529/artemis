"""
alert.py
====================================
User alerts
"""

import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart



def sendEmail(host, sender_email, recipient_email, subject, msg_html):

    msg = MIMEMultipart()
    msg.attach(MIMEText(msg_html, 'html'))


    # Define email details
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = recipient_email


    # Send the message
    s = smtplib.SMTP(host)
    s.sendmail(sender_email, recipient_email, msg.as_string())
    s.quit()
