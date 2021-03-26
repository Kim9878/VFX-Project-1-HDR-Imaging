# Based on Reinhard2005DRR

import cv2
import numpy as np
import math

def cal_luminance(img):
    delta = 0.000001
    luminance = 0.2125 * img[:,:,0] + 0.7154 * img[:,:,1] + 0.0721 * img[:,:,2]
    return luminance, np.max(luminance) + delta, np.min(luminance) + delta, np.mean(luminance) + delta

def tone_mapping_Reinhard2005DRR(hdr_img, f_d=0, c=0, a=1):
    delta = 0.000001
    h, w = hdr_img.shape[:2]

    Cavg = np.array([np.mean(hdr_img[:,:,0]), np.mean(hdr_img[:,:,1]), np.mean(hdr_img[:,:,2])])
    L, Lmax, Lmin, Lavg = cal_luminance(hdr_img)
    print("Lmax: {}, Lavg: {}, Lmin: {}".format(Lmax, Lmin, Lavg))
    print("math.log(Lmax): {}, math.log(Lmavg): {}, math.log(Lmin): {}".format(math.log(Lmax), math.log(Lavg), math.log(Lmin)))
    m = 0.3 + 0.7 * pow((math.log(Lmax) - math.log(Lavg)) / (math.log(Lmax) - math.log(Lmin)), 1.4)
    f = math.exp(-f_d)

    # 

    I_l = c * hdr_img + (1-c) * np.repeat(np.expand_dims(L, axis=2), 3, axis=2)
    I_g = c * Cavg + (1-c) * np.array([Lavg, Lavg, Lavg])
    I_g = np.repeat(np.repeat(np.expand_dims(np.expand_dims(I_g, axis=0), axis=0), h, axis=0), w, axis=1)
    I_a = a * I_l + (1-a) * I_g
    # print(hdr_img)
    # print("-------------")
    # print(np.power(I_a * f, m))
    # print("-------------")
    # print((hdr_img + np.power(I_a * f, m)))
    rgb_img = hdr_img / (hdr_img + np.power(I_a * f, m) + delta)

    # print(np.max(rgb_img[:,:,0]), np.min(rgb_img[:,:,0]))
    # print(np.max(rgb_img[:,:,1]), np.min(rgb_img[:,:,1]))
    # print(np.max(rgb_img[:,:,2]), np.min(rgb_img[:,:,2]))
    # print("-------")
    L, Lmax, Lmin, Lavg = cal_luminance(rgb_img)
    rgb_img = (rgb_img - Lmin) / (Lmax - Lmin) * 255
    return rgb_img



filenames = ["./memorial/memorial", "./sky/HDR_029_Sky_Cloudy_Ref", "./1/1"]
# filenames = ["./1/1"]
FDs = [0.8] # dark -0.8~0.8 bright
Cs = [0.8]  # less sat 0~1 sat
As = [1]    # 0~1
for filename in filenames:
    input_img = cv2.imread("{}.hdr".format(filename), flags = cv2.IMREAD_ANYDEPTH)
    print("image name: {}.hdr".format(filename))
    print("image shape = {}".format(input_img.shape))
    print("image range:")
    print("\rR:{} to {}".format(np.min(input_img[:,:,0]), np.max(input_img[:,:,0])))
    print("\rG:{} to {}".format(np.min(input_img[:,:,1]), np.max(input_img[:,:,1])))
    print("\rB:{} to {}".format(np.min(input_img[:,:,2]), np.max(input_img[:,:,2])))
    for FD in FDs:
        for C in Cs:
            for A in As:
                output_img = tone_mapping_Reinhard2005DRR(input_img, f_d=FD, c=C, a=A)
                cv2.imwrite("{}_fd_{}_c_{}_a_{}.jpg".format(filename, FD, C, A), output_img)
    print("-------------------")

'''

https://www.hdri-hub.com/hdrishop/freesamples/freehdri/item/76-hdr-sky-cloudy

'''