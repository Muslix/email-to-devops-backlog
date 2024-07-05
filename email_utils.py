import email
from email.header import decode_header
import mimetypes


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

def get_email_content(msg):
    body = ""
    images = []
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                payload = part.get_payload(decode=True)
                charset = part.get_content_charset() or 'utf-8'
                body += payload.decode(charset, errors='replace')
            elif content_type.startswith("image/"):
                image_data = part.get_payload(decode=True)
                filename = part.get_filename()
                if not filename:
                    ext = mimetypes.guess_extension(part.get_content_type())
                    filename = f"image{len(images)}{ext}"
                images.append((filename, image_data))
    else:
        payload = msg.get_payload(decode=True)
        charset = msg.get_content_charset() or 'utf-8'
        body = payload.decode(charset, errors='replace')

    return body, images
