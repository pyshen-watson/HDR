import cv2
import numpy as np
from modules.env import ALIGN_LEVEL

# 9 directions to shift
DIRECTIONS = [(x,y) for x in range(-1,2) for y in range(-1,2)]

def translate(img, x:int, y:int):
    M = np.array([[1, 0, x],[0, 1, y]], np.float32)
    return cv2.warpAffine(img.astype(np.float32), M, (img.shape[1], img.shape[0]))

def diff(img, std, mask):
    xor_value = np.logical_xor(img, std)
    and_value = np.logical_and(xor_value, mask)
    sum_value = np.sum(and_value)
    return sum_value.item()

def align(MTB_std, MTB_img, MTB_mask):

    x_shift, y_shift = 0, 0

    for level in range(ALIGN_LEVEL, -1, -1):

        height, width = MTB_mask.shape[:2]
        height >>= level
        width >>= level

        # Resize the image to 2^level times small 
        std = cv2.resize(MTB_std, (height, width), interpolation=cv2.INTER_AREA)        
        img = cv2.resize(MTB_img, (height, width), interpolation=cv2.INTER_AREA)
        mask = cv2.resize(MTB_mask, (height, width), interpolation=cv2.INTER_AREA)

        # The translate(...) is the twice shift of the previous plus current
        diffs = [diff( translate(img, x_shift*2+x, y_shift*2+y), std, mask) for x,y in DIRECTIONS]
        index = diffs.index(min(diffs))
        
        x_shift = x_shift*2 + DIRECTIONS[index][0]
        y_shift = y_shift*2 + DIRECTIONS[index][1]

    shift_diff = diff(translate(MTB_img, x_shift, y_shift), MTB_std, MTB_mask)
    noshift_diff = diff( MTB_img, MTB_std, MTB_mask)

    # print(f'{"="*20}\nShift: {x_shift} {y_shift} Move: {shift_diff} No Move: {noshift_diff}')

    if shift_diff > noshift_diff:
        return 0,0
        
    return x_shift, y_shift

