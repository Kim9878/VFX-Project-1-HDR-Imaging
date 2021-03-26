import cv2
import numpy as np
import math

def cal_luminance(img):
    delta = 0.000001
    luminance = 0.2125 * img[:, :, 0] + 0.7154 * img[:, :, 1] + 0.0721 * img[:, :, 2]
    return luminance, np.max(luminance) + delta, np.min(luminance) + delta, np.mean(luminance) + delta

def rescaleOutput(img, src_imgs, w):
    src_imgs = np.array(src_imgs)
    P, height, width, channels = src_imgs.shape
    mean = np.sum(w[src_imgs] * src_imgs, axis=0) / (np.sum(w[src_imgs], axis=0) + 1e-6)
    rescale_img = (img * np.nanmean(mean, axis=tuple(range(mean.ndim-1))) / np.nanmean(img, axis=tuple(range(img.ndim-1)))).reshape([height, width, 3]) / 255
    rescale_img = (np.clip(rescale_img, 0, 1) * 255).astype(np.uint8)
    return rescale_img 

"""

Erik Reinhard, Kate Devlin, Dynamic Range Reduction Inspired by Photoreceptor Physiology, IEEE TVCG 2005.

"""
def reinhard_photoreceptor(hdr_img, f_d=0.8, c=0.8, a=1):
    delta = 0.000001
    h, w = hdr_img.shape[:2]

    Cavg = np.array([np.mean(hdr_img[:,:,0]), np.mean(hdr_img[:,:,1]), np.mean(hdr_img[:,:,2])])
    L, Lmax, Lmin, Lavg = cal_luminance(hdr_img)
    # print("Lmax: {}, Lavg: {}, Lmin: {}".format(Lmax, Lmin, Lavg))
    # print("math.log(Lmax): {}, math.log(Lmavg): {}, math.log(Lmin): {}".format(math.log(Lmax), math.log(Lavg), math.log(Lmin)))
    m = 0.3 + 0.7 * pow((math.log(Lmax) - math.log(Lavg)) / (math.log(Lmax) - math.log(Lmin)), 1.4)
    f = math.exp(-f_d)

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

"""

Fredo Durand, Julie Dorsey, Fast Bilateral Filtering for the Display of High Dynamic Range Images, SIGGRAPH 2002.

"""
def bilateralFilter(log_intensity, filter_size=5):
    def gaussian(x, mu, sig):
        return 1. / (np.sqrt(2. * np.pi) * sig) * np.exp(-np.power((x - mu) / sig, 2.) / 2)
    
    sig_f, sig_g = 1000., 2000.
    win_size = filter_size // 2
    output = np.zeros_like(log_intensity)
    k = np.zeros_like(log_intensity)
    for shift_y in range(-win_size, win_size+1):
        for shift_x in range(-win_size, win_size+1):
            f = gaussian(np.sqrt(shift_x ** 2 + shift_y ** 2), 0, sig_f)
            offsets = np.roll(log_intensity, [shift_y, shift_x], axis=[0, 1])
            g = gaussian(log_intensity-offsets, 0, sig_g)
            total_weight = f * g
            output += offsets * total_weight
            k += total_weight
    output /= k
    return output

def durand_bilateral(hdr, compression=0.8, filter_size=5):
    h, w, c = hdr.shape
    intensity = 0.0722 * hdr[:, :, 0] + 0.7152 * hdr[:, :, 1] + 0.2126 * hdr[:, :, 2]
    log_intensity = np.log(intensity)
    log_large_scale = bilateralFilter(log_intensity, filter_size)
    log_detail = log_intensity - log_large_scale
    log_output = log_large_scale * compression + log_detail
    ldr = hdr / intensity.reshape([h, w, 1]) * np.exp(log_output).reshape([h, w, 1])
    ldr = cv2.normalize(ldr, np.array([]), alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)
    return ldr