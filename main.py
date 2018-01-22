
from Encoder_SAO_Bformat import EncoderSAOBFormat
import scipy.io as sio
import numpy as np
import time
import matplotlib.pyplot as plt

start_time = time.time()

# Loading RIRs
matW = sio.loadmat('../AES_Milan/RIRs/SoundField_floor_W.mat')
rirW = matW['SoundField_floor_W_RIRs'][:, 1]
matX = sio.loadmat('../AES_Milan/RIRs/SoundField_floor_X.mat')
rirX = matX['SoundField_floor_X_RIRs'][:, 1]
matY = sio.loadmat('../AES_Milan/RIRs/SoundField_floor_Y.mat')
rirY = matY['SoundField_floor_Y_RIRs'][:, 1]
matZ = sio.loadmat('../AES_Milan/RIRs/SoundField_floor_Z.mat')
rirZ = matZ['SoundField_floor_Z_RIRs'][:, 1]
RIRs = np.empty([len(rirW), 4])
RIRs = [rirW, rirX, rirY, rirZ]
RIRs = np.transpose(np.array(RIRs))

# Defining the early reflection object
EarlyReflections = EncoderSAOBFormat(RIRs=RIRs, discrete_mode='strongest', RoomDims=[15, 25, 10])

# Calculating the early reflection parameters
p_pos = EarlyReflections.segmentation()

elapsed_time = time.time() - start_time

plt.plot(p_pos)
plt.show()

print(RIRs.shape)
print(p_pos.shape)
