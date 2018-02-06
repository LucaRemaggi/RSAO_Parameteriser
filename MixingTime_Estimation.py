#
# This class contains some algorithms that are useful for signal processing.
#
# Author: Luca Remaggi
# Email: l.remaggi@surrey.ac.uk
# 06/02/2018

import numpy as np

class EstimatePerceptualMixingTime:
    # The methods in this class were translated from Matlab to Python by Luca Remaggi.
    # The methods were proposed by Lindau et al. in their "Perceptual Evaluation of Model- and Signal-Based
    # Predictors of the Mixing Time in Binaural Room Impulse Responses", JAES, 2012.

    def __init__(self, RoomDims):
        self.RoomDims = RoomDims
        self.mixing_time_estimate = {}

    def model_based(self):
        # Model-based predictors: V/S and V
        print('----------------------------------')
        print('MODEL-BASED MIXING TIME PREDICTION')
        print('----------------------------------')
        print('ROOM PROPERTIES:')

        x_d = self.RoomDims[0]
        y_d = self.RoomDims[1]
        z_d = self.RoomDims[2]
        try:
            x_d > 0
        except ValueError:
            print('RoomDims must contain positive, numeric values only.')
        try:
            y_d > 0
        except ValueError:
            print('RoomDims must contain positive, numeric values only.')
        try:
            z_d > 0
        except ValueError:
            print('RoomDims must contain positive, numeric values only.')

        print('Room dimensions: height = ' + str(x_d) + 'm, length = ' + str(y_d) + 'm, width = ' + str(z_d) + 'm')

        print('Perceptual mixing times tmp50 and tmp95 (in ms) from model-based predictors:')

        # Calculate room properties
        volume = x_d * y_d * z_d
        surface = 2*x_d*y_d + 2*x_d*z_d + 2*y_d*z_d

        print('Volume: ' + str(volume) + 'm3')
        print('Surface area: ' + str(surface) + 'm2')

        # Physical predictor
        rootvol = np.sqrt(volume)
        MFP = 47*volume/surface

        # Predict tmp from linear models
        tmp50 = 20.08 * volume/surface + 12
        print('tmp50: ' + str(tmp50) + 'ms')
        tmp95 = 0.0117 * volume + 50.1
        print('tmp95: ' + str(tmp95) + 'ms')

        self.mixing_time_estimate.update({'model': {'tmp50': tmp50}})
        self.mixing_time_estimate['model'].update({'tmp95': tmp95})
        self.mixing_time_estimate['model'].update({'rootV': rootvol})
        self.mixing_time_estimate['model'].update({'mfp_based': MFP})

        return self



