#!/usr/bin/python

from pathlib import Path

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import Resource, build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials


def authorize(token_path, credentials_path, scopes):
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


class DriveFilesSvc:

    def __init__(self, drive_service):
        self.drive_service = drive_service

    @staticmethod
    def get_filename_metadata(file_path):
        return {'name': Path(file_path).name}

    def get_files_by_name(self, file_name, directory):
        files = []
        page_token = None

        while True:
            response = self.drive_service.files().list(
                q=f"name='{file_name}' and trashed=false and '{directory}' in parents",
                spaces='drive',
                fields='nextPageToken, files(id, size, modifiedTime)',
                pageToken=page_token
            ).execute()

            for file in response.get('files', []):
                files.append(file)

            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break

        return files

    def create_file(self, file_path, directory=None):
        file_metadata = self.get_filename_metadata(file_path)
        if directory:
            file_metadata['parents'] = [directory]

        self.drive_service.files().create(
            body=file_metadata,
            media_body=MediaFileUpload(file_path)
        ).execute()

    def update_file(self, file_path, file_id):
        self.drive_service.files().update(
            body=self.get_filename_metadata(file_path),
            media_body=MediaFileUpload(file_path),
            fileId=file_id
        ).execute()
