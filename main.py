import imaplib
import time
import email_utils
import azure_devops
import config
import email
from email.header import decode_header
from log_config import setup_logging
logger = setup_logging()

def check_emails(mail):
    mail.select(config.MAILBOX)
    status, messages = mail.search(None, 'UnSeen')
    if status == "OK":
        for num in messages[0].split():
            status, data = mail.fetch(num, '(RFC822)')
            if status == "OK":
                msg = email.message_from_bytes(data[0][1])
                subject = decode_header(msg['subject'])[0][0]
                if isinstance(subject, bytes):
                    subject = subject.decode()
                body = email_utils.get_email_body(msg)
                logger.info('Found new email: %s', subject)
                azure_devops.create_devops_issue(subject, body, config.ACCESS_TOKEN, config.ORGANIZATION, config.PROJECT)
                mail.store(num, '+FLAGS', '\\Seen')

def main():
    mail = imaplib.IMAP4_SSL(config.HOST)
    mail.login(config.USERNAME, config.MAIL_PASSWORD)
    try:
        while True:
            check_emails(mail)
            time.sleep(10)
    finally:
        mail.logout()

if __name__ == '__main__':
    main()
