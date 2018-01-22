#
# This class contains some algorithms that are useful for signal peak 
# detection.
#
# Author: Luca Remaggi 
# Email: l.remaggi@surrey.ac.uk
# 11/01/2018

from scipy import signal
import numpy as np
from audiolazy import lazy_lpc as lpc
import math


def peaks_position(RIR, fs, groupdelay_threshold, use_LPC=1, cutoff_samples=5000, nLPC=12):
    # This method estimates the position of peaks in a room impulse response by applying the DYPSA algorithm

    # Saving the RIR in output for reference
    prev_rir = RIR

    # Check that cutoff_samples is integer
    cutoff_samples = np.int_(cutoff_samples)

    # General variables internal to this method
    prev_rir = RIR  # This is defined to allow future changes at the peak positions
    l_rir = len(RIR)
    RIR[cutoff_samples:l_rir] = 0

    if use_LPC == 1:
        # LPC for reduction of amount of data in RIR
        rir_up = signal.decimate(RIR, 2)
        l_rir_lpc = len(rir_up)

        # Calculate the matching AR filter based on the RIR
        ar = lpc.lpc(rir_up, nLPC)
        a = np.array(ar.numerator)
        b = np.array(ar.denominator)

        # Convert the filter into a time-reversed impulse response
        impulse = np.zeros(l_rir_lpc)
        impulse[0] = 1
        matched_forward = signal.lfilter(b, a, impulse)
        matched = np.flipud(matched_forward)

        # Apply the matched filter to the RIR
        rir_matched = signal.convolve(rir_up, matched)
        rir_matched = rir_matched[l_rir_lpc-1:]

        # Linearly interpolating
        RIR_new = signal.upfirdn([1], rir_matched, 2)

    # Realigning the new RIR with the original one
    val_max_new = np.argmax(abs(RIR_new))
    val_max_old = np.argmax(abs(prev_rir))
    diff_max = val_max_new - val_max_old
    if diff_max > 0:
        del RIR
        RIR = np.concatenate([RIR_new[diff_max:], np.zeros(diff_max)])
    elif diff_max < 0:
        del RIR
        RIR = np.concatenate([np.zeros(abs(diff_max)), RIR_new[:l_rir-abs(diff_max)]])
    else:
        del RIR
        RIR = RIR_new

    # Running the DYPSA algorithm
    tew, sew, y, toff = xewgrdel(RIR, fs)
    ntew = np.int_(np.round_(tew))

    # This avoids possible problems with sources too close to the microphones
    if ntew[0] < 0:
        ntew[0] = 0

    # Create an array which has zeros except for where tew defines peak positions
    k = 0
    peaks_init = np.zeros(l_rir)
    for idx_samp in range(0, len(y)):
        if k == len(ntew):
            break

        if idx_samp == ntew[k]:
            peaks_init[idx_samp] = 1
            k += 1

    # Peaks taken from the group-delay function where the slope is less than the threshold in input are deleted
    for idx_sew in range(0, len(sew)):
        if sew[idx_sew] > groupdelay_threshold:
            peaks_init[ntew[idx_sew]] = 0
    p_pos = peaks_init

    # Normalizing the RIR
    RIR = abs(RIR)
    norm_val = np.max(RIR)
    RIR = RIR / norm_val

    # Take the neighbourhood of the calculated position in the signal (which corresponds in total to 1ms) taking the rms
    # of the energy
    half_win = int(round(fs/2000))
    for idx_samp in range(0, len(ntew)):
        center = int(ntew[idx_samp])
        if (center - half_win) > 0:
            segment = RIR[center-half_win:center+half_win]
        else:
            segment = RIR[0:center+half_win]

        p_pos[center] = np.sqrt(np.mean(segment**2))

    ################################################################
    # From here there are additional improvements to the performance
    ################################################################
    # First, the array containing the peaks is normalized, and the position of the strongest peak found
    p_pos = p_pos / np.max(p_pos)
    ds_pos = int(np.argmax(p_pos))

    # Everything before the direct sound is equal to zero
    p_pos[:ds_pos-1] = 0

    # Deletes small errors by aligning the estimated direct sound position to the one in input
    ds_pos_gt = int(np.argmax(RIR))
    estimation_err = ds_pos_gt - ds_pos
    if estimation_err > 0:
        p_pos = list(p_pos)
        p_pos = [[0]*estimation_err + p_pos[estimation_err:]]
    elif estimation_err < 0:
        p_pos = list(p_pos)
        p_pos = [p_pos[abs(estimation_err):] + [0]*abs(estimation_err)]
    p_pos = np.transpose(np.array(p_pos))

    return p_pos


def xewgrdel(RIR, fs):
    # This is the DYPSA algorithm that has been translated from Matlab to Python. The DYPSA algorithm was first
    # presented in P. A. Naylor, A. Kounoudes, J. Gudnason and M. Brookes, ''Estimation of glottal closure instants in
    # voiced speech using the DYPSA algorithm'', IEEE Trans. on Audio, Speech and Lang. Proc., Vol. 15, No. 1, Jan. 2007

    # General variables
    dy_gwlen = 0.003
    dy_fwlen = 0.00045

    # Perform group delay calculation
    gw = np.int_(2 * np.floor(dy_gwlen*fs/2) + 1)  # Force window length to be odd
    ghw = signal.hamming(gw, 1)
    ghwn = np.squeeze(ghw * [np.array(range(gw-1, -gw, -2))/2])

    RIR2 = RIR ** 2
    yn = signal.lfilter(ghwn, [1], RIR2)
    yd = signal.lfilter(ghw, [1], RIR2)
    yd[abs(yd) < 10**-16] = 10**-16  # It prevents infinity
    y = yn[gw-1:] / yd[gw-1:]
    toff = (gw - 1) / 2
    fw = np.int_(2 * np.floor(dy_fwlen*fs/2) + 1)  # Force window length to be odd
    if fw > 1:
        daw = signal.hamming(fw, 1)
        y = signal.lfilter(daw, [1], y) / np.sum(daw)  # Low pass filtering
        toff = toff - (fw - 1)/2

    tew, sew = zerocross(x=y, m='n')  # Finding zero crossing

    tew = tew + toff

    return tew, sew, y, toff


def zerocross(x, m='b'):
    # This code is translated from the original version that was in Matlab, within the VOICEBOX toolbox
    # zerocross finds the zeros crossing in a signal

    x[abs(x) < 10**-5] = 0

    s = x >= 0
    s = np.int_(np.array(s))  # Converting false to 0 and true to 1
    k = s[1:] - s[:-1]
    if m is 'p':
        f = np.where(k > 0)
    elif m is 'n':
        f = np.where(k < 0)
    else:
        f = k != 0

    f = np.transpose(np.int_(f))

    s = np.subtract(x[f + 1], x[f])
    t = f - np.divide(x[f], s)

    return t, s


def clustering_dypsa():

    return


def findpeaks():

    return