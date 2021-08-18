#!/usr/bin/python

from datetime import datetime
from pathlib import Path

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import Resource, build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials


def authorize(token_path, credentials_path, scopes) -> Resource:
    creds = None

    if Path(token_path).exists():
        creds = Credentials.from_authorized_user_file(token_path, scopes)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path, scopes)
            creds = flow.run_local_server(port=0)

        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    return build('drive', 'v3', credentials=creds)


def get_files_by_name(drive_service, file_name, directory):
    files = []
    page_token = None

    while True:
        response = drive_service.files().list(
            q=f"name='{file_name}' and trashed=false and '{directory}' in parents",
            spaces='drive',
            fields='nextPageToken, files(id, modifiedTime)',
            pageToken=page_token
        ).execute()

        for file in response.get('files', []):
            files.append(file)

        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break

    return files


def get_newest_file_id(drive_service, file_name, directory):
    files = get_files_by_name(drive_service, file_name, directory)
    if not files:
        return None

    dates_list = []
    for file in files:
        modified_time = datetime.strptime(
            file.get('modifiedTime'), '%Y-%m-%dT%H:%M:%S.%f%z')
        dates_list.append(modified_time)

    dates_list.sort()

    for file in files:
        modified_time = datetime.strptime(
            file.get('modifiedTime'), '%Y-%m-%dT%H:%M:%S.%f%z')
        if modified_time == dates_list[-1]:
            return file.get('id')


def create_file(drive_service, file_path, directory=None):
    file_name = Path(file_path).name
    file_metadata = {'name': file_name}
    if directory:
        file_metadata['parents'] = [directory]

    drive_service.files().create(
        body=file_metadata,
        media_body=MediaFileUpload(file_path)
    ).execute()


def update_file(drive_service, file_path, file_id):
    file_name = Path(file_path).name
    file_metadata = {'name': file_name}
    drive_service.files().update(
        body=file_metadata,
        media_body=MediaFileUpload(file_path),
        fileId=file_id
    ).execute()
