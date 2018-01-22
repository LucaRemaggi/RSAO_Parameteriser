# -*- coding: utf-8 -*-

# This class contains the encoder of the reverb parameterization model, described in 
# Remaggi et al., "Estimation of room reflection parameters for a 
# reverberant spatial audio object", 138th AES Convention, 2015.
# This version works with B-format RIRs.
# 
# in:
# * RIRs are impulse responses recorded using a microphone array
#   (NxM matix, where N is the number of samples, and M the number of microphones) 
# * 'fs' is a scalar, corresponding to the sample frequency of RIRs. 
# *  groupdelay_threshold sets the threshold at which the
#    slope of the group delay zero crossing is considered to be a reflection e.g -0.05 
# *  'UCA_radius' is a vector containing the radius of the microphone array, 
#     e.g. if the double concentric UCA is
#     used, '[0.083 0.104]'. 
# * 'use_LPC' set to 1 enables the LPC filter inside DYPSA
# * n_discrete sets the number of early reflections returned (not including
#   direct sound)
# * discrete_mode sets the behaviour to return:
#   'first': the first n_discrete reflections
#   'strongest': the strongest n_discrete reflections
# * late_mode sets the behaviour of the late estimation:
#   'data': uses the mean perceptual mixing time based over all RIR chans
#   'model': uses the perceptual mixing time based on the given room
#           dimensions
# * roomDims gives the ground truth room dimensions [l,w,h] or [] if not
#    used
#
# out:
# 'parameters' is a data structure, containing the parameters
# characterizing the spatial objects. 
#
# Luca Remaggi, University of Surrey, 16/10/2015.
# l.remaggi@surrey.ac.uk
#
# 3/5/2016 major changes (Philip Coleman)
# * used the Lindau perceptual mixing time (tmp50) for late
#   onset estimation
# * uses a reference microphone (with largest energy) for spectrum
#   estimation
# * removed assumption of two early reflections and instead return L
#   reflections
# * added option to control early reflection behaviour: 'first' (default)
#   returns the first n_discrete reflections (as previous version), 'strongest'
#   returns the n_discrete reflections with biggest energy
#
# 11/01/2018 Translated from Matlab to Python by Luca Remaggi 

import numpy as np
import sys
from Algorithm_PeakDetection import peaks_position
from scipy import signal


class EncoderSAOBFormat:

    def __init__(self, RIRs, fs=48000, groupdelay_threshold=-0.05, use_LPC=1,
                 n_discrete=20, discrete_mode='first', late_mode='model', RoomDims=None):
        # Including input variables in self
        self.RIRs = RIRs
        self.fs = fs
        self.groupdelay_threshold = groupdelay_threshold
        self.use_LPC = use_LPC
        self.n_discrete = n_discrete
        self.discrete_mode = discrete_mode
        self.late_mode = late_mode
        self.RoomDims = RoomDims

        print("Assuming RIRs presented in B-Format (WXYZ)")
        
        # Number of peaks considered as direct sound and early reflections
        self.nPeaks = n_discrete + 1
        
        self.speed = 343.1
        
        SizeRIRs = np.shape(RIRs)
        if SizeRIRs[0] < SizeRIRs[1]:
            RIRs.transpose()
        
        nMics = SizeRIRs[1]
        if nMics != 4:
            sys.exit("1st order (4-channel) B-Format input expected")
            
        self.TOAs_sample = np.zeros([self.nPeaks, nMics])
        self.PeakVals = np.zeros([self.nPeaks, nMics])

        if late_mode is 'model' and RoomDims is None:
            sys.exit("Please, provide the room dimensions in input")

    def segmentation(self):

        # Run DYPSA with the B-format omni component
        p_pos = peaks_position(RIR=self.RIRs[:, 0], fs=self.fs,
                                     groupdelay_threshold=self.groupdelay_threshold,
                                     use_LPC=self.use_LPC, cutoff_samples=0.5*self.fs)

        # Choosing which peaks to prioritize
        if self.discrete_mode is 'first':
            # Find peaks in the DYPSA output
            locs_all = np.transpose(np.array(np.where(p_pos[:, 0] != 0)))
            locs = locs_all[:(self.nPeaks + 5)]
            peaks = np.squeeze(p_pos[locs])
            firstearlypeaks = []
            firstearlylocs = []
        elif self.discrete_mode is 'strongest':
            # Find the first two in time
            locs_all = np.transpose(np.array(np.where(p_pos[:, 0] != 0)))
            firstearlylocs = locs_all[:2]
            firstearlypeaks = np.squeeze(p_pos[firstearlylocs])

            # Then finds the first peaks in energy-descending order
            peaks = np.squeeze(p_pos[locs_all])
            peaks = list(peaks)
            peaks = np.array(sorted(peaks, reverse=True))
            locs_mixed, idx_locs = np.where(p_pos == peaks)
            locs = locs_mixed[idx_locs]



        return p_pos

    def direct_and_early_parameterization(self):
        
        return 0
    
    def late_parameterization(self):
        
        return 0
