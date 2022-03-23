"""
HDRImageAlbum: 
            A Set of HDRImage
Attribute:
            id: The album ID
            root: The path to the album
            path: The paths to different types
"""
import os
import cv2
import numpy as np

from tqdm import tqdm
from modules.env import ALBUM_NAMES, ALBUM_TYPES, ALIGN_IGNORANCE, SAMPLE_HEIGHT, SAMPLE_WIDTH
from modules.utils import download, getExif, translate
from modules.plot import draw_g
from modules.alignment import align
from modules.responseCurveSolver import debevec_solution

class HDRImageAlbum:

    def __init__(self, album_id):
        self.id = album_id
        self.root = f'./Images/{album_id}_{ALBUM_NAMES[album_id]}'
        self.path = [ f'{self.root}/{album_type}' for album_type in ALBUM_TYPES]
    
    def download_images(self):
        if not os.path.isdir(self.path[0]):
            download(self.id)
            print(f'Download finished and unzip the images at {self.path[0]}.')

    def load_images(self):
        filenames = os.listdir(self.path[0])
        filenames.sort(reverse=True) # From the longest exposure time to the shortest
        jpg_path = [f'{self.path[0]}/{filename}' for filename in filenames if 'JPG' in filename]
        self.images = [HDRImage(jpg) for jpg in jpg_path]

    def align_images(self):
        if os.path.isdir(self.path[1]):
            return
        else:
            print(f'Align the images at {self.path[1]}:')
            os.makedirs(self.path[1])

            std = self.images[0]
            cv2.imwrite(std.path[1] ,std.img)

            for img in tqdm(self.images[1:]):
                img.align_to(std.get_MTB(), std.get_mask())

            print(f'The alignment is done.')

    def sampling(self):

        for img in self.images:
            img.sampling()

        N_channel = 3
        N_sample = SAMPLE_HEIGHT * SAMPLE_WIDTH
        N_image = len(self.images)
        self.Z = np.zeros((N_channel, N_image, N_sample))

        for channel in range(3):
            self.Z[channel] = np.array([img.Z[:,channel] for img in self.images])

    def solve(self):
        dt = np.array([img.shutter for img in self.images])
        self.g = [debevec_solution(self.Z[c], dt) for c in range(3)]
        draw_g(ALBUM_NAMES[self.id], self.g)


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
        self.shutter = getExif(self.path[0])[0]
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