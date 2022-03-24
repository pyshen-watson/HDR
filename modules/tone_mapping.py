import numpy as np
from numba import njit

#                 Algorithm:
#       Reinhard Tone Mapping Algorithm

@njit
def tone_mapping(height, width, img):
    E_gamma = np.zeros((height, width, 3), dtype=np.float32)
    E_norm = np.zeros((height, width, 3), dtype=np.float32)
    gamma = 2.8
    a = 0.18
    for channel in range(3):
        E_max = 0
        E_min = img[0, 0, channel]
        for r in range(height):
            for c in range(width):
                if E_max < img[r, c, channel]:
                    E_max = img[r, c, channel]
                if E_min > img[r, c, channel]:
                    E_min = img[r, c, channel]
        #print(f'E_max={E_max}, E_min={E_min}')
        for r in range(height):
            for c in range(width):
                E_norm[r, c, channel] = (img[r, c, channel] - E_min)/(E_max - E_min)
                # E_gamma[r, c, channel] = E_norm[channel, r, c] ** gamma
    #print(f'E_gamma={E_gamma}, E_norm={E_norm}')
    L = np.zeros((height, width), dtype=np.float32)
    for r in range(height):
        for c in range(width):
            L[r, c] = (E_norm[r, c, 0]*11 + E_norm[r, c, 1]*59 + E_norm[r, c, 2]*30 + 50)/100
    #print(f'L={L}')
    L_sum = 0
    for r in range(height):
        for c in range(width):
            L_sum = L_sum + np.log(L[r, c])
    #print(f'L_sum={L_sum}')
    L_avg = np.exp(L_sum/(height*width))
    T = np.zeros((height, width), dtype=np.float32)
    for r in range(height):
        for c in range(width):
            T[r, c] = L[r, c]*(a/L_avg)
    #print(f'L_avg={L_avg}, T={T}')
    T_max = 0
    for r in range(height):
        for c in range(width):
            if T_max < T[r, c]:
                T_max = T[r, c]
    #print(f'T_max={T_max}')
    L_tone = np.zeros((height, width), dtype=np.float32)
    for r in range(height):
        for c in range(width):
            L_tone[r, c] = T[r, c]*(1+(T[r, c])/(T_max**2))/(1+T[r, c])
    #print(f'L_tone={L_tone}')
    M = np.zeros((height, width), dtype=np.float32)
    for r in range(height):
        for c in range(width):
            M[r, c] = L_tone[r, c]/L[r, c]
    #print(f'M={M}')
    for r in range(height):
        for c in range(width):
            img[r, c] = np.array([M[r, c]*img[r, c, 0], M[r, c]*img[r, c, 1], M[r, c]*img[r, c, 2]])*255
    #print(f'tone_mapped={img}')
    return img