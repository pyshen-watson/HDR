import cv2
import numpy as np
from modules.env import ALIGN_LEVEL
from modules.utils import translate

# 9 directions to shift
DIRECTIONS = [(x,y) for x in range(-1,2) for y in range(-1,2)]

def diff(img, std, mask):
    xor_value = np.logical_xor(img, std)
    and_value = np.logical_and(xor_value, mask)
    sum_value = np.sum(and_value)
    return sum_value.item()

def align(img, std, mask, debug=False):

    x_shift, y_shift = 0, 0

    for level in range(ALIGN_LEVEL, -1, -1):

        height, width = mask.shape[:2]
        height >>= level
        width >>= level

        # Resize the image to 2^level times small 
        _std = cv2.resize(std, (height, width), interpolation=cv2.INTER_AREA)        
        _img = cv2.resize(img, (height, width), interpolation=cv2.INTER_AREA)
        _mask = cv2.resize(mask, (height, width), interpolation=cv2.INTER_AREA)

        # The translate(...) is the twice shift of the previous plus current
        diffs = [diff(translate(_img, x_shift*2+x, y_shift*2+y), _std, _mask) for x,y in DIRECTIONS]
        choice_index = diffs.index(min(diffs))
        
        x_shift = x_shift*2 + DIRECTIONS[choice_index][0]
        y_shift = y_shift*2 + DIRECTIONS[choice_index][1]

    if debug:
        shift_diff = diff(translate(img, x_shift, y_shift), std, mask)
        noshift_diff = diff(img, std, mask)
        print(f'{"="*20}\nShift: {x_shift} {y_shift} Move: {shift_diff} No Move: {noshift_diff}')
        
    return x_shift, y_shift
