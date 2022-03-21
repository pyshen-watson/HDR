import os
from modules.utils import selection, download
from modules.env import ALBUM_NAMES, ALBUM_TYPES
from modules.HDRimage import HDRImageAlbum


if __name__ == '__main__':


    options = " ".join([f'[{i}] {name}' for i, name in enumerate(ALBUM_NAMES)])
    album_id = selection(
                statement=f'Select the album: {options} (default 0): ',
                N_options=2,
                default_value=0)


    album_path = f'./Images/{ALBUM_NAMES[album_id]}/{ALBUM_TYPES[0]}'
    if not os.path.isdir(album_path):
        download(album_id)


    images = HDRImageAlbum(album_path)
    images.align()
