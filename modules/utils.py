import os, cv2, gdown
import numpy as np
from zipfile import ZipFile
from numba import njit
from modules.env import ALBUM_LINKS, ALBUM_NAMES, ALBUM_TYPES

def selection(statement, N_options, default_value):
    ret = input(statement)

    # input is integer
    try:
        ret = int(ret)
        if ret < 0 or ret >= N_options:
            return default_value
        return ret

    # Invalid input
    except:
        return default_value

def download(album_id):

    url = f'https://drive.google.com/uc?id={ALBUM_LINKS[album_id]}'
    album_path = f'./Images/{album_id}_{ALBUM_NAMES[album_id]}'

    os.makedirs(album_path)
    os.makedirs(f'{album_path}/{ALBUM_TYPES[0]}')


    # Download the zipfile from google drive to ZIP_PATH and unzip at original directory.
    zip_path = f'{album_path}/images.zip'
    gdown.download(url=url, output=zip_path, quiet=False)

    with ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(f'{album_path}/{ALBUM_TYPES[0]}')

    os.remove(zip_path)

def translate(img, x:int, y:int):
    M = np.array([[1, 0, x],[0, 1, y]], np.float32)
    return cv2.warpAffine(img.astype(np.float32), M, (img.shape[1], img.shape[0]))

@njit
def reorder(ln_E):
    (channel, height, width) = ln_E.shape
    E = np.zeros((height, width, channel), dtype=np.float32)
    
    for c in range(channel):
        for h in range(height):
            for w in range(width):
                E[h,w,c] = np.exp(ln_E[c,h,w])
    return E

"""
Reference: 
[1] https://stackoverflow.com/questions/38511444/python-download-files-from-google-drive-using-url
[2] https://stackoverflow.com/questions/3451111/unzipping-files-in-python
[3] https://numba.pydata.org/numba-doc/latest/user/performance-tips.html
"""