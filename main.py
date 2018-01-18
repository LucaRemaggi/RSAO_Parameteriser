
from Encoder_SAO_Bformat import EncoderSAOBFormat
import scipy.io as sio
import numpy as np

# Loading RIRs
matW = sio.loadmat('../AES_Milan/RIRs/SoundField_floor_W.mat')
rirW = matW['SF_W_RIRs'][:, 1]
matX = sio.loadmat('../AES_Milan/RIRs/SoundField_floor_X.mat')
rirX = matX['SF_X_RIRs'][:, 1]
matY = sio.loadmat('../AES_Milan/RIRs/SoundField_floor_Y.mat')
rirY = matY['SF_Y_RIRs'][:, 1]
matZ = sio.loadmat('../AES_Milan/RIRs/SoundField_floor_Z.mat')
rirZ = matZ['SF_Z_RIRs'][:, 1]
RIRs = np.empty([len(rirW), 4])
RIRs = [rirW, rirX, rirY, rirZ]
RIRs = np.transpose(np.array(RIRs))

# Defining the early reflection object
EarlyReflections = EncoderSAOBFormat(RIRs=RIRs, RoomDims=[15, 25, 10])

# Calculating the early reflection parameters
p_pos = EarlyReflections.segmentation()


print(p_pos)

