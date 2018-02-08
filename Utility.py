
from scipy import signal
import numpy as np


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
        self.RT = None
        self.EDC_log = None
        self.EDC = None

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

        # Finding zero crossing
        self.x = self.y * 1
        self.m = 'n'
        self.zerocross()
        self.tew = self.t
        self.sew = self.s

        self.tew = self.tew + self.toff

        return self

    def zerocross(self):
        # This code is translated from the original version that was in Matlab, within the VOICEBOX toolbox
        # zerocross finds the zeros crossing in a signal

        self.x[abs(self.x) < 10 ** -5] = 0

        self.s = self.x >= 0
        self.s = np.int_(np.array(self.s))  # Converting false to 0 and true to 1
        k = self.s[1:] - self.s[:-1]
        if self.m is 'p':
            f = np.where(k > 0)
        elif self.m is 'n':
            f = np.where(k < 0)
        else:
            f = k != 0

        f = np.transpose(np.int_(f))

        self.s = np.subtract(self.x[f + 1], self.x[f])
        self.t = f - np.divide(self.x[f], self.s)

        return self


class DecayCalculation:

    def __init__(self, h, fs=48000, region=[-5, -35], delay_comp=0):
        self.h = h
        self.fs = fs
        self.region = region
        self.delay_comp = delay_comp

    def RT_Shroeder(self):
        # This method calculates reverb time and energy decay using the Shroeder's approach

        h_length = len(self.h)
        # Compensate sound propagation (exclude parts of the RIR before the direct path)
        if self.delay_comp == 1:
            prop_delay = np.argmax(self.h)
            self.h[0:h_length-prop_delay] = self.h[prop_delay:h_length]
            h_length = len(self.h)

        # Energy decay curve
        h_sq = self.h ** 2
        h_sq = np.flipud(h_sq)
        self.EDC = np.cumsum(h_sq)
        self.EDC = np.flipud(self.EDC) + 10**-250

        # Normalize to '1'
        EDC_norm = self.EDC / np.max(self.EDC)

        # Estimate the reverberation time
        self.EDC_log = 10*np.log10(EDC_norm)
        EDC_reg1 = np.int_(np.argwhere(self.EDC_log <= self.region[0])[0])
        EDC_reg2 = np.int_(np.argwhere(self.EDC_log <= self.region[1])[0])

        EDC_reg12 = self.EDC_log[EDC_reg1[0]:EDC_reg2[0]]
        x = np.array([idx for idx in range(0, len(EDC_reg12))])
        p = np.polyfit(x, EDC_reg12, 1)
        y = p[0]*x + p[1]

        y0 = y[0] - p[0]*EDC_reg1

        # Inserction of polyfit line with -60dB
        x_rt = np.int_((-60-y0)/p[0])

        # Reverberation time in seconds
        self.RT = x_rt/self.fs

        # Fitting line from 0 to -60dB
        x = np.array([idx for idx in range(0, x_rt[0])])
        y = p[0]*x + y0

        return self


class Biquad_Convertion():

    def __init__(self, RSAO_params, RSAO_params_directsound=None, idx_RIR_part_investigated=None,
                 iBand_investigated=None):

        self.RSAO_params = RSAO_params
        self.RSAO_params_single = RSAO_params[idx_RIR_part_investigated]
        self.idx_RIR_part_investigated = idx_RIR_part_investigated
        self.iBand_investigated = iBand_investigated
        self.RSAO_params_directsound = RSAO_params_directsound

        self.filtersos = None
        self.earlyLevel = None
        self.lateLevel = None

    def lpc2biquad(self):
        # Obtain biquad coefficients for filter estimation
        self.filtersos = _normalized_sos(self.RSAO_params_single['filter'])

        return self

    def convertlevels_early(self):
        # Convert parameters so that the early levels are relative to the direct level
        directLevel = self.RSAO_params['Direct_sound']['level']
        self.earlyLevel = self.RSAO_params_single['level'] / directLevel

        return self

    def convertlevels_late(self):
        # Convert parameters so that the early levels are relative to the direct level
        directLevel = self.RSAO_params_directsound['level']
        self.lateLevel = self.RSAO_params_single['level'][str(self.iBand_investigated + 1)] / directLevel

        return self

    def convertdelays_early(self):
        self.earlyDelay = self.RSAO_params_single['toa'] - self.RSAO_params['Direct_sound']['toa']

        return self

    def convertdelays_late(self):
        self.lateDelay = self.RSAO_params_single['toa'] - self.RSAO_params_directsound['toa_notconverted']

        return self


def _normalized_sos(coeff):
    # Subfunction to re-normalize the coefficients of the incoming LPC (FIR) coefficients to unity based on the noise
    # gain np.sqrt(np.sum(coeff**2))

    impulse = np.zeros(129)
    impulse[64] = 1
    sos = signal.tf2sos(1, coeff)
    filtsig1 = signal.sosfilt(sos, impulse)
    lpc_noise_gain = np.sqrt(np.sum(filtsig1 ** 2))

    gainmatrix = np.ones([sos.shape[0], sos.shape[1]])
    gainmatrix[0, 0] = 1/lpc_noise_gain
    soscoeff = sos * gainmatrix

    return soscoeff