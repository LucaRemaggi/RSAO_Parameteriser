#
# This class contains some algorithms that are useful for signal processing.
#
# Author: Luca Remaggi
# Email: l.remaggi@surrey.ac.uk
# 05/02/2018

import numpy as np

class Beamformers:


    def __init__(self, signal, d=1, dimension='3D'):
        self.signal = signal
        self.d = d
        self.dimension = dimension
        self.az_rad_curr = None
        self.el_rad_curr = None
        self.hBeam = None

    def steerBFormat(self):
        try:
            self.signal.shape[1] == 4
        except ValueError:
            print('To use this beamformer the input must be B-format. The data shape should be Nx4, where N is the '
                  'number of samples')

        # The four channels
        W = self.signal[:, 0]
        X = self.signal[:, 1]
        Y = self.signal[:, 2]
        Z = self.signal[:, 3]

        # Defining the angles under investigation
        if self.dimension is 'az' or self.dimension is '3D':
            azimuths = np.linspace(0, np.pi*2-(np.pi/180), 360)
        else:
            azimuths = np.array([0, np.pi])

        if self.dimension is 'el' or self.dimension is '3D':
            elevations = np.linspace(-np.pi/2, np.pi/2, 181)
        else:
            elevations = np.array([0, np.pi/2])

        # Calculating the steered responses for different angles
        steeredresp = np.zeros([len(W), len(azimuths), len(elevations)])
        for iAz in range(0, len(azimuths)):
            for iEl in range(0, len(elevations)):
                # Converting from spherical to Cartesian
                r_x = np.cos(elevations[iEl]) * np.cos(azimuths[iAz])
                r_y = np.cos(elevations[iEl]) * np.sin(azimuths[iAz])
                r_z = np.sin(elevations[iEl])

                # Equation to steer a B-format signal towards a specific DOA
                steeredresp[:, iAz, iEl] = 0.5 * ((2-self.d)*W + self.d*(r_x*X + r_y*Y + r_z*Z))

        # Calculates the energy for each DOA
        angular_response = np.squeeze(np.sum(steeredresp**2, 0))

        # Find the direction of the max energy
        max_az, max_el = np.where(angular_response == np.max(angular_response))
        self.az_rad_curr = azimuths[max_az[0]]
        self.el_rad_curr = elevations[max_el[0]]
        self.hBeam = steeredresp[:, max_az[0], max_el[0]]

        return self
