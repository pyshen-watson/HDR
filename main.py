from modules.downloadSourceImages import download


if __name__ == '__main__':

    try:
        album_id = input('Enter the album id: [0]Test [1]NTULibrary (default none): ')
        album_id = int(album_id)
        download(album_id)
    except:
        pass

