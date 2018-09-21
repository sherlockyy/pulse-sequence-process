import os
import sys
import struct
import numpy as np


def load_datafile(datafile, width=400, height=250):

    datafh = open(datafile, "rb")
    p = 0
    ivsLen = 1

    statinfo = os.stat(datafile)
    length = statinfo.st_size

    while p < length:
        datafh.seek(p)
        s = datafh.read(ivsLen)
        p += ivsLen
        bits = struct.unpack('B', s)

    frame = np.zeros((height, width), np.bool, 'C')


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("python filename")
        exit(0)
    filename = sys.argv[-1]
    load_datafile(filename)
