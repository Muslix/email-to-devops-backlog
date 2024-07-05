from dotenv import load_dotenv, dotenv_values

# Daten aus der .env-Datei laden
load_dotenv('.env')
values = dotenv_values('.env')

# E-Mail Server Konfiguration
HOST = values.get('HOST')
USERNAME = values.get('USERNAME')
MAIL_PASSWORD = values.get('MAIL_PASSWORD')
MAILBOX = values.get('MAILBOX')

# Azure DevOps Konfiguration
ORGANIZATION = values.get('ORGANIZATION')
PROJECT = values.get('PROJECT')
ACCESS_TOKEN = values.get('ACCESS_TOKEN')
