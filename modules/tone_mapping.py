import numpy as np
from numba import njit

#                 Algorithm:
#       Reinhard Tone Mapping Algorithm

@njit
def tone_mapping(height, width, img, radiances):
    E_gamma = np.zeros((3, height, width), dtype=np.float64)
    E_norm = np.zeros((3, height, width), dtype=np.float64)
    gamma = 2.8
    a = 0.5
    for channel in range(3):
        E_max = 0
        E_min = radiances[channel, 0, 0]
        radiance = radiances[channel]
        for r in range(height):
            for c in range(width):
                radiance[r, c] = np.exp(radiance[r, c])
                if E_max < radiance[r, c]:
                    E_max = radiance[r, c]
                if E_min > radiance[r, c]:
                    E_min = radiance[r, c]
        #print(f'E_max={E_max}, E_min={E_min}')
        for r in range(height):
            for c in range(width):
                E_norm[channel, r, c] = (radiance[r, c] - E_min)/(E_max - E_min)
                E_gamma[channel, r, c] = E_norm[channel, r, c] ** gamma
    #print(f'E_gamma={E_gamma}, E_norm={E_norm}')
    L = np.zeros((height, width), dtype=np.float64)
    for r in range(height):
        for c in range(width):
            L[r, c] = (E_norm[0, r, c]*11 + E_norm[1, r, c]*59 + E_norm[2, r, c]*30 + 50)/100
    #print(f'L={L}')
    L_sum = 0
    for r in range(height):
        for c in range(width):
            L_sum = L_sum + np.log(L[r, c])
    #print(f'L_sum={L_sum}')
    L_avg = np.exp(L_sum/(height*width))
    T = np.zeros((height, width), dtype=np.float64)
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
    L_tone = np.zeros((height, width), dtype=np.float64)
    for r in range(height):
        for c in range(width):
            L_tone[r, c] = T[r, c]*(1+(T[r, c])/(T_max**2))/(1+T[r, c])
    #print(f'L_tone={L_tone}')
    M = np.zeros((height, width), dtype=np.float64)
    for r in range(height):
        for c in range(width):
            M[r, c] = L_tone[r, c]/L[r, c]
    #print(f'M={M}')
    for r in range(height):
        for c in range(width):
            img[r, c] = [M[r, c]*radiances[0, r, c], M[r, c]*radiances[1, r, c], M[r, c]*radiances[2, r, c]]*255
    #print(f'tone_mapped={img}')
    return img