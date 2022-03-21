import numpy as np
import numpy.linalg as la


def gsolve(Z, dt):

    n = 255
    ln_dt = np.log(dt)
    N_SAMPLE, N_IMAGES = Z.shape[:2]
    N_DATA = N_SAMPLE * N_IMAGES

    A = np.zeros((N_DATA+n, N_SAMPLE+n+1))
    b = np.zeros((N_DATA+n))
    w = lambda z: z if z <= n/2 else n-z
    int_Z = lambda i,j : int(Z[i, j].item())

    # g(Z_ij) = ln E_i + ln dt_j
    for idx_img in range(N_IMAGES):
        for i in range(N_SAMPLE):

            row = idx_img * N_SAMPLE + i
            Zij = int_Z(i, idx_img)
            Wij = w(Zij)

            A[row, Zij] = Wij
            A[row, n+1+i] = -Wij
            b[row] = ln_dt[idx_img] * Wij

    # g(127) = 0
    A[N_DATA][127] = 1

    # g"(z) = g(z-1) - 2g(z) + g(z+1)
    for row in range(1,n):
        A[N_DATA + row][row-1:row+2] = np.array([1,-2,1])

    x = la.lstsq(A, b, rcond=None)[0]
    g = x[:256]
    ln_E = np.zeros((N_SAMPLE))

    for i in range(N_SAMPLE):

        weight = np.array([w(int_Z(i, idx_image)) for idx_image in range(N_IMAGES)])
        g_ln_dt_diff = np.array([g[int_Z(i, j)] - ln_dt[j] for j in range(N_IMAGES)])
        ln_E[i] = np.sum(weight * g_ln_dt_diff) / np.sum(weight)


    return g, ln_E