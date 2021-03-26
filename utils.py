import argparse
import os
import cv2
from PIL import Image
from PIL.ExifTags import TAGS

def parseArgse():
    parser = argparse.ArgumentParser()

    parser.add_argument('--s', type=int, default=2, help='The size of the shift bits use in the MTB function, default = 2')
    parser.add_argument('--l', type=float, default=10, help='The amount of smoothness of hdr function, default = 10')
    parser.add_argument('--k', type=int, default=5, help='The size of the gaussion filter use in the tonemapping, default = 5')
    parser.add_argument('--f', type=float, default=0.7, help='The compression factor of tone mapping, default = 0.7')
    parser.add_argument('--n', type=int, default=50, help='The number of the sample points uses for constructing g curve, default = 50')
    parser.add_argument('--i', type = str, default = './images/1', help='The input image folder path to execute hdr algorithm')
    parser.add_argument('--o', type = str, default = './outputs/1', help='The output image folder path to save results')
    parser.add_argument('--t', type=int, default=0, help='The tone mapping algorithm current uses. default = 0 (Bilateral)')
    parser.add_argument('--d', type=float, default=0.8, help='')
    parser.add_argument('--c', type=float, default=0.8, help='')
    parser.add_argument('--a', type=float, default=1, help='')

    args = parser.parse_args()

    return args

def checkExists(folder_path):
    os.makedirs(folder_path, exist_ok=True)


def readImages(folder_path):
    imgs_name = [f for f in os.listdir(folder_path) if f.endswith(('.png', '.jpg', '.PNG', '.JPG', '.JPEG'))]
    imgs = []
    
    for img_name in sorted(imgs_name):
        img = cv2.imread(os.path.join(folder_path, img_name))
        imgs.append(img)

    return imgs

def getExif(img_path, tag):
    img = Image.open(img_path)
    exifdata = img.getexif()
    for tag_id in exifdata:
        tag_name = TAGS.get(tag_id, tag_id)
        if tag_name == tag:
            data = exifdata.get(tag_id)
            if isinstance(data, bytes):
                data = data.decode()
            return data
    return None

def readExpTime(folder_path):
    imgs_name = [f for f in os.listdir(folder_path) if f.endswith(('.png', '.jpg', '.PNG', '.JPG', '.JPEG'))]
    exposure_times = []

    for img_name in sorted(imgs_name):
        exposure_time = getExif(os.path.join(folder_path, img_name), "ExposureTime")
        exposure_times.append(float(exposure_time))

    return exposure_times