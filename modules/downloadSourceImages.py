import os, zipfile
import gdown

album_keys = [
    '1DFY8Ke-s4suFuTuzVx18Bfe5OCYKYWCl',
    '1qF5SuA3dAIYESbMQ1TxUayZZtCXd_-WZ']

album_names = [
    'Test_file',
    'NTU_MainLibrary']

def download(album_id):

    URL = f'https://drive.google.com/uc?id={album_keys[album_id]}'
    PATH = f'./Images/{album_names[album_id]}'
    os.makedirs(PATH, exist_ok=True)
    FILE_PATH = f'{PATH}/images.zip'

    downloaded_filename = gdown.download(url=URL, output=FILE_PATH, quiet=False)
    print(f'Download of {downloaded_filename} finished.')

    unzip(FILE_PATH, PATH)
    print(f'Unzip at {PATH}')

    os.remove(FILE_PATH)

def unzip(input_file, output_dir):
    with zipfile.ZipFile(input_file, 'r') as zip_ref:
        zip_ref.extractall(output_dir)

"""
Reference: 
[1] https://stackoverflow.com/questions/38511444/python-download-files-from-google-drive-using-url
[2] https://stackoverflow.com/questions/3451111/unzipping-files-in-python
"""