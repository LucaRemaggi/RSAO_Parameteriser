#
# This class contains some algorithms that are useful for signal peak 
# detection.
#
# Author: Luca Remaggi 
# Email: l.remaggi@surrey.ac.uk
# 11/01/2018

from scipy import signal
import math

class Algorithm_PeakDetection:

    def __init__(self, RIR, fs, groupdelay_threshold, use_LPC, cutoff_samples, nLPC=12):

        self.RIR = RIR
        self.fs = fs
        self.groupdelay_threshold = groupdelay_threshold
        self.use_LPC = use_LPC
        self.cutoff_samples = round(cutoff_samples)
        self.nLPC = nLPC  # Number of poles for the LPC

    def peaks_position(self):
        # This method estimates the position of peaks in a room impulse response by applying the DYPSA algorithm

        # General variables internal to this method
        prev_rir = self.RIR  # This is defined to allow future changes at the peak positions
        l_rir = len(self.RIR)
        self.RIR[self.cutoff_samples:l_rir] = 0

        # LPC for reduction of amount of data in RIR
        rir_up = signal.decimate(self.RIR, 2)


        return rir_up

    def clustering_dypsa(self):
        
        return
    
    def findpeaks(self):
        
        return