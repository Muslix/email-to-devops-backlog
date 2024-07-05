import imaplib
import email
from email.header import decode_header
import time
import requests
import base64
from dotenv import load_dotenv
import os

# Daten aus der .env-Datei laden
load_dotenv()

# E-Mail Server Konfiguration
host = os.getenv('HOST')
username = os.getenv('USERNAME')
password = os.getenv('MAIL_PASSWORD')
mailbox = os.getenv('MAILBOX')

# Azure DevOps Konfiguration
organization = os.getenv('ORGANIZATION')
project = os.getenv('PROJECT')
personal_access_token = os.getenv('ACCESS_TOKEN')

def extract_main_body(text):
    # Trennen des Texts an der Standard-Signaturgrenze
    parts = text.split('-- \n', 1)
    return parts[0] if parts else text

def get_email_body(message):
    if message.is_multipart():
        for part in message.walk():
            ctype = part.get_content_type()
            cdispo = str(part.get('Content-Disposition'))
            if ctype == 'text/plain' and 'attachment' not in cdispo:
                body = part.get_payload(decode=True).decode()
                return extract_main_body(body)  # Haupttext extrahieren
    else:
        body = message.get_payload(decode=True).decode()
        return extract_main_body(body)


def check_emails(mail):
    mail.select(mailbox)  # Wähle das Postfach aus
    # Suche nach ungelesenen E-Mails
    status, messages = mail.search(None, 'UnSeen')
    if status == "OK":
        for num in messages[0].split():
            status, data = mail.fetch(num, '(RFC822)')
            if status == "OK":
                msg = email.message_from_bytes(data[0][1])

                subject = decode_header(msg['subject'])[0][0]
                if isinstance(subject, bytes):
                    subject = subject.decode()
                body = get_email_body(msg)
                print("Neue E-Mail gefunden:", subject)

                # Funktion zum Erstellen eines Azure DevOps Issues aufrufen
                create_devops_issue(subject, body, personal_access_token, organization, project)
                mail.store(num, '+FLAGS', '\\Seen')  # Markiere als gelesen

def create_devops_issue(title, description, personal_access_token, organization, project):
    url = f"https://dev.azure.com/{organization}/{project}/_apis/wit/workitems/$Issue?api-version=6.0"
    b64_pat = base64.b64encode(bytes(f":{personal_access_token}", 'utf-8')).decode('ascii')
    headers = {
        "Authorization": f"Basic {b64_pat}",
        "Content-Type": "application/json-patch+json"
    }
    payload = [
        {
            "op": "add",
            "path": "/fields/System.Title",
            "value": title
        },
        {
            "op": "add",
            "path": "/fields/System.Description",
            "value": description
        }
    ]
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        print("Azure DevOps Issue erfolgreich erstellt.")
    else:
        print("Fehler beim Erstellen des Azure DevOps Issues:")
        print("Body:", description)
        print("Titel:", title)
        print("Response:", response)


def main():
    # Verbindung zum Mail-Server
    mail = imaplib.IMAP4_SSL(host)
    mail.login(username, password)
    try:
        while True:
            check_emails(mail)
            time.sleep(10)
    finally:
        mail.logout()

if __name__ == '__main__':
    main()
