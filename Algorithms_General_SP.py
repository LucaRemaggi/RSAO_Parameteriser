#
# This class contains some algorithms that are useful for signal processing.
#
# Author: Luca Remaggi 
# Email: l.remaggi@surrey.ac.uk
# 11/01/2018

import numpy as np

class Algorithms_General_SP:

    def __init__(self, x, m='b'):
        self.x = x
        self.m = m
        self.t = None
        self.s = None

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
    
    def _FindNearest():
        
        return
    
    def _LPC2Biquad():
        
        return
    
    def _ConvertLevels():
        
        return
    
    def _ConvertDelays():
        
        return
    
    def _ConvertTimes():
        
        return
