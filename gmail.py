# Libraries for accessing to Google API
from __future__ import print_function
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Email creation
import mimetypes
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import base64
import os.path

from config.credentials import GMAIL_SENDER, GMAIL_TO



from main import *

# Save the path of the current working directory as a string
cwd = str(os.getcwd())

# Gmail Credentials
gmail_client_secret = cwd + r'\config\client_secret.json'

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']


def initialize_gmail(gmail_creds):
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(gmail_creds, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)

    return service


def create_message(sender, to, subject, message_text):
    """Create a message for an email.

    Args:
    sender: Email address of the sender.
    to: Email address of the receiver.
    subject: The subject of the email message.
    message_text: The text of the email message.

    Returns:
    An object containing a base64url encoded email object.
    """
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject

    raw = base64.urlsafe_b64encode(message.as_bytes())

    return {'raw': raw.decode()}


def create_message_with_attachment(sender, to, subject, message_text, file):
    """Create a message for an email.

    Args:
    sender: Email address of the sender.
    to: Email address of the receiver.
    subject: The subject of the email message.
    message_text: The text of the email message.
    file: The path to the file to be attached.

    Returns:
    An object containing a base64url encoded email object.
    """
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject

    msg = MIMEText(message_text)
    message.attach(msg)

    content_type, encoding = mimetypes.guess_type(file)


    if content_type is None or encoding is not None:
        content_type = 'application/octet-stream'
        main_type, sub_type = content_type.split('/', 1)
    else:
        main_type, sub_type = content_type.split('/', 1)

    if main_type == 'text':
        fp = open(file, 'rb')
        msg = MIMEText(fp.read(), _subtype=sub_type)
        fp.close()
        filename = os.path.basename(file)
        msg.add_header('Content-Disposition', 'attachment', filename=filename)
        message.attach(msg)
    elif main_type == 'image':
        fp = open(file, 'rb')
        msg = MIMEImage(fp.read(), _subtype=sub_type)
        fp.close()
        filename = os.path.basename(file)
        msg.add_header('Content-Disposition', 'attachment', filename=filename)
        message.attach(msg)
    elif main_type == 'audio':
        fp = open(file, 'rb')
        msg = MIMEAudio(fp.read(), _subtype=sub_type)
        fp.close()
        filename = os.path.basename(file)
        msg.add_header('Content-Disposition', 'attachment', filename=filename)
        message.attach(msg)
    else:
        fp = open(file, 'rb')
        msg = MIMEBase(main_type, sub_type)
        msg.set_payload(fp.read())
        fp.close()
        filename = os.path.basename(file)
        msg.add_header('Content-Disposition', 'attachment', filename=filename)
        message.attach(msg)

    raw = base64.urlsafe_b64encode(message.as_bytes())

    return {'raw': raw.decode()}


def create_message_with_df_in_body(sender, to, subject, message_text, df):
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject

    style = """
    table {
        border: 1px solid black;
        border-collapse: collapse;
    }
    tr:hover {background-color: yellow;}
    th {
        text-align: center;
        background-color: #04AA6D;
        color: white;
        padding: 10px
    }
    td {
        text-align: center;
        padding: 10px
    }
"""

    html = """<html>
<head>
<style>{css}</style>
</head>
<body>
    <h1>{header}</h1>
    <p>
        {message}
    </p>
    {html_df}
</body>
</html>
    """.format(message=message_text, header="GroupMe Statistics", html_df=df.to_html(), css=style)
    print(html)
    html = MIMEText(html, 'html')
    message.attach(html)

    raw = base64.urlsafe_b64encode(message.as_bytes())

    return {'raw': raw.decode()}


def send_message(service, user_id, message):
    """Send an email message.

    Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    message: Message to be sent.

    Returns:
    Sent Message.
    """
    message = (service.users().messages().send(userId=user_id, body=message).execute())
    print('Message Id: %s' % message['id'])
    return message


def test():
    top_ten = get_top_ten_likes("month", groupID)
    top_ten = organize_attachments(top_ten)

    # Create a connection in order to interact with Gmail
    service = initialize_gmail(gmail_client_secret)

    subject = "TEST: GroupMe Statistics"
    message_text = "This is a test email for the GroupMe Statistics project."
    # file = r"C:\Users\gbach\Downloads\domain-model.png"

    # gmail_message = create_message(GMAIL_SENDER, GMAIL_TO, subject, message_text)
    # gmail_message_with_attachment = create_message_with_attachment(GMAIL_SENDER, GMAIL_TO, subject, message_text, file)
    gmail_message_with_df = create_message_with_df_in_body(GMAIL_SENDER, GMAIL_TO, subject, message_text, top_ten)

    sent = send_message(service=service, user_id=GMAIL_SENDER, message=gmail_message_with_df)
    print(sent)

    return


test()
