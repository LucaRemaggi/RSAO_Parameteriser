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
import math
from scipy import signal
from audiolazy import lazy_lpc as lpc
from RIR_Segmentation import Segmentation
from Beamformers import Beamformers
from MixingTime_Estimation import EstimatePerceptualMixingTime
from FilterGeneration import FilterGeneration
from Utility import DecayCalculation
from scipy import optimize
from Utility import Biquad_Convertion


class EncoderSAOBFormat:

    def __init__(self, RIRs, fs=48000, groupdelay_threshold=-0.05, use_LPC=1,
                 n_discrete=20, discrete_mode='first', RoomDims=None, EarlyProperties=None):
        # Including input variables in self
        self.RIRs = RIRs
        self.fs = fs
        self.groupdelay_threshold = groupdelay_threshold
        self.use_LPC = use_LPC
        self.n_discrete = n_discrete
        self.discrete_mode = discrete_mode
        self.RoomDims = RoomDims
        self.EarlyProperties = EarlyProperties

        print("Assuming RIRs presented in B-Format (WXYZ)")
        
        # Number of peaks considered as direct sound and early reflections
        self.nPeaks = n_discrete + 1
        
        self.speed = 343.1
        
        SizeRIRs = np.shape(RIRs)
        if SizeRIRs[0] < SizeRIRs[1]:
            RIRs.transpose()
        
        self.nMics = SizeRIRs[1]
        if self.nMics != 4:
            sys.exit("1st order (4-channel) B-Format input expected")

        self.PeakVals = np.zeros([self.nPeaks, self.nMics])

        # Defining the outputs
        self.param = {}

    def direct_and_early_parameterization(self):

        # Window length for segmenting direct sound and early reflections
        hamm_lengths = [32]*(self.n_discrete+1)
        hamm_lengths[0] = 0.002 * self.fs
        hamm_lengths = np.int_(hamm_lengths)

        # Segment every channel of the soundfield mic
        RIR_segments = Segmentation(RIRs=self.RIRs, fs=self.fs,
                                              groupdelay_threshold=self.groupdelay_threshold,
                                              use_LPC=self.use_LPC, discrete_mode=self.discrete_mode,
                                              nPeaks=self.nPeaks, hamm_lengths=hamm_lengths)
        RIR_segments.segmentation()

        segments = RIR_segments.segments
        TOAs = RIR_segments.TOAs_sample_single_mic

        # Beamforming from B-format cardioid steering
        count = 0
        for idx_refl in segments:
            reflectionDOA = Beamformers(signal=segments[idx_refl])
            reflectionDOA.steerBFormat()

            # Amplitude (for valid peaks)
            ampl_curr = np.sqrt(np.sum(reflectionDOA.hBeam**2))

            # Defining LPC order to estimate colouration
            LPC_orders = [8]*(self.n_discrete+1)
            LPC_orders[0] = 16

            # LPC spectrum estimation based on the highest amplitude microphone
            hLPCRef = reflectionDOA.hBeam  # segments[idx_refl][:, 0]
            nOD = LPC_orders[count]
            ar = lpc.lpc.kautocor(hLPCRef, nOD)

            # Saving parameters in a dictionary
            self.param.update({idx_refl: {'toa': TOAs[count]}})
            self.param[idx_refl].update({'window_samples': hamm_lengths[count]*2})
            self.param[idx_refl].update({'doa': [round(math.degrees(reflectionDOA.az_rad_curr)),
                                                 round(math.degrees(reflectionDOA.el_rad_curr))]})
            self.param[idx_refl].update({'level': ampl_curr})
            self.param[idx_refl].update({'filter': ar.numerator})

            # Convert LPC to biquads including normalization
            earlybiquad = Biquad_Convertion(RSAO_params=self.param, idx_RIR_part_investigated=idx_refl)
            earlybiquad.lpc2biquad()
            self.param[idx_refl].update({'filtersos': earlybiquad.filtersos})

            # Convert the levels to be relative to the direct sound's
            if count > 0:
                earlybiquad.convertlevels_early()
                self.param[idx_refl]['level'] = earlybiquad.earlyLevel

            # Convert delays to be relative to the direct sound's
            if count > 0:
                if count == 1:
                    self.param[idx_refl].update({'toa_notconverted': self.param[idx_refl]['toa']})

                earlybiquad.convertdelays_early()
                self.param[idx_refl]['toa'] = earlybiquad.earlyDelay

            # Convert onset times in seconds
            if count > 0:
                self.param[idx_refl]['toa'] = self.param[idx_refl]['toa'] / self.fs

            count += 1

        # Convert delay direct sound
        self.param['Direct_sound'].update({'toa_notconverted': self.param['Direct_sound']['toa']})
        self.param['Direct_sound']['toa'] = 0

        self.param

        return self
    
    def late_parameterization(self):
        if self.RoomDims is None:
            sys.exit("Please, provide the room dimensions in input")

        # Create object to calculate the mixing time
        mte = EstimatePerceptualMixingTime(RoomDims=self.RoomDims)
        mte.model_based()

        self.param.update({'Late': {'toa': mte.mixing_time_estimate['model']['tmp50'] * self.fs /
                                           1000 + self.EarlyProperties['Direct_sound']['toa_notconverted'] + 100}})
        self.param['Late'].update({'refattackramplength': math.floor(self.param['Late']['toa'] -
                                                          self.EarlyProperties['Reflection1']['toa_notconverted'])})

        # Take the last part after the estimated mixing time
        lateFirstSample = np.int_(round(self.param['Late']['toa']))
        hLate = self.RIRs[lateFirstSample:, :]
        self.param['Late'].update({'window_samples': hLate.shape[0]})
        estimateDrop = -20  # Drop in late energy over which to estimate level and decay

        # Defining the filter bank properties
        fcentre = [1000*2**idx for idx in range(-4, 5)]
        bandwidth = [1]*10
        bandwidth[0] = 0.3
        maxwindowlength = self.fs/100
        windowlength = np.int_([2*self.fs/idx for idx in fcentre])
        for iW in range(0, len(windowlength)):
            if windowlength[iW] > maxwindowlength:
                windowlength[iW] = maxwindowlength
        self.param['Late'].update({'bandcut': fcentre})

        # Generating the filter bank and calculating the RIR decays
        for iBand in range(0, len(fcentre)):
            if iBand == 0:
                LowPass = FilterGeneration(f0=fcentre[iBand], BW=1, fs=self.fs)
                LowPass.lowpassCoefficientsBW()
                b = LowPass.b
                a = LowPass.a

            elif iBand == len(fcentre)-1:
                HighPass = FilterGeneration(f0=fcentre[iBand], BW=1, fs=self.fs)
                HighPass.highpassCoefficientsBW()
                b = HighPass.b
                a = HighPass.a

            else:
                BandPass = FilterGeneration(f0=fcentre[iBand], BW=1, fs=self.fs)
                BandPass.bandpassCoefficientsBW()
                b = BandPass.b
                a = BandPass.a

            # Backwards integration
            FilteredLate = signal.filtfilt(b, a, hLate[:, 0])
            FilteredFull = signal.filtfilt(b, a, self.RIRs[:, 0])

            # Decay estimate
            decay = DecayCalculation(h=np.abs(FilteredLate), fs=self.fs)
            decay.RT_Shroeder()
            estimateStop = np.argmin(np.abs(decay.EDC_log - (-20)))

            # Fitting the decays with an exponential
            time = np.linspace(0, estimateStop, estimateStop)
            fitfunc = lambda p, x: p[0]*np.exp(p[1]*x)  # Target function
            errfunc = lambda p, x, y: fitfunc(p, x) - y  # Distance to the target function
            fit_init = [np.max(decay.EDC), -0.5]  # Initial guess for the parameters
            fit_tmp, success = optimize.leastsq(errfunc, fit_init[:], args=(time, decay.EDC[0:estimateStop]))
            try:
                success == 1
            except OverflowError:
                print('Overflow encountered, possibly in the np.exp function')

            fitresult = fit_tmp[1] / 2

            # Estimating reverberation energy
            lateEnergy = np.sum(FilteredFull[lateFirstSample:lateFirstSample+estimateStop] ** 2)
            est_energy = np.sqrt(np.sum(FilteredFull[lateFirstSample-windowlength[iBand]:
                                        lateFirstSample+windowlength[iBand]] ** 2))

            if iBand == 0:
                self.param['Late'].update({'expdecays': {str(iBand+1): fitresult}})
                self.param['Late'].update({'level': {str(iBand + 1): est_energy*bandwidth[iBand]}})
            else:
                self.param['Late']['expdecays'].update({str(iBand + 1): fitresult})
                self.param['Late']['level'].update({str(iBand + 1): est_energy*bandwidth[iBand]})

            # Convert late level to be as a proportion of the direct level
            latebiquad = Biquad_Convertion(RSAO_params=self.param, idx_RIR_part_investigated='Late',
                                           RSAO_params_directsound=self.EarlyProperties['Direct_sound'],
                                           iBand_investigated=iBand)
            latebiquad.convertlevels_late()
            self.param['Late']['level'][str(iBand + 1)] = latebiquad.lateLevel

        # Convert the reverb TOA assuming that the direct sound arrives at time 0, and populate the attack time based on
        #  the late refattackramplength
        latebiquad.convertdelays_late()
        self.param['Late']['toa'] = latebiquad.lateDelay
        self.param['Late']['toa'] = (self.param['Late']['toa']-self.param['Late']['refattackramplength']) / self.fs

        # Convert the times from samples to seconds
        for iBand in range(0, len(fcentre)):
            if iBand == 0:
                self.param['Late'].update({'attacktimes': {str(iBand + 1): self.param['Late']['refattackramplength'] /
                                                           self.fs}})
            else:
                self.param['Late']['attacktimes'].update({str(iBand + 1): self.param['Late']['refattackramplength'] /
                                                          self.fs})

            self.param['Late']['expdecays'][str(iBand + 1)] = self.param['Late']['expdecays'][str(iBand + 1)] * self.fs

        return self
