import os
import gdown
from zipfile import ZipFile

album_keys = [
    '1DFY8Ke-s4suFuTuzVx18Bfe5OCYKYWCl',
    '1qF5SuA3dAIYESbMQ1TxUayZZtCXd_-WZ'
    ]

album_names = [
    'Test_file',
    'NTU_MainLibrary'
    ]

def download(album_id):

    URL = f'https://drive.google.com/uc?id={album_keys[album_id]}'
    ALBUM_PATH = f'./Images/{album_names[album_id]}'

    os.makedirs(ALBUM_PATH, exist_ok=True)
    os.makedirs(f'{ALBUM_PATH}/original', exist_ok=True)
    os.makedirs(f'{ALBUM_PATH}/MTB', exist_ok=True)


    # Download the zipfile from google drive to ZIP_PATH and unzip at original directory.
    ZIP_PATH = f'{ALBUM_PATH}/images.zip'
    DOWNLOAD_FILENAME = gdown.download(url=URL, output=ZIP_PATH, quiet=False)
    print(f'Download of {DOWNLOAD_FILENAME} finished.')

    with ZipFile(ZIP_PATH, 'r') as zip_ref:
        zip_ref.extractall(f'{ALBUM_PATH}/original')

    print(f'Unzip at {ALBUM_PATH}')
    os.remove(ZIP_PATH)

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