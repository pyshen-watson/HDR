import os
from modules.utils import selection, download, album_names
from modules.VFXimage import VFXImageSet


if __name__ == '__main__':

    album_id = selection(
                statement='Select the album: [0]Test [1]NTULibrary (default 0): ',
                N_options=2,
                default_value=0)


    album_path = f'./Images/{album_names[album_id]}/original'
    if not os.path.isdir(album_path):
        download(album_id)


    images = VFXImageSet(album_path)
    images.align()

