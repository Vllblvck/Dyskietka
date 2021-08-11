# Permissions for google drive
SCOPES = [
    # Gives access to files created by this script
    'https://www.googleapis.com/auth/drive.file'
]

# Path to a credentials.json file on a hard drive
CREDENTIALS = 'credentials.json'

# Path to a token.json file which is used for saving authentication token for future runs
TOKEN = 'token.json'

# List containing paths to files (can contain patterns according to the rules used by UNIX shell)
FILES = ['/home/vllblvck/.x*']

# SIZES OF FILES AND DIRECTORIES MUST BE THE SAME!!!
# List of destination directories ids on google drive. Each entry corresponds to entry from FILES.
# Main directory = None or empty string
DIRECTORIES = ['']
