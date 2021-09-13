from datetime import datetime, timezone
from glob import glob
from pathlib import Path

import config
import googledrive as drive
from googleapiclient.discovery import Resource


SCOPES = ['https://www.googleapis.com/auth/drive.file']
AUTH_DIR = Path(__file__).parent / '..' / 'auth'
CREDENTIALS = AUTH_DIR / 'credentials.json'
TOKEN = AUTH_DIR / 'token.json'
DATE_FORMAT = '%Y-%m-%dT%H:%M:%S.%f%z'


def get_newest_file(drive_files: list[dict]) -> dict:
    """
        Returns google drive file with newest modification time

        Parameters:
        drive_files (list[dict]): list of dictionaries containing google drive file metadata

        Returns:
        dict: dictionary containing google drive file metadata
    """

    if not drive_files:
        return {}

    dates_list = []

    for file in drive_files:
        modified_time = datetime.strptime(file.get('modifiedTime'), DATE_FORMAT)
        dates_list.append(modified_time)

    dates_list.sort()

    for file in drive_files:
        modified_time = datetime.strptime(file.get('modifiedTime'), DATE_FORMAT)
        if modified_time == dates_list[-1]:
            return file

    return {}


def file_changed(local_file: str, drive_file: dict) -> bool:
    """
        Checks whether file located on google drive is different from the one on hard disk

        Parameters:
        local_file (str): system path to a file
        drive_file (dict): google drive file metadata

        Returns:
        bool: whether files differ or not
    """

    local_metadata = Path(local_file).stat()

    size_changed = int(drive_file.get('size')) != local_metadata.st_size
    if size_changed:
        return True

    local_mtime = datetime.fromtimestamp(local_metadata.st_mtime, tz=timezone.utc)
    drive_mtime = datetime.strptime(drive_file.get('modifiedTime'), DATE_FORMAT)

    return local_mtime > drive_mtime


def upload_files(drive_svc: Resource, paths: list[str], directory: str) -> None:
    """
        Uploads files to google drive

        Parameters:
        drive_svc (Resource): object for interaction with google drive api
        paths (list[str]): list of system paths
        directory (str): google drive directory id

        Returns:
        None
    """

    for path in paths:
        if Path(path).is_dir():
            continue

        files_svc = drive.DriveFilesSvc(drive_svc)
        file_name = Path(path).name

        print(f'Checking whether {file_name} exists on google drive...')
        drive_files = files_svc.get_files_by_name(file_name, directory)
        drive_file = get_newest_file(drive_files)
        drive_file_id = drive_file.get('id')

        if not drive_file_id:
            print(f'Creating {file_name} on google drive...')
            files_svc.create_file(path, directory)
        elif file_changed(path, drive_file):
            print(f'Updating {file_name} on google drive...')
            files_svc.update_file(path, drive_file_id)
        else:
            print(f'Skipping {file_name} update because it has not been modified')


def main() -> None:
    try:
        print('Authorizing')
        drive_svc = drive.authorize(TOKEN, CREDENTIALS, SCOPES)

        for backup in config.BACKUPS:
            resolved_paths = glob(backup[0], recursive=True)
            if not resolved_paths:
                print(f'PATTERN \'{backup[0]}\' IS INVALID!!!')
                continue

            upload_files(drive_svc, resolved_paths, backup[1])

        print('Done')

    except Exception as ex:
        print(ex)
        print('EXCEPTION OCCURED WHILE UPLOADING FILES!')


if __name__ == '__main__':
    main()
