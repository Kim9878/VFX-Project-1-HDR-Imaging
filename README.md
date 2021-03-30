# VFX Project 1 HDR Imaging 
R09922074 潘奕廷 R09922139 蕭延儒

## Introduction
High dynamic range (HDR) images have much larger dynamic ranges than traditional images' 256 levels. In addition, they correspond linearly to physical irradiance values of the scene. Hence, they are useful for many graphics and vision applications. In this assignment, we are required to complete the following tasks to assemble an HDR image in a group of two.  
Besides finishing basic HDR image reconstruction task, we also completed image alignment method & two different tone mapping methods.

## Program Usage
To reproduce our sesult, simply run:  
```
python3 hdr.py --i ./images/4 --o ./outputs/4 --t 0
```
### Arguments
* **i:** The input image folder path to execute hdr algorithm
* **o:** The output image folder path to save results
* **s:** The size of the shift bits use in the MTB function, default is 2
* **l:** The amount of smoothness of hdr function, default is 10
* **k:** The size of the gaussian filter use in the tone mapping, default is 5
* **f:** The compression factor of Durand's tone mapping, default is 0.7
* **n:** The number of the sample points use for constructing response curve, default is 50
* **t:** [0, 1] The tone mapping algorithm current uses. default is 0 (Bilateral)
* **d:** [-0.8, 0.8]. Parameter of Reinhard's tone mapping. It controls intensity. Default is 0
* **c:** [0.0, 1.0]. Parameter of Reinhard's tone mapping. It controls chromatic adaptation. Default is 0
* **a:** [0.0, 1.0]. Parameter of Reinhard's tone mapping. It controls light adaptation. Default is 0

For detail about our implementation, please check out the [report](https://github.com/Kim9878/VFX-Project-1-HDR-Imaging/blob/master/Report.md) page.
