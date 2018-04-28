"""
This Python package estimates the Reverberant Spatial Audio Object (RSAO) given a B-Format room impulse response (RIR).

Input:
.wav file containing the 4 channels of a B-Format RIR
OutPut:
It saves two files containing the RSAO parameters related to the early reflections (plus direct sound) and the late
reverberation, respectively.
Additionally it also saves a .json file, that contains the RSAO metadata that can be read by VISR, the object-based S3A
renderer.

Coded by:
Luca Remaggi, CVSSP, University of Surrey, 2018

If you use any code included in this package for research purposes, please refer to the following papers:
- P. Coleman, A. Franck, P. J. B. Jackson, R. J. Hughes, L. Remaggi, F. Melchior, "Object-based reverberation for
  spatial audio", Journal of the Audio Engineering Society, Vol. 65, No. 1/2, pp. 66-77, 2017.
- L. Remaggi, P. J. B. Jackson, P. Coleman, "Estimation of room reflection parameters for a reverberant spatial audio
  object", 138th AES Convention, Warsaw, Poland, 2015.
- P. Coleman, A. Franck, D. Menzies, P. J. B. Jackson, "Object-Based Reverberation Encoding from First-Order Ambisonic
  RIRs", 142nd AES Convention, Berlin, Germany, 2017.
"""

from Encoder_SAO_Bformat import EncoderSAOBFormat
from GenerateJSON import GenerateJSON_RSAO
from scipy.io import wavfile
import numpy as np
import pickle
import sys

##############################################################
# Loading RIRs
##############################################################
fs, RIRs = wavfile.read('./BFormat_BrigeWaterHall.wav')
RIRs = np.array(RIRs)

##############################################################
# RSAO estimation
##############################################################
x_dim = float(input('Input the length oh the x dimension of the room: '))
y_dim = float(input('Input the length oh the y dimension of the room: '))
z_dim = float(input('Input the length oh the z dimension of the room: '))
RoomDims = [x_dim, y_dim, z_dim]
#RoomDims = [23.97, 32.22, 21.89]  # This are the dimensions related to the example (i.e. Bridge Water Hall)

# Defining the early reflection object
EarlyReflections = EncoderSAOBFormat(RIRs=RIRs, discrete_mode='strongest')
# Calculating the early reflection parameters
EarlyReflections.direct_and_early_parameterization()

# Defining the late reverberation object
LateReverb = EncoderSAOBFormat(RIRs=RIRs, RoomDims=RoomDims, EarlyProperties=EarlyReflections.param)
# Calculating the late reverberation parameters
LateReverb.late_parameterization()

##############################################################
# Delete variables that are not needed
##############################################################
# Delete variables that are not needed in the objects
del EarlyReflections.EarlyProperties
del EarlyReflections.PeakVals
del EarlyReflections.RIRs
del EarlyReflections.RoomDims
del EarlyReflections.discrete_mode
del EarlyReflections.fs
del EarlyReflections.groupdelay_threshold
del EarlyReflections.nMics
del EarlyReflections.nPeaks
del EarlyReflections.n_discrete
del EarlyReflections.speed
del EarlyReflections.use_LPC
del LateReverb.EarlyProperties
del LateReverb.PeakVals
del LateReverb.RIRs
del LateReverb.RoomDims
del LateReverb.discrete_mode
del LateReverb.fs
del LateReverb.groupdelay_threshold
del LateReverb.nMics
del LateReverb.nPeaks
del LateReverb.n_discrete
del LateReverb.speed
del LateReverb.use_LPC

##############################################################
# Save objects
##############################################################
with open('RSAO_Early_params', 'wb') as output:
    pickler = pickle.Pickler(output, -1)
    pickler.dump(EarlyReflections)

with open('RSAO_Late_params', 'wb') as output:
    pickler = pickle.Pickler(output, -1)
    pickler.dump(LateReverb)

##############################################################
# Write json file containing BFormat-derived parameters
##############################################################
JsonFile = GenerateJSON_RSAO(paramEarly=EarlyReflections.param, paramLate=LateReverb.param, name='testroom',
                             maxEarly=10, filename='BridgeWaterHall_ls2.json', objtype='pointreverb')
JsonFile.getobjectvector_roomlibrary()
JsonFile.savejson()
