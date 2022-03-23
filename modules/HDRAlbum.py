import os
import cv2
import numpy as np

from tqdm import tqdm
from numba import njit
from time import perf_counter
from modules.HDRImage import HDRImage
from modules.convertor import render_radiance
from modules.env import ALBUM_NAMES, ALBUM_TYPES, SAMPLE_HEIGHT, SAMPLE_WIDTH
from modules.utils import download
from modules.plot import draw_g, draw_radiance
from modules.responseCurveSolver import debevec_solution

"""
HDRImageAlbum: 
            A Set of HDRImage
Attribute:
            id: The album ID
            root: The path to the album
            path: The paths to different types
"""

class HDRAlbum:

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

    def solve(self):

        if os.path.isdir(self.path[2]):
            self.resCurve = np.load(f'{self.path[2]}/model.npy')
            return

        for img in self.images:
            img.sampling()

        N_channel = 3
        N_sample = SAMPLE_HEIGHT * SAMPLE_WIDTH
        N_image = len(self.images)
        self.Z = np.zeros((N_channel, N_image, N_sample))

        for channel in range(3):
            self.Z[channel] = np.array([img.Z[:,channel] for img in self.images])
        
        dt = np.array([img.shutter for img in self.images])
        self.resCurve = np.array([debevec_solution(self.Z[c], dt) for c in range(3)], dtype=np.float64)

        os.makedirs(self.path[2])
        print(f'Save {self.path[2]}/model.npy')

        np.save(f'{self.path[2]}/model', self.resCurve)

        draw_g(ALBUM_NAMES[self.id], self.path[2], self.resCurve)

    def get_radiance(self):
        
        std = self.images[0].img

        print(self.resCurve)

        start = perf_counter()
        
        radiance = render_radiance(
            height=std.shape[0], 
            width=std.shape[1], 
            N_image=len(self.images),
            Z3=np.array([img.img for img in self.images]), # shape: (#images, height, width, 3)
            curve=self.resCurve,
            ln_dt=np.log([img.shutter for img in self.images])
        )

        
        end = perf_counter()
        print(end-start)

        os.makedirs(self.path[3],exist_ok=True)
        draw_radiance(ALBUM_NAMES[self.id], self.path[3], radiance)                



