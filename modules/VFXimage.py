"""
VFXImageSet: 
            A Set of VFXImage
Attribute:
            name | path | images
"""
import os
import cv2
import numpy as np


class VFXImageSet:

    def __init__(self, img_path):

        self.original_path = img_path
        self.MTB_path = self.original_path.replace('original', 'MTB')
        self.name = self.original_path.split('/')[-1]

        def load_images():
            filenames = os.listdir(self.original_path)
            filenames.sort()
            jpg_path = [f'{self.original_path}/{filename}' for filename in filenames if 'JPG' in filename]
            raw_path = [f'{self.original_path}/{filename}' for filename in filenames if 'CR2' in filename]
            return [VFXImage(raw_path[i], jpg_path[i]) for i in range(len(jpg_path))]
        self.images = load_images()

    def align(self):

        # origin = np.asarray(self.images[-1].JPG)
        # img_gray = cv2.cvtColor(origin, cv2.COLOR_RGB2GRAY)
        # _, img_MTB = cv2.threshold(img_gray, 150, 255, cv2.THRESH_BINARY)
        # output_path = f'{self.MTB_path}/image.JPG'
        # cv2.imwrite(output_path, img_MTB)
        print("align")


        
    def __str__(self) -> str:

        for image in self.images:
            print(image)
        return self.name
        
        
"""
VFXImage: 
            A single image
Attribute:
            name | RAW | JPG | ISO | shutter | aperture
"""

import piexif
from PIL import Image

class VFXImage:
    def __init__(self, raw_img='', jpg_img=''):
        self.RAW = Image.open(raw_img)
        self.JPG = Image.open(jpg_img)
        self.name = raw_img.split('/')[-1][:-4]
        
        exif = piexif.load(self.JPG.info["exif"])["Exif"]

        self.ISO = exif[34855]
        self.shutter = exif[33434][0] / exif[33434][1]
        self.aperture = exif[37378][0] / exif[37378][1]

        # def get_MTB():
        #     img_gray = cv2.cvtColor(np.asarray(self.JPG), cv2.COLOR_RGB2GRAY)
        #     median = np.median(img_gray.flatten())
        #     img_MTB = cv2.threshold(img_gray, median, 255, cv2.THRESH_BINARY)
        #     print(median)
        #     return img_MTB

        # self.MTB = get_MTB()

    def __str__(self):
        output = f'{"=" * 20} {self.name} {"=" * 20}\n'
        output += f'ISO: {self.ISO}\n'
        output += f'Shutter: {self.shutter}\n'
        output += f'Aperture: {self.aperture}\n'
        return output
        