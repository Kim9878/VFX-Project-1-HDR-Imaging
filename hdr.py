import numpy as np
import os
import cv2
import glob
from utils import *
from alignment import align
from toneMapping import reinhard_photoreceptor, durand_bilateral, rescaleOutput

def gsolve(Z, B, l, w):
    n = 256
    N, P = Z.shape[:2]
    
    A = np.zeros([N*P+n+1, n+N])
    b = np.zeros([A.shape[0], 1])
    
    # include the data-fitting equations
    k = 0
    for i in range(N):
        for j in range(P):
            wij = w[Z[i, j]]
            A[k, Z[i, j]] = wij
            A[k, n+i] = -wij
            b[k, 0] = wij * B[j]
            k = k + 1
    
    # fix the curve by setting its middle value to 0
    A[k, 127] = 1
    k = k + 1
    
    # include the smoothness equations
    for i in range(n-2):
        A[k, i] = l * w[i+1]
        A[k, i+1] = -2 * l * w[i+1]
        A[k, i+2] = l * w[i+1]
        k = k + 1
    
    # solve the system using SVD
    x = np.linalg.lstsq(A, b, rcond=None)[0]
    g = x[:n].flatten()
    lE = x[n+1:].flatten()
    
    return g, lE

def genlE(Z, B, g, w):
    P, height, width = Z.shape
    d = np.sum(w[Z], axis=0)
    n = np.sum(w[Z] * (g[Z] - B.reshape(P, 1, 1)), axis=0)
    d[d <= 0] = 1
    lE = (n / d).reshape([height, width])
    return lE

if __name__ == '__main__':

    args = parseArgse()

    # read input ldr images
    input_folder = args.i
    output_folder = args.o
    output_align_folder = os.path.join(output_folder, 'alignment')
    checkExists(output_folder)
    checkExists(output_align_folder)

    src_imgs = readImages(input_folder)
    exposure_times = readExpTime(input_folder)


    # start aligning
    align_imgs = align(src_imgs, args.s)
    for i, align_img in enumerate(align_imgs):
        cv2.imwrite(os.path.join(output_align_folder, f'{i}.png'), align_img)

    # start constructing hdr image
    N = args.n # the number of sample points
    l = args.l # the amount of smoothness of hdr function
    height, width, channels = align_imgs[0].shape
    sample_index = np.random.randint(min(height, width), size=(N, 2))

    Z = np.zeros([N, len(align_imgs), 3])
    for i in range(N):
        for j in range(len(align_imgs)):
            Z[i][j] = align_imgs[j][sample_index[i][0], sample_index[i][1]]
    Z = Z.astype(int)

    w = np.zeros([256])
    for i in range(256):
        w[i] = i if i <= 127 else 255 - i

    # calculate g curve of r, g, b channels
    Z_r = Z[:, :, 2]
    g_r, _ = gsolve(Z_r, np.log(exposure_times), l, w)

    Z_g = Z[:, :, 1]
    g_g, _ = gsolve(Z_g, np.log(exposure_times), l, w)

    Z_b = Z[:, :, 0]
    g_b, _ = gsolve(Z_b, np.log(exposure_times), l, w)

    # calculate radiance map
    imgs = np.array(align_imgs)
    Z_r = imgs[:, :, :, 2]
    lE_r = genlE(Z_r.copy(), np.log(exposure_times), g_r, w)

    Z_g = imgs[:, :, :, 1]
    lE_g = genlE(Z_g.copy(), np.log(exposure_times), g_g, w)

    Z_b = imgs[:, :, :, 0]
    lE_b = genlE(Z_b.copy(), np.log(exposure_times), g_b, w)

    radiance_map = np.zeros([height, width, 3], dtype=np.float32)
    radiance_map[:, :, 0] = lE_b
    radiance_map[:, :, 1] = lE_g
    radiance_map[:, :, 2] = lE_r
    radiance_map = np.exp(radiance_map)

    cv2.imwrite(os.path.join(output_folder, 'hdr.hdr'), radiance_map)

    # start tone mapping
    if args.t == 0:
        c = args.f
        ldr = durand_bilateral(radiance_map, c)
        ldr = rescaleOutput(ldr, src_imgs, w)
    elif args.t == 1:
        f_d, c, a = args.d, args.c, args.a
        ldr = reinhard_photoreceptor(radiance_map, f_d, c, a)

    cv2.imwrite(os.path.join(output_folder, 'ldr.png'), ldr)

