import config
from datetime import datetime
from pathlib import Path

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import Resource, build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials


def authorize() -> Resource:
    creds = None

    if Path(config.TOKEN).exists():
        creds = Credentials.from_authorized_user_file(
            config.TOKEN, ['https://www.googleapis.com/auth/drive.file'])

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                config.CREDENTIALS, ['https://www.googleapis.com/auth/drive.file'])
            creds = flow.run_local_server(port=0)

        with open(config.TOKEN, 'w') as token:
            token.write(creds.to_json())

    return build('drive', 'v3', credentials=creds)


#TODO check if directory matches 
def get_files_by_name(drive_service: Resource, file_name: str) -> list:
    ''' 
        Returns all the files located on google drive that match the file_name.
        Rejects trashed files.

        Parameters: 
            drive_service (Resource): a class for interacting with a google drive API
            file_name (str): Self explanatory

        Returns:
            files (list): list containing files metadata
    '''

    files = []
    page_token = None

    while True:
        response = drive_service.files().list(
            q=f"name='{file_name}'",
            spaces='drive',
            fields='nextPageToken, files(id, modifiedTime, trashed)',
            pageToken=page_token
        ).execute()

        for file in response.get('files', []):
            if not file.get('trashed'):
                files.append(file)

        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break

    return files


def get_newest_file_id(drive_service: Resource, file_name: str) -> str:
    ''' 
        Returns id of newest file (modification time) with name file_name.

        Parameters: 
            drive_service (Resource): a class for interacting with a google drive API
            file_name (str): Self explanatory

        Returns:
            id (str): id of a file in a string
    '''
    files = get_files_by_name(drive_service, file_name)
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
