import os, gdown
from modules.env import ALBUM_LINKS, ALBUM_NAMES, ALBUM_TYPES
from zipfile import ZipFile

def download(album_id):

    url = f'https://drive.google.com/uc?id={ALBUM_LINKS[album_id]}'
    album_path = f'./Images/{ALBUM_NAMES[album_id]}'

    os.makedirs(album_path, exist_ok=True)
    for type in ALBUM_TYPES:
        os.makedirs(f'{album_path}/{type}', exist_ok=True)


    # Download the zipfile from google drive to ZIP_PATH and unzip at original directory.
    zip_path = f'{album_path}/images.zip'
    gdown.download(url=url, output=zip_path, quiet=False)
    print(f'Download of {zip_path} finished.')

    with ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(f'{album_path}/{ALBUM_TYPES[0]}')

    print(f'Unzip at {album_path}/{ALBUM_TYPES[0]}')
    os.remove(zip_path)

def selection(statement, N_options, default_value):
    ret = input(statement)

    # input is integer
    try:
        ret = int(ret)
        if ret < 0 or ret >= N_options:
            print(f'Using default value: {default_value}')
            return default_value
            
        return ret

    # Invalid input
    except:
        print(f'Using default value: {default_value}')
        return default_value


"""
Reference: 
[1] https://stackoverflow.com/questions/38511444/python-download-files-from-google-drive-using-url
[2] https://stackoverflow.com/questions/3451111/unzipping-files-in-python
"""