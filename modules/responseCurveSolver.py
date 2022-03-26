import numpy as np
import numpy.linalg as la
from modules.env import LAMBDA

def debevec_solution(Z, ln_dt):

    n = 255
    N_IMAGES, N_SAMPLE = Z.shape[:2]
    N_DATA = N_SAMPLE * N_IMAGES

    A = np.zeros((N_DATA+n, N_SAMPLE+n+1), dtype=np.float32)
    b = np.zeros((N_DATA+n), dtype=np.float32)

    w = lambda z: z if z <= n/2 else n-z
    int_Z = lambda i,j : int(Z[j, i].item())

    # [Rule 1] g(Z_ij) = ln E_i + ln dt_j
    for j in range(N_IMAGES):
        for i in range(N_SAMPLE):

            row = j * N_SAMPLE + i
            Zij = int_Z(i, j)
            Wij = w(Zij)

            A[row, Zij] = Wij
            A[row, n+1+i] = -Wij
            b[row] = ln_dt[j] * Wij

    # [Rule 2] g(127) = 0
    A[N_DATA][127] = 1

    # [Rule 3] g"(z) = g(z-1) - 2g(z) + g(z+1)
    for row in range(1,n):
        A[N_DATA + row][row-1:row+2] = np.array([LAMBDA,-2*LAMBDA,LAMBDA])

    x = la.lstsq(A, b, rcond=None)[0]
    g = x[:256]

    return g