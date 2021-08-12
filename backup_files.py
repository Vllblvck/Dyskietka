#!/usr/bin/python

import config
import googledrive as drive

from glob import glob
from pathlib import Path


def upload_files(drive_service, paths, directory):
    for path in paths:
        #TODO Instead of skipping directories create their structure on google drive
        if Path(path).is_dir():
            continue

        print('Checking whether file exists on google drive...')
        file_name = Path(path).name
        file_id = drive.get_newest_file_id(drive_service, file_name, directory)
        if not file_id:
            print(f'Creating {file_name} on google drive...')
            drive.create_file(drive_service, path,
                              directory=directory)
        else:
            print(f'Updating {file_name} on google drive...')
            drive.update_file(drive_service, path, file_id)


def main():
    try:
        print('Authorizing...')
        drive_service = drive.authorize(
            config.TOKEN,
            config.CREDENTIALS,
            config.SCOPES
        )

        for backup in config.BACKUPS:
            resolved_paths = glob(backup[0], recursive=True)
            print(resolved_paths)
            if not resolved_paths:
                print(f'PATTERN \'{backup[0]}\' IS INVALID!!!')
                continue

            directory = backup[1]
            upload_files(drive_service, resolved_paths, directory)

    except Exception as ex:
        print('EXCEPTION OCCURED WHILE UPLOADING FILES!')
        print(ex)


if __name__ == '__main__':
    main()
