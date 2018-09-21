import os
import sys
import struct
import numpy as np


def load_datafile(datafile, fnum=0, width=400, height=250):

    statinfo = os.stat(datafile)
    length = statinfo.st_size
    datafh = open(datafile, "rb")

    max_frame = length * 8 / (height * width)
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


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("python filename")
        exit(0)
    filename = sys.argv[-1]
    load_datafile(filename)
