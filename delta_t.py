import os
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
from time import time


def load_datafile(datafile, fnum=0, width=400, height=250):
    statinfo = os.stat(datafile)
    length = statinfo.st_size
    datafh = open(datafile, "rb")

    max_frame = length * 8 // (height * width)
    if fnum == 0 or fnum > max_frame:
        fnum = max_frame

    frames1 = np.zeros((fnum, height, width), dtype=np.int8)
    for k in range(fnum):
        buffer = datafh.read(height * width // 8)
        buffer = np.frombuffer(buffer, dtype=np.uint8).reshape(height, width // 8)
        for i in range(8):
            frames1[k, :, i::8] = np.bitwise_and(np.right_shift(buffer, i), 1)

    return frames1

def find_delta(frames, ts):
    duration, height, width  = frames.shape
    t_before = np.zeros((height, width), dtype=np.uint32)
    t_after = np.zeros((height, width), dtype=np.uint32)
    if ts > duration or ts < 0:
        print(f'ts({ts}) must > 0 and < duration({duration})')
        exit(0)

    flags = np.zeros((height,width), dtype=np.bool)
    for t in range(ts-1, 0, -1):
        spike = frames[t]
        t_before[np.logical_and(spike==1, flags==0)] = t
        flags[spike==1] = 1
        if flags.min() == 1:
            break

    flags = np.zeros((height,width), dtype=np.bool)
    for t in range(ts, duration-1, 1):
        spike = frames[t]
        t_after[np.logical_and(spike==1, flags==0)] = t
        flags[spike==1] = 1
        if flags.min() == 1:
            break
    delta_t = t_after - t_before

    return delta_t

def calcu_residual(delta_t):
    height, width = delta_t.shape
    ii = 1
    kernel_size = 2 * ii + 1
    # conv_k = np.ones((kernel_size, kernel_size), dtype=np.int8)
    # conv_k[ii, ii] = 0
    conv_k = np.array([[0,0,0], [0,0,1], [1,1,1]])
    avg = signal.convolve(delta_t, conv_k, mode='same')
    resi = delta_t * 4 - avg
    resi = resi[ii:-ii, ii:-ii]

    return resi

def plot_histogram(data):
    plt.hist(data, bins=8, range=(-200,200), density=True)


if __name__ == "__main__":
    dat_list = ['bookflip', 'campus', 'disk-pku', 'fork', 'number-rotation', 'office', 'rolling', 'wavehand']
    root = '../dataset/PKU-Spike-Stationary'
    t_list = [10000, 20000, 50000, 100000]
    for filename in dat_list:
        fig = plt.figure(figsize=[20, 5])
        fig.suptitle(f'{filename}')
        path = os.path.join(root, filename + '.dat')
        frames1 = load_datafile(path)
        for i in range(len(t_list)):
            ts = t_list[i]
            delta_t = find_delta(frames1, ts)
            stat = calcu_residual(delta_t)
            ax = fig.add_subplot(1, len(t_list), i+1)
            ax.hist(stat, bins=8, range=(-100, 100), density=True)
            ax.set_title(f'ts={ts}')
        plt.show()
