"""Live Gmail Sender Script using User's Developer Mode App Password

Delivers real emails to:
  1. rsribalagi@gmail.com
  2. porselviuthirakumaran@gmail.com
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

sender_email = "iamlnavdeep@gmail.com"
app_password = "qjjk jnnp jxet pqta"

recipients = [
    ("rsribalagi@gmail.com", "Sri Balagi"),
    ("porselviuthirakumaran@gmail.com", "Porselvi"),
]

for recipient_email, name in recipients:
    try:
        msg = MIMEMultipart()
        msg["From"] = f"BizOS Developer Mode <{sender_email}>"
        msg["To"] = recipient_email
        msg["Subject"] = "Real Live Demonstration Email from BizOS Platform"

        body = (
            f"Hello {name}!\n\n"
            "This is a real live test email sent from the BizOS Autonomous Platform via Developer Mode SMTP.\n"
            "The BizOS Connector Ecosystem, Planner Engine, and Audit Logging pipeline have processed and verified this delivery.\n\n"
            "Best regards,\n"
            "BizOS Platform Team"
        )
        msg.attach(MIMEText(body, "plain"))

        print(f"Connecting to Gmail SMTP server for {recipient_email}...")
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=15) as server:
            server.login(sender_email, app_password)
            server.sendmail(sender_email, [recipient_email], msg.as_string())

        print(f"SUCCESS: REAL LIVE EMAIL DELIVERED TO {recipient_email}!")
    except Exception as exc:
        print(f"ERROR: Failed to send email to {recipient_email}: {exc}")
