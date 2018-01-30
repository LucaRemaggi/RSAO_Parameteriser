#
# This class contains some algorithms that are useful for signal peak 
# detection.
#
# Author: Luca Remaggi 
# Email: l.remaggi@surrey.ac.uk
# 11/01/2018

from scipy import signal
import numpy as np
from audiolazy import lazy_lpc as lpc
from Utility import Utility


class Peakpicking:

    def __init__(self, RIR, fs, groupdelay_threshold, use_LPC=1, cutoff_samples=5000, nLPC=12):
        self.RIR = RIR
        self.fs = fs
        self.groupdelay_threshold = groupdelay_threshold
        self.use_LPC = use_LPC
        self.cutoff_samples = cutoff_samples
        self.nLPC = nLPC
        self.p_pos = None

    def DYPSA(self):
        # This method estimates the position of peaks in a room impulse response by applying the DYPSA algorithm

        # Check that cutoff_samples is integer
        cutoff_samples = np.int_(self.cutoff_samples)

        # General variables internal to this method
        prev_rir = self.RIR  # This is defined to allow future changes at the peak positions
        l_rir = len(self.RIR)
        self.RIR[cutoff_samples:l_rir] = 0

        if self.use_LPC == 1:
            # LPC for reduction of amount of data in RIR
            rir_up = signal.decimate(self.RIR, 2)
            l_rir_lpc = len(rir_up)

            # Calculate the matching AR filter based on the RIR
            ar = lpc.lpc(rir_up, self.nLPC)
            a = np.array(ar.numerator)
            b = np.array(ar.denominator)

            # Convert the filter into a time-reversed impulse response
            impulse = np.zeros(l_rir_lpc)
            impulse[0] = 1
            matched_forward = signal.lfilter(b, a, impulse)
            matched = np.flipud(matched_forward)

            # Apply the matched filter to the RIR
            rir_matched = signal.convolve(rir_up, matched)
            rir_matched = rir_matched[l_rir_lpc-1:]

            # Linearly interpolating
            RIR_new = signal.upfirdn([1], rir_matched, 2)

        # Realigning the new RIR with the original one
        val_max_new = np.argmax(abs(RIR_new))
        val_max_old = np.argmax(abs(prev_rir))
        diff_max = val_max_new - val_max_old
        if diff_max > 0:
            del self.RIR
            self.RIR = np.concatenate([RIR_new[diff_max:], np.zeros(diff_max)])
        elif diff_max < 0:
            del self.RIR
            self.RIR = np.concatenate([np.zeros(abs(diff_max)), RIR_new[:l_rir-abs(diff_max)]])
        else:
            del self.RIR
            self.RIR = RIR_new

        # Running the DYPSA algorithm
        OriginalDYPSA = Utility(self.RIR, self.fs)
        peaks_properties = OriginalDYPSA.xewgrdel()
        tew = peaks_properties.tew
        sew = peaks_properties.sew
        y = peaks_properties.y
        ntew = np.int_(np.round_(tew))

        # This avoids possible problems with sources too close to the microphones
        if ntew[0] < 0:
            ntew[0] = 0

        # Create an array which has zeros except for where tew defines peak positions
        k = 0
        peaks_init = np.zeros(l_rir)
        for idx_samp in range(0, len(y)):
            if k == len(ntew):
                break

            if idx_samp == ntew[k]:
                peaks_init[idx_samp] = 1
                k += 1

        # Peaks taken from the group-delay function where the slope is less than the threshold in input are deleted
        for idx_sew in range(0, len(sew)):
            if sew[idx_sew] > self.groupdelay_threshold:
                peaks_init[ntew[idx_sew]] = 0
        self.p_pos = peaks_init

        # Normalizing the RIR
        self.RIR = abs(self.RIR)
        norm_val = np.max(self.RIR)
        self.RIR = self.RIR / norm_val

        # Take the neighbourhood of the calculated position in the signal (which corresponds in total to 1ms) taking the rms
        # of the energy
        half_win = int(round(self.fs/2000))
        for idx_samp in range(0, len(ntew)):
            center = int(ntew[idx_samp])
            if (center - half_win) > 0:
                segment = self.RIR[center-half_win:center+half_win]
            else:
                segment = self.RIR[0:center+half_win]

            self.p_pos[center] = np.sqrt(np.mean(segment**2))

        ################################################################
        # From here there are additional improvements to the performance
        ################################################################
        # First, the array containing the peaks is normalized, and the position of the strongest peak found
        self.p_pos = self.p_pos / np.max(self.p_pos)
        ds_pos = int(np.argmax(self.p_pos))

        # Everything before the direct sound is equal to zero
        self.p_pos[:ds_pos-1] = 0

        # Deletes small errors by aligning the estimated direct sound position to the one in input
        ds_pos_gt = int(np.argmax(self.RIR))
        estimation_err = ds_pos_gt - ds_pos
        if estimation_err > 0:
            self.p_pos = list(self.p_pos)
            self.p_pos = [[0]*estimation_err + self.p_pos[estimation_err:]]
        elif estimation_err < 0:
            self.p_pos = list(self.p_pos)
            self.p_pos = [self.p_pos[abs(estimation_err):] + [0]*abs(estimation_err)]
        self.p_pos = np.transpose(np.array(self.p_pos))

        return self


def clustering_dypsa():

    return
