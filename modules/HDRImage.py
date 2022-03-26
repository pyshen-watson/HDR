import os
import cv2
import numpy as np

from modules.env import  ALBUM_TYPES, ALIGN_IGNORANCE, SAMPLE_HEIGHT, SAMPLE_WIDTH
from modules.utils import translate
from modules.alignment import align

"""
HDRImage: 
            A single image
Attribute:
            path: The paths to different type of images
            shutter: The exposure time of the image
            isAligned: To check if the image is aligned
            img: The image in numpy 2d-array
Method:
            get_gray_and_median: Get the grayscale version of img and its median
            get_MTB: Get the median Threshold Bitmap of the image
            get_mask: Get the  mask use in alignment
            align_to: Align img to std_MTB with the mask and rewrite img
            sampling: Here we use downscale to get sample in grid shape
"""

class HDRImage:

    def __init__(self, jpg_path):
        self.path = [jpg_path.replace(ALBUM_TYPES[0], album_type) for album_type in ALBUM_TYPES]
        self.shutter = 1 / int(self.path[0].split('.')[2])
        self.isAligned = os.path.isfile(self.path[1])
        self.img = cv2.imread(self.path[1] if self.isAligned else self.path[0])
    
    def get_gray_and_median(self):
        img_gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        median = np.median(img_gray.flatten())
        return img_gray, median
    
    def get_MTB(self):
        img_gray, median = self.get_gray_and_median()
        _, img_MTB = cv2.threshold(img_gray, median, 255, cv2.THRESH_BINARY)
        return img_MTB

    def get_mask(self):
        img_gray, median = self.get_gray_and_median()
        mask = cv2.inRange(img_gray, median-ALIGN_IGNORANCE, median+ALIGN_IGNORANCE)
        return mask

    def align_to(self, std_MTB, mask):
        x_shift, y_shift = align(self.get_MTB(), std_MTB, mask)
        self.img = translate(self.img, x_shift, y_shift)
        cv2.imwrite(self.path[1], self.img)

    def sampling(self):
        downScale = cv2.resize(self.img, (SAMPLE_HEIGHT, SAMPLE_WIDTH), interpolation=cv2.INTER_AREA)
        self.Z = np.reshape(downScale, (SAMPLE_HEIGHT*SAMPLE_WIDTH, 3))