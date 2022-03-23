import os
import gdown
import piexif
import cv2
import numpy as np
from PIL import Image
from zipfile import ZipFile
from modules.env import ALBUM_LINKS, ALBUM_NAMES, ALBUM_TYPES

def download(album_id):

    url = f'https://drive.google.com/uc?id={ALBUM_LINKS[album_id]}'
    album_path = f'./Images/{ALBUM_NAMES[album_id]}'

    os.makedirs(album_path)
    os.makedirs(f'{album_path}/{ALBUM_TYPES[0]}')


    # Download the zipfile from google drive to ZIP_PATH and unzip at original directory.
    zip_path = f'{album_path}/images.zip'
    gdown.download(url=url, output=zip_path, quiet=False)

    with ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(f'{album_path}/{ALBUM_TYPES[0]}')

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

def getExif(img_path):
    img = Image.open(img_path)
    exif = piexif.load(img.info["exif"])["Exif"]
    exposureTime = exif[33434][0] / exif[33434][1]  # Shutter Speed Value
    filmSpeed = exif[34855]                         # ISO Value
    aperture = exif[37378][0] / exif[37378][1]      # Aperture Value
    return [exposureTime, filmSpeed, aperture]

def translate(img, x:int, y:int):
    M = np.array([[1, 0, x],[0, 1, y]], np.float32)
    return cv2.warpAffine(img.astype(np.float32), M, (img.shape[1], img.shape[0]))

"""
Reference: 
[1] https://stackoverflow.com/questions/38511444/python-download-files-from-google-drive-using-url
[2] https://stackoverflow.com/questions/3451111/unzipping-files-in-python
[3] https://stackoverflow.com/questions/4764932/in-python-how-do-i-read-the-exif-data-for-an-image
"""