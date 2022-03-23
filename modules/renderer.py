import numpy as np
from numba import njit

@njit
def render_radiance(height, width, N_image, Z3, curve, ln_dt):

    radiances = np.zeros((3, height, width), dtype=np.float64)

    w = lambda z: z if z<=127 else 255-z
    g = lambda z, channel: curve[channel][int(z.item())]

    for channel in range(3):

        radiance = np.zeros((height, width), dtype=np.float64)

        for r in range(height):
            for c in range(width):

                sample = Z3[:,r,c,channel]
                W = np.array([ w(sample[j]) for j in range(N_image)])
                X = np.array([ g(sample[j], channel) - ln_dt[j] for j in range(N_image)])

                try:            
                    radiance[r,c] = np.sum(X*W) / np.sum(W)

                except:
                    radiance[r,c] = 0

        radiances[channel] = radiance


    return radiances