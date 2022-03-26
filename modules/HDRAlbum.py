import os
import cv2
import numpy as np

from tqdm import tqdm
from modules.env import *
from modules.HDRImage import HDRImage
from modules.renderer import render_radiance
from modules.utils import download, reorder
from modules.plot import draw_g, draw_radiance
from modules.responseCurveSolver import debevec_solution
from modules.toneMapping import NonNormalizeToneMap, NaiveToneMap

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
        jpg_path = [f'{self.path[0]}/{filename}' for filename in filenames if 'JPG' in filename]
        self.images = [HDRImage(jpg) for jpg in jpg_path]
        self.images.sort(key=lambda x: x.shutter, reverse=True)

    def align_images(self):

        # Load cache if it exists
        if os.path.isdir(self.path[1]):
            return

        print(f'Align the images at {self.path[1]}:')
        os.makedirs(self.path[1])

        std = self.images[len(self.images)//2]
        for img in tqdm(self.images):
            img.align_to(std.get_MTB(), std.get_mask())

    def solve_response_curve(self):

        # Load cache if it exists
        if os.path.isdir(self.path[2]):
            print(f'Loading the response curve...')
            self.resCurve = np.load(f'{self.path[2]}/model.npy')
            return

        print('Solving the response curve...')

        self.Z = np.zeros((3, len(self.images), SAMPLE_HEIGHT * SAMPLE_WIDTH))

        for c in range(3):
            self.Z[c] = np.array([img.sampling()[:,c] for img in self.images])
        
        ln_dt = np.log(np.array([img.shutter for img in self.images]), dtype=np.float32)
        self.resCurve = np.array([debevec_solution(self.Z[c], ln_dt) for c in range(3)], dtype=np.float32)

        # os.makedirs(self.path[2])
        np.save(f'{self.path[2]}/model', self.resCurve)
        print(f'Save {self.path[2]}/model.npy')
        draw_g(ALBUM_NAMES[self.id], self.path[2], self.resCurve)

    def get_radiances(self):

        # Load cache if it exists
        if os.path.isdir(self.path[3]):
            print(f'Loading the HDR image...')
            self.hdr = cv2.imread(f'{self.path[3]}/{ALBUM_NAMES[self.id]}.hdr', flags=cv2.IMREAD_ANYDEPTH)
            return


        print("Calculate the radiance map...")
        std = self.images[0].img

        ln_radiances = render_radiance(
            height=std.shape[0], 
            width=std.shape[1], 
            N_image=len(self.images),
            Z3=np.array([img.img for img in self.images]), # shape: (#images, height, width, 3)
            curve=self.resCurve,
            ln_dt=np.log([img.shutter for img in self.images])
        )
        
        os.makedirs(self.path[3])
        draw_radiance(ALBUM_NAMES[self.id], self.path[3], ln_radiances)                

        self.hdr = reorder(ln_radiances)
        cv2.imwrite(f'{self.path[3]}/{ALBUM_NAMES[self.id]}.hdr', self.hdr)
        print(f'Save {self.path[3]}/{ALBUM_NAMES[self.id]}.hdr')

    def get_tonemapping(self):

        os.makedirs(self.path[4], exist_ok=True)

        Drago = cv2.createTonemapDrago(DRAGO_GAMMA, DRAGO_SATURATION)
        Reinhard = cv2.createTonemapReinhard(REINHARD_GAMMA, REINHARD_INTENSITY, REINHARD_LIGHT_ADAPT, REINHARD_COLOR_ADAPT)
        Mantiuk = cv2.createTonemapMantiuk(MANTIUK_GAMMA, MANTIUK_SCALE, MANTIUK_SATURATION)
        Naive = NaiveToneMap(SELF_MU)
        NonNorm = NonNormalizeToneMap(SELF_ALPHA)

        TM_func = [Drago, Reinhard, Mantiuk, Naive, NonNorm]
        TM_name = ['Drago', 'Reinhard', 'Mantiuk', 'Naive', 'NonNorm']


 
        for func, name, tune in zip(TM_func, TM_name, ALBUM_TUNE[self.id]):
            ldr = func.process(self.hdr) * tune
            filename = f"{self.path[4]}/{name}.jpg"
            cv2.imwrite(filename, ldr * 255)
            print(f"Save {filename}")
        