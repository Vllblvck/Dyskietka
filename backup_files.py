import config
import googledrive as drive

from glob import glob
from pathlib import Path


def resolve_patterns(paths_patterns):
    files = []
    for pattern in paths_patterns:
        resolved_paths = glob(pattern, recursive=True)
        files += resolved_paths

    return files


def main():
    if len(config.FILES) != len(config.DIRECTORIES):
        print('SIZES OF FILES AND DIRECTORIES MUST BE THE SAME!!!')
        return

    try:
        print('Authorizing...')
        drive_service = drive.authorize()

        #TODO fix index out of bounds
        file_paths = resolve_patterns(config.FILES)
        for idx, file_path in enumerate(file_paths):
            directory = config.DIRECTORIES[idx]
            file_name = Path(file_path).name

            print('Checking whether file exists...')
            file_id = drive.get_newest_file_id(drive_service, file_name)

            if not file_id:
                print('Creating file on google drive...')
                drive.create_file(drive_service, file_path,
                                  directory=directory)
            else:
                print('Updating file on google drive...')
                drive.update_file(drive_service, file_path, file_id)

    except Exception as ex:
        print('EXCEPTION OCCURED WHILE UPLOADING FILES!')
        print(ex)


if __name__ == '__main__':
    main()
