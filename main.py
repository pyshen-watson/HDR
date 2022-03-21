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

    album = HDRImageAlbum(album_id)
    album.load_image()
    album.load_MTB()
    album.load_ALN()