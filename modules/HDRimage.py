"""
HDRImageAlbum: 
            A Set of HDRImage
Attribute:
            id: The album ID
            root: The path to the album
            path: The paths to different types
"""
import os
from re import S
import cv2
import numpy as np

from tqdm import tqdm
from modules.env import ALBUM_NAMES, ALBUM_TYPES, ALIGN_IGNORANCE, SAMPLE_HEIGHT, SAMPLE_WIDTH
from modules.utils import download, getExif
from modules.alignment import align
from modules.responseCurve import gsolve

class HDRImageAlbum:

    def __init__(self, album_id):
        self.id = album_id
        self.root = f'./Images/{ALBUM_NAMES[album_id]}'
        self.path = [ f'{self.root}/{album_type}' for album_type in ALBUM_TYPES]

    def load_image(self):

        if not os.path.isdir(self.path[0]):
            download(self.id)
            print(f'Download and unzip photos at {self.path[0]}.')

        filenames = os.listdir(self.path[0])
        filenames.sort()
        jpg_path = [f'{self.path[0]}/{filename}' for filename in filenames if 'JPG' in filename]
        self.images = [HDRImage(jpg) for jpg in jpg_path]

    def load_MTB(self):

        print(f'Loading MTB at {self.path[1]}...')

        if not os.path.isdir(self.path[1]):
            os.makedirs(self.path[1])
            for img in tqdm(self.images):
                img.load_MTB(exist=False)
        else:
            for img in self.images:
                img.load_MTB(exist=True)

    def load_ALN(self): 

        print(f'Loading ALN at {self.path[2]}...')
        if not os.path.isdir(self.path[2]):
            os.makedirs(self.path[2])
            std = self.images[-1]
            img_gray, median = std.get_gray_and_median()
            mask = cv2.inRange(img_gray, median-ALIGN_IGNORANCE, median+ALIGN_IGNORANCE)
            for img in tqdm(self.images):
                img.load_ALN(exist=False, std=std.MTB, mask=mask)
        else:
            for img in self.images:
                img.load_ALN(exist=True)  

    def sampling(self):
        for img in self.images:
            img.sampling()


        N_channel = 3
        N_sample = SAMPLE_HEIGHT * SAMPLE_WIDTH
        N_image = len(self.images)

        self.Z_value = np.zeros((N_channel, N_sample, N_image))

        for i in range(3):
            self.Z_value[i] =  np.array([img.Z_value[:,i] for img in self.images]).reshape(N_sample, N_image)

    def get_G_function(self):

        dt = np.array([img.shutter for img in self.images])
        for i in range(3):
            g, ln_E = gsolve(self.Z_value[i], dt) 
        


"""
HDRImage: 
            A single image
Attribute:
            path: The paths to different type of images
            img: The image in numpy 2d-array
            shutter: The exposure time of the image
            MTB: The median Threshold Bitmap of the image
            ALN: The shifted image after alignment
"""

class HDRImage:

    def __init__(self, jpg_path):
        self.path = [jpg_path.replace(ALBUM_TYPES[0], album_type) for album_type in ALBUM_TYPES]
        self.img = cv2.imread(self.path[0])
        self.shutter = getExif(self.path[0])[0]

    def load_MTB(self, exist):
        if exist:
            self.MTB = cv2.imread(self.path[1], cv2.IMREAD_GRAYSCALE)
        else:
            img_gray, median = self.get_gray_and_median()
            _, img_MTB = cv2.threshold(img_gray, median, 255, cv2.THRESH_BINARY)
            self.MTB = img_MTB
            cv2.imwrite(self.path[1], self.MTB)

    def get_gray_and_median(self):
        img_gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        median = np.median(img_gray.flatten())
        return img_gray, median

    def load_ALN(self, exist, std=None, mask=None):
        if exist:
            self.ALN = cv2.imread(self.path[2])
        else:
            x_shift, y_shift = align(std, self.MTB, mask)
            M = np.array([[1, 0, x_shift],[0, 1, y_shift]], np.float32)
            self.ALN = cv2.warpAffine(self.img.astype(np.float32), M, (self.img.shape[1], self.img.shape[0]))
            cv2.imwrite(self.path[2], self.ALN)

    def sampling(self):
        downScale = cv2.resize(self.img, (SAMPLE_HEIGHT, SAMPLE_WIDTH), interpolation=cv2.INTER_AREA)
        self.Z_value = np.reshape(downScale, (SAMPLE_HEIGHT*SAMPLE_WIDTH, 3))