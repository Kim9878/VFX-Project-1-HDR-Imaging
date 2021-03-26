import numpy as np
import cv2
import os

def getBitmap(img):
    img = img.astype(np.float32) / 255
    gray_img = (54*img[:, :, 2] + 183*img[:, :, 1] + 19*img[:, :, 0]) / 256
    median = np.median(gray_img)
    binary_img = (gray_img > median) * 1.0
    mask_img = np.invert(cv2.inRange(gray_img, median-0.0156, median+0.0156).astype(bool)) * 1.0
    return binary_img, mask_img

def bitmapShift(img, xs, ys):
    h, w = img.shape[:2]
    M = np.float32([[1, 0, xs], [0, 1, ys]])
    shift_img = cv2.warpAffine(img, M, (w, h))
    return shift_img

def getShift(img1, img2, shift_bits):
    if shift_bits > 0:
        h, w = img1.shape[:2]
        sm_h, sm_w = int(h/2), int(w/2)
        sm_img1 = cv2.resize(img1, (sm_w, sm_h))
        sm_img2 = cv2.resize(img2, (sm_w, sm_h))
        cur_shift = getShift(sm_img1, sm_img2, shift_bits-1)
        cur_shift = 2 * cur_shift
    else:
        cur_shift = np.zeros([2], dtype=int)
    
    min_err = np.inf
    best_shift = cur_shift
    binary_img1, mask1 = getBitmap(img1)
    binary_img2, mask2 = getBitmap(img2)
    row, col = np.mgrid[-1:2, -1:2]
    for i, j in zip(row.reshape(-1,), col.reshape(-1,)):
        ys, xs = cur_shift[0]+i, cur_shift[1]+j
        shift_img2 = bitmapShift(binary_img2.copy(), xs, ys)
        shift_mask2 = bitmapShift(mask2.copy(), xs, ys)
        diff_b = cv2.bitwise_xor(binary_img1, shift_img2)
        diff_b = cv2.bitwise_and(diff_b, mask1)
        diff_b = cv2.bitwise_and(diff_b, shift_mask2)
        err = np.sum(diff_b)
        if err < min_err:
            min_err = err
            best_shift[0] = ys
            best_shift[1] = xs
    return best_shift

def align(src_imgs, shift_bits=6):
    align_imgs = [src_imgs[0]]
    
    for src_img in src_imgs[1:]:
        ys, xs = getShift(src_imgs[0], src_img, shift_bits)
        align_img = bitmapShift(src_img, xs, ys)
        align_imgs.append(align_img)

    return align_imgs