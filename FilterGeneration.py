#
# Author: Luca Remaggi
# Email: l.remaggi@surrey.ac.uk
# 06/02/2018
#
# Ported in Python from the Matlab implementation of Andreas Frank

import numpy as np


class FilterGeneration:

    def __init__(self, f0, BW, fs=48000):
        self.f0 = f0
        self.BW = BW
        self.fs = fs

        self.w0 = 2 * np.pi * f0/fs

        self.b = None
        self.a = None

    def lowpassCoefficientsBW(self):

        alpha = np.sin(self.w0) * np.sinh(np.log(2)/2 * self.BW * self.w0/np.sin(self.w0))

        b0 = (1 - np.cos(self.w0)) / 2
        b1 = 1 - np.cos(self.w0)
        b2 = (1 - np.cos(self.w0)) / 2
        a0 = 1 + alpha
        a1 = -2*np.cos(self.w0)
        a2 = 1 - alpha

        bUnNorm = [b0, b1, b2]
        aUnNorm = [a0, a1, a2]

        self.b = [1/aUnNorm[0]*idx for idx in bUnNorm]
        self.a = [1/aUnNorm[0]*idx for idx in aUnNorm]

        return self

    def bandpassCoefficientsBW(self):

        alpha = np.sin(self.w0) * np.sinh(np.log(2) / 2 * self.BW * self.w0 / np.sin(self.w0))

        b0 = alpha
        b1 = 0
        b2 = -alpha
        a0 = 1 + alpha
        a1 = -2 * np.cos(self.w0)
        a2 = 1 - alpha

        bUnNorm = [b0, b1, b2]
        aUnNorm = [a0, a1, a2]

        self.b = [1 / aUnNorm[0] * idx for idx in bUnNorm]
        self.a = [1 / aUnNorm[0] * idx for idx in aUnNorm]

        return self

    def highpassCoefficientsBW(self):

        alpha = np.sin(self.w0) * np.sinh(np.log(2) / 2 * self.BW * self.w0 / np.sin(self.w0))

        b0 = (1 + np.cos(self.w0)) / 2
        b1 = -(1 + np.cos(self.w0))
        b2 = (1 + np.cos(self.w0)) / 2
        a0 = 1 + alpha
        a1 = -2 * np.cos(self.w0)
        a2 = 1 - alpha

        bUnNorm = [b0, b1, b2]
        aUnNorm = [a0, a1, a2]

        self.b = [1 / aUnNorm[0] * idx for idx in bUnNorm]
        self.a = [1 / aUnNorm[0] * idx for idx in aUnNorm]

        return self
