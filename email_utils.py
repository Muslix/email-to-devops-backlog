import email
from email.header import decode_header

def extract_main_body(text):
    parts = text.split('-- \n', 1)
    return parts[0] if parts else text

def get_email_body(message):
    if message.is_multipart():
        for part in message.walk():
            ctype = part.get_content_type()
            cdispo = str(part.get('Content-Disposition'))
            if ctype == 'text/plain' and 'attachment' not in cdispo:
                body = part.get_payload(decode=True).decode()
                return extract_main_body(body)
    else:
        body = message.get_payload(decode=True).decode()
        return extract_main_body(body)
