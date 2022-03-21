"""
HDRImageAlbum: 
            A Set of HDRImage
Attribute:
            ORI_path: The path to the original photo directory
            MTB_path: The path to the MTB directory
            name: The name of the album
            images: A list of HDRImage
"""
import os
import cv2
import numpy as np

from modules.env import ALBUM_TYPES


class HDRImageAlbum:

    def __init__(self, album_path):

        self.ORI_path = album_path
        self.MTB_path = self.ORI_path.replace(ALBUM_TYPES[0], ALBUM_TYPES[1])
        self.name = self.ORI_path.split('/')[2]

        filenames = os.listdir(self.ORI_path)
        filenames.sort()
        jpg_path = [f'{self.ORI_path}/{filename}' for filename in filenames if 'JPG' in filename]
        self.images = [HDRImage(jpg) for jpg in jpg_path] 

    def align(self):
        # std = self.images[-1] 
        # mask = cv2.inRange(cv2.cvtColor(std.JPG, cv2.COLOR_BGR2GRAY), std.median-10, std.median+10)
        pass
        
    def __str__(self):

        for image in self.images:
            print(image)
        return self.name
        
        
"""
HDRImage: 
            A single image
Attribute:
            name: Name of the photo
            path: Path to the orginal version of photo
            img: Image open by PIL
            JPG: img convert to NumPy array
            MTB: The Median Threshold Bitmap
            shutter: The exposure time of image
"""

import piexif
import rawpy
from PIL import Image

class HDRImage:

    def __init__(self, jpg_path):
        self.name = jpg_path.split('/')[-1][:-4]
        self.path = jpg_path
        self.img = Image.open(jpg_path)
        self.JPG = cv2.cvtColor(np.asarray(self.img), cv2.COLOR_RGB2BGR)
        self.MTB = self.load_MTB()

        exif = piexif.load(self.img.info["exif"])["Exif"]
        self.shutter = exif[33434][0] / exif[33434][1]
        # self.ISO = exif[34855]
        # self.aperture = exif[37378][0] / exif[37378][1]
        
    def load_raw(self):
        raw_path = self.path.replace('JPG', 'CR2')
        self.RAW = rawpy.imread(raw_path)
        # self.RAW = self.RAW.postprocess()
        # self.RAW = cv2.cvtColor(self.RAW, cv2.COLOR_RGB2BGR)
        return self.RAW

    def load_MTB(self):
        
        MTB_PATH = self.path.replace(ALBUM_TYPES[0], ALBUM_TYPES[1])

        if os.path.isfile(MTB_PATH):
            return cv2.imread(MTB_PATH, cv2.IMREAD_GRAYSCALE)
        else:
            img_gray = cv2.cvtColor(self.JPG, cv2.COLOR_BGR2GRAY)
            self.median = np.median(img_gray.flatten())
            _, img_MTB = cv2.threshold(img_gray, self.median, 255, cv2.THRESH_BINARY)
            cv2.imwrite(MTB_PATH, img_MTB)
            return img_MTB

    def get_median(self):
        img_gray = cv2.cvtColor(self.JPG, cv2.COLOR_BGR2GRAY)
        self.median = np.median(img_gray.flatten())
        return self.median

    def __str__(self):
        output = f'{"=" * 20} {self.name} {"=" * 20}\n'
        output += f'Shutter: {self.shutter}\n'
        # output += f'ISO: {self.ISO}\n'
        # output += f'Aperture: {self.aperture}\n'
        return output
