import imaplib
import time
import email_utils
import azure_devops
import config
import email
from datetime import datetime, timedelta
from email.header import decode_header
from log_config import setup_logging
logger = setup_logging()
last_submissions = {}

def allowed_to_submit(email):
    now = datetime.now()
    limit = timedelta(minutes=10)
    if email in last_submissions:
        if now - last_submissions[email] < limit:
            return False
    last_submissions[email] = now
    return True

def cleanup_submissions():
    now = datetime.now()
    limit = timedelta(minutes=10)
    to_delete = [email for email, time in last_submissions.items() if now - time > limit]
    for email in to_delete:
        del last_submissions[email]
    logger.info(f"Cleaned up {len(to_delete)} outdated submissions.")

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
                body, images = email_utils.get_email_content(msg)
                sender = msg['from']
                logger.info('Found new email: %s', subject)
                if not azure_devops.is_spam(body):
                    if allowed_to_submit(sender):
                        bug_id = azure_devops.create_devops_issue(subject, body, sender, config.ACCESS_TOKEN, config.ORGANIZATION, config.PROJECT)
                        if bug_id:
                            for filename, image_data in images:
                                azure_devops.upload_attachment_to_devops(config.ORGANIZATION, config.PROJECT, bug_id, filename, image_data,  config.ACCESS_TOKEN)

                    else:
                        logger.info(f"Submission denied for {sender}. Rate limit exceeded.")
                else:
                    logger.info('Email is spam. Ignoring.')
                mail.store(num, '+FLAGS', '\\Seen')

def main():
    mail = imaplib.IMAP4_SSL(config.HOST)
    mail.login(config.USERNAME, config.MAIL_PASSWORD)
    try:
        while True:
            check_emails(mail)
            cleanup_submissions()
            time.sleep(10)
    finally:
        mail.logout()

if __name__ == '__main__':
    main()
