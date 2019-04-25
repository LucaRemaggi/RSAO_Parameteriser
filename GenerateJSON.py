#
# Author: Luca Remaggi
# Email: l.remaggi@surrey.ac.uk
# 22/02/2018
#
# Ported in Python from the Matlab implementation of Philip Coleman

import numpy as np
import json


class GenerateJSON_RSAO():

    def __init__(self, paramEarly, paramLate, name, maxEarly, filename, objtype):
        self.paramEarly = paramEarly
        self.paramLate = paramLate
        self.name = name
        self.maxEarly = maxEarly
        self.filename = filename
        self.objtype = objtype
        self.libentry = []

    def getobjectvector_roomlibrary(self):
        ##############
        # Direct sound
        ##############
        self.libentry = {'name': self.name, 'type': self.objtype, 'id': 0, 'channels': 0, 'priority': 0, 'level': 1.0,
                         'position': {'az': '{:0.2f}'.format(self.paramEarly['Direct_sound']['doa'][0]),
                                      'el': '{:0.2f}'.format(self.paramEarly['Direct_sound']['doa'][1]),
                                      'radius': '1.00'},
                         'room': {'ereflect': []}}

        ###################
        # Early reflections
        ###################
        for idx_refl in range(1, self.maxEarly+1):

            # Instantiate temporary dictionary to then append it in the later loop
            tmpDictionary = {'level': '{:0.3e}'.format(self.paramEarly['Reflection'+str(idx_refl)]['level']),
                             'delay': '{:0.3e}'.format(self.paramEarly['Reflection'+str(idx_refl)]['toa']),
                             'position': {'az': '{:0.1f}'.format(self.paramEarly['Reflection'+str(idx_refl)]['doa'][0]),
                                          'el': '{:0.1f}'.format(self.paramEarly['Reflection'+str(idx_refl)]['doa'][1]),
                                          'refdist': '1.0'},
                             'biquadsos': []}

            # Instantiating another temporary dictionary that is going inside the other dictionary
            nbiquadparam = np.shape(self.paramEarly['Reflection'+str(idx_refl)]['filtersos'])[0]
            for idx_biquadparam in range(0, nbiquadparam):
                tmp = {'b0': '{:0.3e}'.format(self.paramEarly['Reflection'+str(idx_refl)]['filtersos'][idx_biquadparam][0]),
                       'b1': '{:0.3e}'.format(self.paramEarly['Reflection'+str(idx_refl)]['filtersos'][idx_biquadparam][1]),
                       'b2': '{:0.3e}'.format(self.paramEarly['Reflection'+str(idx_refl)]['filtersos'][idx_biquadparam][2]),
                       'a0': '{:0.3e}'.format(self.paramEarly['Reflection'+str(idx_refl)]['filtersos'][idx_biquadparam][3]),
                       'a1': '{:0.3e}'.format(self.paramEarly['Reflection'+str(idx_refl)]['filtersos'][idx_biquadparam][4]),
                       'a2': '{:0.3e}'.format(self.paramEarly['Reflection'+str(idx_refl)]['filtersos'][idx_biquadparam][5])}

                tmpDictionary['biquadsos'].append(tmp)

            self.libentry['room']['ereflect'].append(tmpDictionary)

        ####################
        # Late reverberation
        ####################
        self.libentry['room'].update({'lreverb': {'delay': '{:0.3e}'.format(self.paramLate['Late']['toa']),
                                                  'level': formatList(self.paramLate['Late']['level']),
                                                  'attacktime': formatList(self.paramLate['Late']['attacktimes']),
                                                  'decayconst': formatList(self.paramLate['Late']['expdecays'])}})

        return self

    def savejson(self):
        data = self.libentry
        with open(self.filename, 'w') as outfile:
            json.dump(data, outfile)


def formatList(list_val):
    val = ['{:0.2e}'.format(list_val[str(item)]) for item in range(1, len(list_val)+1)]
    val = ', '.join(val)
    return val