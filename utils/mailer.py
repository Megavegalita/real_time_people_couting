import smtplib
import json
from typing import Dict, Any

# initiate features config.
with open("utils/config.json", "r") as file:
    config: Dict[str, Any] = json.load(file)


class Mailer:
    """
    Email alert system for people counting.
    
    Sends email notifications when the people count exceeds
    the configured threshold.
    """

    def __init__(self) -> None:
        """Initialize email sender with SMTP configuration."""
        self.email: str = config["Email_Send"]
        self.password: str = config["Email_Password"]
        self.port: int = 465
        self.server: smtplib.SMTP_SSL = smtplib.SMTP_SSL('smtp.gmail.com', self.port)

    def send(self, mail: str) -> None:
        """
        Send alert email.
        
        Args:
            mail: Recipient email address
        """
        self.server = smtplib.SMTP_SSL('smtp.gmail.com', self.port)
        self.server.login(self.email, self.password)
        # message to be sent
        SUBJECT: str = 'ALERT!'
        TEXT: str = f'People limit exceeded in your building!'
        message: str = 'Subject: {}\n\n{}'.format(SUBJECT, TEXT)
        # send the mail
        self.server.sendmail(self.email, mail, message)
        self.server.quit()
