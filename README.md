# Dyskietka

Dyskietka is a simple python utility for uploading files to google drive.  

**IMPORTANT**
Recently I realized that there is a tool called **_'rclone'_** which does everything I wanted **_'dyskietka'_** to do and even more.  
I suggest using rclone unless someday I improve my utility.  
It will probably be thrown into the void called **_'Projects I started but never finished'_** though.

## Why did I create this?
Who likes to manually drag and drop files? I know I don't. That's why I spent hours on making this tool so I can automate the process of backing up my files on google drive :)  

## TODOs (Might do some day)
- Add support for uploading directories

## Requirements
- Python and pip package management tool installed
- A Google Cloud Platform project with the API enabled. Guide to that can be found here: https://developers.google.com/workspace/guides/create-project
- Authorization credentials for a desktop application. Guide to creating credentials: https://developers.google.com/workspace/guides/create-credentials

## Setup
- Put credentials.json into ***auth*** directory of this project
- Install requirements using pip (I highly recommend using virtual environment for this): ***pip install -r requirements.txt***
- Add paths to files you want to backup in ***src/config.py*** (comment and example inside should be self explanatory)
- Run ***src/backup_files.py*** and don't worry about using GUI no more
