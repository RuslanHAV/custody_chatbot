from __future__ import print_function

import os.path
import requests
import io

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive']

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
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.json', 'w') as token:
        token.write(creds.to_json())


def get_files(folder_id):
    try:
        service = build('drive', 'v3', credentials=creds)
        # Call the Drive v3 API
        results = service.files().list(q="'" + folder_id + "' in parents and mimeType='application/pdf'",
                                       #    pageSize=10, fields="nextPageToken, files(id, name)").execute()
                                       fields="files(id, name)").execute()
        items = results.get('files', [])
        return items

    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f'An error occurred: {error}')

    return []


def get_file_path(file_id, file_name):
    try:
        path = './files/%s.pdf' % file_id
        if file_name.endswith(".pdf") == False or os.path.exists(path) == True:
            return None
        service = build('drive', 'v3', credentials=creds)
        request = service.files().get_media(fileId=file_id)
        with open(path, 'wb') as file:
            downloader = MediaIoBaseDownload(file, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                print(
                    F'Download {int(status.progress() * 100)} of {file_name}.')

        return path

    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f'An error occurred: {error}')

    return None
