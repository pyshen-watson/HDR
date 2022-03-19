import os, zipfile
import gdown

def download(album_id=0):

    album_keys = ['1DFY8Ke-s4suFuTuzVx18Bfe5OCYKYWCl','1qF5SuA3dAIYESbMQ1TxUayZZtCXd_-WZ']
    album_names = ['Test_file','NTU_MainLibrary']


    URL = f'https://drive.google.com/uc?id={album_keys[album_id]}'
    PATH = f'./Images/{album_names[album_id]}'
    NAME = f'{PATH}/images.zip'
    os.makedirs(PATH, exist_ok=True)

    downloaded_filename = gdown.download(url=URL, output=NAME, quiet=False)
    print(f'Download of {downloaded_filename} finished.')

    unzip(NAME, PATH)
    print(f'Unzip at {PATH}')

    os.remove(NAME)

def unzip(input_file, output_dir):
    with zipfile.ZipFile(input_file, 'r') as zip_ref:
        zip_ref.extractall(output_dir)

