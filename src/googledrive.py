from pathlib import Path

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import Resource, build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials


def authorize(token: str, credentials: str, scopes: list[str]) -> Resource:
    """
        Creates service for interaction with google drive

        Parameters: 
        token (str): system path to json file that contains authentication token
        credentials (str): system path to json file that contains credentials for authentication with google drive
        scopes (list[str]): list of permissions for the app on google drive

        Returns:
        Resource: object for interaction with google drive api
    """

    creds = None

    if Path(token).exists():
        creds = Credentials.from_authorized_user_file(token, scopes)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials, scopes)
            creds = flow.run_local_server(port=0)

        with open(token, 'w') as token:
            token.write(creds.to_json())

    return build('drive', 'v3', credentials=creds)


class DriveFilesSvc:
    """
        Class for interaction with files located on google drive
    """

    def __init__(self, drive_svc: Resource) -> None:
        """
            Initializes class fields

            Parameters:
            drive_svc (Resource): object for interaction with google drive api

            Returns:
            None
        """

        self.drive_svc = drive_svc

    @staticmethod
    def get_file_metadata(file: str) -> dict:
        """
            Returns file metadata containing file name

            Parameters:
            file (str): system path to a file

            Returns:
            dict: dictionary containing key:'name' and value of file parameter
        """

        return {'name': Path(file).name}

    def get_files_by_name(self, name: str, directory: str) -> list[dict]:
        """
            Returns list of files metadata that match specified name and directory

            Parameters:
            name (str): file name
            directory (str): google drive directory id

            Returns:
            list: list of dictionaries containing file metadata (id, size, modifiedTime)
        """

        files = []
        page_token = None

        while True:
            response = self.drive_svc.files().list(
                q=f"name='{name}' and trashed=false and '{directory}' in parents",
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

    def create_file(self, file: str, directory: str) -> None:
        """
            Uploads file to google drive

            Parameters:
            file (str): system path to a file
            directory (str): google drive directory id

            Returns:
            None
        """

        file_metadata = self.get_file_metadata(file)
        file_metadata['parents'] = [directory]

        self.drive_svc.files().create(
            body=file_metadata,
            media_body=MediaFileUpload(file)
        ).execute()

    def update_file(self, file: str, id: str) -> None:
        """
            Updates file on google drive

            Parameters:
            file (str): system path to a file
            id (str): google drive file id
        """

        self.drive_svc.files().update(
            body=self.get_file_metadata(file),
            media_body=MediaFileUpload(file),
            fileId=id
        ).execute()
