import os
import sys
import struct
import numpy as np
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

    frames8 = np.zeros((fnum // 8, height, width), dtype=np.int8)
    for k in range(fnum // 8):
        buffer = np.zeros((height, width), dtype=np.int8)
        for i in range(8):
            buffer += np.left_shift(frames1[8*k + i, :, :], i)
        frames8[k] = buffer

    return frames8


def encode_yuv(yuvfile):

    yuv_root = './yuv'
    enc_root = './encode'
    infile = os.path.join(yuv_root, yuvfile + '.yuv')
    outfile = os.path.join(enc_root, yuvfile + '.265')
    cmd = 'ffmpeg -s 400x1000 -pix_fmt gray' + ' -i ' + infile + ' -lossless 1 -c:v libx265 -preset slow -frames 100' + ' ' + outfile
    # cmd = 'ffmpeg -s 400x1000 -pix_fmt gray' + ' -i ' + infile + ' -qp 0 -c:v libx265 -preset slow -frames 100' + ' ' + outfile
    print(cmd + '\n')
    os.system(cmd)

def decode_bin(binfile):

    bin_root = './encode'
    dec_root = './encode'
    infile = os.path.join(bin_root, binfile + '.265')
    outfile = os.path.join(dec_root, binfile + '.yuv')
    cmd = 'ffmpeg' + ' -i ' + infile + ' -c:v rawvideo' + ' ' + outfile
    print(cmd + '\n')
    os.system(cmd)


if __name__ == "__main__":
    dat_list = ['bookflip', 'campus', 'disk-pku', 'fork', 'number-rotation', 'office', 'rolling', 'wavehand']
    root = '../dataset/PKU-Spike-Stationary'
    for filename in dat_list:
        path = os.path.join(root, filename + '.dat')
        save_yuv = filename + '.yuv'
        # yuv = load_datafile(path)
        # yuv.tofile(save_yuv)
        t = time()
        encode_yuv(filename)
        t = time() - t
        print(f'encode finished. {t:.2f}s')
        decode_bin(filename)
