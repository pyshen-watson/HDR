import os
from modules.utils import selection
from modules.env import ALBUM_NAMES, ALBUM_TYPES
from modules.HDRimage import HDRImageAlbum


if __name__ == '__main__':

    options = " ".join([f'[{i}] {name}' for i, name in enumerate(ALBUM_NAMES)])
    album_id = selection(
                statement=f'Select the album: {options}: ',
                N_options=len(ALBUM_NAMES),
                default_value=0)

    album = HDRImageAlbum(album_id)
    album.download_images()
    album.load_images()
    album.align_images()
    album.sampling()
    album.solve()