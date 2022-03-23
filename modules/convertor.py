import numpy as np
from numba import njit

@njit
def Z3_to_X(Z3, curve):

    X = np.array([curve[i][int(Z3[i].item())] for i in range(3)])
    X = (X[0] * 19 + X[1] * 183 + X[2] * 54) / 256
    return X
   
@njit
def Z3_to_w(Z3):
    Z = (Z3[0] * 19 + Z3[1] * 183 + Z3[2] * 54) / 256

    if Z <= 127:
        return Z
    else:
        return 255-Z


@njit
def render_radiance(height, width, N_image, Z3, curve, ln_dt):

    # Z3 shape: (#images, height, width, 3)

    radiance = np.zeros((height, width), dtype=np.float64)

    for r in range(height):
        for c in range(width):

            sample = Z3[:,r,c,:]
            W = np.array([ Z3_to_w(sample[j]) for j in range(N_image)])
            X = np.array([ Z3_to_X(sample[j], curve) - ln_dt[j] for j in range(N_image)])


            try:            
                radiance[r,c] = np.sum(X*W) / np.sum(W)

            except:
                radiance[r,c] = 0


    return radiance