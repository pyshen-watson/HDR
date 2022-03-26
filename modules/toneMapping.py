import numpy as np

class NaiveToneMap:

    def __init__(self, mu):
        self.mu = mu

    def process(self, hdr):
        return np.log(1 + self.mu * hdr) / np.log(1 + self.mu) / 3

class NonNormalizeToneMap:

    def __init__(self, alpha):
        self.alpha = alpha

    def process(self, hdr):

        gray_trans = np.array([0.114, 0.587, 0.299], dtype=np.float32)

        L = hdr[:,:].dot(gray_trans)

        L_avg = np.exp(np.average(np.log(L + 1e-4)))

        T = (self.alpha / L_avg) * L

        T_max = np.max(T)

        L_tone = T*(1+T/(T_max**2))  / (1+T)

        M = L_tone / L 


        for i in range(3):
            hdr[:,:,i] *= M
        

        return hdr