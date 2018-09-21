"""试图发现Spike信号的一些统计规律."""
import os
from time import time

import numpy as np
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

IVS_WIDTH = 400
IVS_HEIGHT = 250

def load_ivs(data_path, fnum):
    """Load several frames from an IVS data."""
    total_size = os.stat(data_path).st_size
    frame_size = IVS_WIDTH * IVS_HEIGHT // 8
    total_num = total_size // frame_size
    print(f'file contians {total_num}, load {fnum}({fnum / total_num:.2f}%) frames.')
    frames = np.zeros((fnum, IVS_HEIGHT, IVS_WIDTH), dtype=np.int8)
    f = open(data_path, 'rb')
    t = time()
    for k in range(fnum):
        buffer = f.read(IVS_WIDTH * IVS_HEIGHT // 8)
        # parse data using loop
        # for i in range(IVS_HEIGHT):
        #     for j in range(IVS_WIDTH):
        #         idx = i * IVS_WIDTH + j
        #         frames[k, i, j] = (buffer[idx // 8] >> (idx % 8)) & 1

        # parse data using matrix
        buffer = np.frombuffer(buffer, dtype=np.uint8).reshape((IVS_HEIGHT, IVS_WIDTH // 8))
        for i in range(8):
            frames[k, :, i::8] = np.bitwise_and(np.right_shift(buffer, i), 1)
    t = time() - t
    f.close()
    print(f'load finished. {t:.2f}s')
    return np.fliplr(np.flipud(frames))

def cvt_list(frames):
    """Convert an array like frames[frame, x, y] to (x, y, frame)."""
    fnum, width, height = frames.shape
    num = fnum * width * height
    x = np.zeros((num, ))
    y = np.zeros((num, ))
    frame = np.zeros((num, ))
    p = np.zeros((num, ))
    idx = 0
    for k in range(fnum):
        for i in range(height):
            for j in range(width):
                x[idx] = j
                y[idx] = i
                frame[idx] = k
                p[idx] = frames[k, j, i]
                idx += 1
    return x[p > 0], y[p > 0], frame[p > 0]

def cvt_hist(frames):
    """Convert an image array to hist."""
    fnum, height, width= frames.shape
    hist = []
    for i in range(width * height):
        hist.append([])
    print('generate hist...', end='\t')
    t = time()
    for k in range(fnum):
        y, x = np.where(frames[k, :, :] > 0)
        for i in range(y.shape[0]):
            # print(y[i], x[i], y[i] * width + x[i])
            hist[y[i] * width + x[i]].append(k)
    t = time() - t
    print(f'finished. {t:.2f}s')
    return hist

def plot_hist_var(hist):
    """Plot variance of every position in the hist."""
    figure = plt.figure()
    ax = figure.add_subplot(1, 1, 1)
    var_img = np.zeros((IVS_HEIGHT, IVS_WIDTH))

    for i in range(IVS_HEIGHT):
        for j in range(IVS_WIDTH):
            idx = i * IVS_WIDTH + j
            if len(hist[idx]) > 1:
                t = np.array(hist[idx])
                var_img[i, j] = np.std(t[1:] - t[:-1])
                # print(t[1:] - t[:-1])
            else:
                var_img[i, j] = 0
            # break
    ax.imshow(var_img, cmap='gray')
    ax.set_title('Var')


if __name__ == '__main__':
    seqs= ['bookflip.dat', 'campus.dat', 'disk-pku.dat', 'fork.dat', 'number-rotation.dat']
    seqs = '/home/code-xu/Dataset/PKU-Spike-Stationary'
    seq = 'disk-pku.dat'
    frames = load_ivs(f'/home/code-xu/Dataset/PKU-Spike-Stationary/{seq}', 30)
    figure_sum = plt.figure()

    plot_many = 0
    if plot_many:
        plot_h_num = 4
        plot_w_num = 4
        for i in range(plot_h_num * plot_w_num):
            ax = figure_sum.add_subplot(plot_h_num, plot_w_num, i + 1)
            sum_frame_num = i * 4 + 1
            img = np.sum(frames[:sum_frame_num, :, :], axis=0)
            ax.imshow(img, cmap='gray')
            ax.set_title(f'frame 0~{sum_frame_num}')
    else:
        ax = figure_sum.add_subplot(1, 1, 1)
        sum_frame_num = 30
        img = np.sum(frames[:sum_frame_num, :, :], axis=0)
        ax.imshow(img, cmap='gray')
        ax.set_title(f'frame 0~{sum_frame_num}')

    hist = cvt_hist(frames)
    plot_hist_var(hist)

    plt.show()
