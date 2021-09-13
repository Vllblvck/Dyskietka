#!/usr/bin/python

import config
import googledrive as drive

from datetime import datetime, timezone
from glob import glob
from pathlib import Path


SCOPES = ['https://www.googleapis.com/auth/drive.file']
AUTH_DIR = Path(__file__).parent / '..' / 'auth'
CREDENTIALS = AUTH_DIR / 'credentials.json'
TOKEN = AUTH_DIR / 'token.json'
DATE_FORMAT = '%Y-%m-%dT%H:%M:%S.%f%z'


def get_newest_file(drive_files):
    if not drive_files:
        return None

    dates_list = []
    for file in drive_files:
        modified_time = datetime.strptime(
            file.get('modifiedTime'), DATE_FORMAT)
        dates_list.append(modified_time)

    dates_list.sort()

    for file in drive_files:
        modified_time = datetime.strptime(
            file.get('modifiedTime'), DATE_FORMAT)
        if modified_time == dates_list[-1]:
            return file


def file_changed(file_path, drive_file):
    file_metadata = Path(file_path).stat()

    size_changed = int(drive_file.get('size')) != file_metadata.st_size
    if size_changed:
        return True

    local_mtime = datetime.fromtimestamp(file_metadata.st_mtime, tz=timezone.utc)
    drive_mtime = datetime.strptime(drive_file.get('modifiedTime'), DATE_FORMAT)

    return local_mtime > drive_mtime


def upload_files(drive_svc, paths, directory):
    for path in paths:
        if Path(path).is_dir():
            continue

        print('Checking whether file exists on google drive...')
        file_name = Path(path).name
        files_svc = drive.DriveFilesSvc(drive_svc)
        drive_files = files_svc.get_files_by_name(file_name, directory)
        drive_file = get_newest_file(drive_files)
        drive_file_id = drive_file.get('id')

        if not drive_file_id:
            print(f'Creating {file_name} on google drive...')
            files_svc.create_file(path, directory=directory)
        elif file_changed(path, drive_file):
            print(f'Updating {file_name} on google drive...')
            files_svc.update_file(path, drive_file_id)
        else:
            print('Skipping file update because it has not been modified')


def main():
    try:
        print('Authorizing...')
        drive_service = drive.authorize(TOKEN, CREDENTIALS, SCOPES)

        for backup in config.BACKUPS:
            resolved_paths = glob(backup[0], recursive=True)
            if not resolved_paths:
                print(f'PATTERN \'{backup[0]}\' IS INVALID!!!')
                continue

            upload_files(drive_service, resolved_paths, backup[1])

        print('Done')

    except Exception as ex:
        print('EXCEPTION OCCURED WHILE UPLOADING FILES!')
        print(ex)


if __name__ == '__main__':
    main()
