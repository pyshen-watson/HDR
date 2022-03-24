from modules.utils import selection
from modules.env import ALBUM_NAMES
from modules.HDRAlbum import HDRAlbum


if __name__ == '__main__':

    options = " ".join([f'[{i}] {name}' for i, name in enumerate(ALBUM_NAMES)])
    album_id = selection(
                statement=f'Select the album: {options}: ',
                N_options=len(ALBUM_NAMES),
                default_value=0)

    album = HDRAlbum(album_id)
    album.download_images()
    album.load_images()
    album.align_images()
    album.solve_response_curve()
    album.get_radiances()
    album.get_tonemapping()