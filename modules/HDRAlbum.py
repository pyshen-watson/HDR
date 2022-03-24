import os
import cv2
import numpy as np

from tqdm import tqdm
from time import perf_counter
from modules.HDRImage import HDRImage
from modules.renderer import render_radiance
from modules.env import ALBUM_NAMES, ALBUM_TYPES, DRAGO_GAMMA, DRAGO_SATURATION, MANTIUK_GAMMA, MANTIUK_SATURATION, MANTIUK_SCALE, REINHARD_COLOR_ADAPT, REINHARD_GAMMA, REINHARD_INTENSITY, REINHARD_LIGHT_ADAPT, SAMPLE_HEIGHT, SAMPLE_WIDTH
from modules.utils import download, reorder
from modules.plot import draw_g, draw_radiance
from modules.responseCurveSolver import debevec_solution
from modules.tone_mapping import tone_mapping

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

    def solve_response_curve(self):

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
        np.save(f'{self.path[2]}/model', self.resCurve)
        print(f'Save {self.path[2]}/model.npy')
        draw_g(ALBUM_NAMES[self.id], self.path[2], self.resCurve)

    def get_radiances(self):
        
        if os.path.isdir(self.path[3]):
            self.hdr = cv2.imread(f'{self.path[3]}/{ALBUM_NAMES[self.id]}.hdr', flags=cv2.IMREAD_ANYDEPTH)
            return

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

        tonemapDrago = cv2.createTonemapDrago(DRAGO_GAMMA, DRAGO_SATURATION)
        ldrDrago = tonemapDrago.process(self.hdr) * 3
        filename = f"{self.path[4]}/Drago-{DRAGO_GAMMA}-{DRAGO_SATURATION}.jpg"
        cv2.imwrite(filename, ldrDrago * 255)
        print(f"Save {filename}")


        tonemapReinhard = cv2.createTonemapReinhard(REINHARD_GAMMA, REINHARD_INTENSITY, REINHARD_LIGHT_ADAPT, REINHARD_COLOR_ADAPT)
        ldrReinhard = tonemapReinhard.process(self.hdr)
        filename = f"{self.path[4]}/Reinhard-{REINHARD_GAMMA}-{REINHARD_INTENSITY}-{REINHARD_LIGHT_ADAPT}-{REINHARD_COLOR_ADAPT}.jpg"
        cv2.imwrite(filename, ldrReinhard * 255)
        print(f"Save {filename}")

        tonemapMantiuk = cv2.createTonemapMantiuk(MANTIUK_GAMMA, MANTIUK_SCALE, MANTIUK_SATURATION)
        ldrMantiuk = tonemapMantiuk.process(self.hdr) * 3
        filename = f"{self.path[4]}/MANTIUK-{MANTIUK_GAMMA}-{MANTIUK_SCALE}-{MANTIUK_SATURATION}.jpg"
        cv2.imwrite(filename, ldrMantiuk * 255)
        print(f"Save {filename}")

        std = self.images[len(self.images)//2].img

        tone_mapped = tone_mapping(
            height=std.shape[0],
            width=std.shape[1],
            img=std,
            radiances=self.hdr
        )
        # newimg = self.images[1].img
        # for r in range(std.shape[0]):
        #     for c in range(std.shape[1]):
        #         newimg[r, c, 0] = newimg[r, c, 0]*tone_mapped[r, c]
        #         newimg[r, c, 1] = newimg[r, c, 1]*tone_mapped[r, c]
        #         newimg[r, c, 2] = newimg[r, c, 2]*tone_mapped[r, c]
        cv2.imwrite(f'{self.path[3]}/tone_mapped.jpg', tone_mapped)
        print(f'Save {self.path[3]}/tone_napped.jpg')