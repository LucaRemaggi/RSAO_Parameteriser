
from scipy import signal
import numpy as np
from Algorithms_General_SP import Algorithms_General_SP


class Utility:

    def __init__(self, RIR=None, fs=None, x=None, m='b'):
        self.RIR = RIR
        self.fs = fs
        self.x = x
        self.m = m
        self.y = None
        self.toff = None
        self.tew = None
        self.sew = None


    def xewgrdel(self):
        # This is the DYPSA algorithm that has been translated from Matlab to Python. The DYPSA algorithm was first
        # presented in P. A. Naylor, A. Kounoudes, J. Gudnason and M. Brookes, ''Estimation of glottal closure instants in
        # voiced speech using the DYPSA algorithm'', IEEE Trans. on Audio, Speech and Lang. Proc., Vol. 15, No. 1, Jan. 2007

        # General variables
        dy_gwlen = 0.003
        dy_fwlen = 0.00045

        # Perform group delay calculation
        gw = np.int_(2 * np.floor(dy_gwlen*self.fs/2) + 1)  # Force window length to be odd
        ghw = signal.hamming(gw, 1)
        ghwn = np.squeeze(ghw * [np.array(range(gw-1, -gw, -2))/2])

        RIR2 = self.RIR ** 2
        yn = signal.lfilter(ghwn, [1], RIR2)
        yd = signal.lfilter(ghw, [1], RIR2)
        yd[abs(yd) < 10**-16] = 10**-16  # It prevents infinity
        self.y = yn[gw-1:] / yd[gw-1:]
        self.toff = (gw - 1) / 2
        fw = np.int_(2 * np.floor(dy_fwlen*self.fs/2) + 1)  # Force window length to be odd
        if fw > 1:
            daw = signal.hamming(fw, 1)
            self.y = signal.lfilter(daw, [1], self.y) / np.sum(daw)  # Low pass filtering
            self.toff = self.toff - (fw - 1)/2

        zerocrossing = Algorithms_General_SP(x=self.y, m='n')
        zerocrossing.zerocross()  # Finding zero crossing
        self.tew = zerocrossing.t
        self.sew = zerocrossing.s

        self.tew = self.tew + self.toff

        return self


class DecayCalculation:

    def __init__(self):


    def RT_Shroeder(self):


        return self

