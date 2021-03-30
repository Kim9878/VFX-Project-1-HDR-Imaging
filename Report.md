# VFX HW 1 HDR Imaging Report

R09922074 潘奕廷 R09922139 蕭延儒

## Introduction
High dynamic range (HDR) images have much larger dynamic ranges than traditional images' 256 levels. In addition, they correspond linearly to physical irradiance values of the scene. Hence, they are useful for many graphics and vision applications. In this assignment, we are required to complete the following tasks to assemble an HDR image in a group of two.  
Besides finishing basic HDR image reconstruction task, we also completed image alignment method & two different tone mapping methods.

## Image Alignment
We implement the image alignment method by Ward's Median Threshold Bitmap(MTB) alignment. The following are our implementation steps:  

### Preprocessing
Before starting to search for the optimal offset, the first thing we need to do is to convert the RGB images to grayscale images.  
We follow the formula in the paper to convert RGB images to grayscale images:  

<a href="https://www.codecogs.com/eqnedit.php?latex=grey&space;=&space;(54*red&space;&plus;&space;183*green&space;&plus;&space;19*blue)&space;/&space;256" target="_blank"><img src="https://latex.codecogs.com/gif.latex?grey&space;=&space;(54*red&space;&plus;&space;183*green&space;&plus;&space;19*blue)&space;/&space;256" title="grey = (54*red + 183*green + 19*blue) / 256" /></a>  

Second, we construct bitmap images by thresholding the input grayscale images using median of intensities.The 0's in the bitmap images means the input pixels are less than or equal to the median value, while 1's are greater than the median value.

Third, we remove threshold noise. We follow the steps from paper to create the exclusion bitmaps. It consists of 0's whose grayscale value is within some specified distance of the threshold, and 1's is elsewhere. We zero all bits where pixels are within ± 4 of median value.

### Search for the optimal offset
The shift bits range is a parameter controlled by user, the default value is 2 without specified, It means that we will search within a range of ±2<sup>shift bits</sup>. We compare the images with the first image. Then, scale by 2 when passing down and try its 9 neighbors to find the minimum difference. The difference is calculated by three steps: XOR with bitmaps, AND with exclusion maps, and Bit counting by table lookup.

## High Dynamic Range Imaging
We implement Debevec's method by the way shown in class. The following are our implementation steps:  

### Pixel Sampling
The number of pixel sampling N is a parameter controlled by user, the default value is 50. We randomly sample N points in min(W, H), which W, H are width & height of images respectively, and store the pixel value of the same positon into other images.

### Recover Response Curve
Accrording to the paper, we add hat weight function <a href="https://www.codecogs.com/eqnedit.php?latex=w" target="_blank"><img src="https://latex.codecogs.com/gif.latex?w" title="w" /></a> to the objective function, which is used to reduce the effect of the extreme pixel value.   
The formula is defined as follows:  
<a href="https://www.codecogs.com/eqnedit.php?latex=w(z)=\begin{cases}&space;z-Z_{min},\space&space;for&space;\space&space;z&space;\le&space;\frac{1}{2}(Z_{min}&plus;Z_{max})\\&space;Z_{max}-z,&space;\space&space;for&space;\space&space;z&space;>&space;\frac{1}{2}(Z_{min}&plus;Z_{max})&space;\end{cases}" target="_blank"><img src="https://latex.codecogs.com/gif.latex?w(z)=\begin{cases}&space;z-Z_{min},\space&space;for&space;\space&space;z&space;\le&space;\frac{1}{2}(Z_{min}&plus;Z_{max})\\&space;Z_{max}-z,&space;\space&space;for&space;\space&space;z&space;>&space;\frac{1}{2}(Z_{min}&plus;Z_{max})&space;\end{cases}" title="w(z)=\begin{cases} z-Z_{min},\space for \space z \le \frac{1}{2}(Z_{min}+Z_{max})\\ Z_{max}-z, \space for \space z > \frac{1}{2}(Z_{min}+Z_{max}) \end{cases}" /></a>  

Then we split the images to R, G, B channels and solve least-square solution separately by constructing optimization matrix <a href="https://www.codecogs.com/eqnedit.php?latex=\inline&space;Ax&space;=&space;b" target="_blank"><img src="https://latex.codecogs.com/gif.latex?\inline&space;Ax&space;=&space;b" title="Ax = b" /></a> traught in class. The solution <a href="https://www.codecogs.com/eqnedit.php?latex=\inline&space;x" target="_blank"><img src="https://latex.codecogs.com/gif.latex?\inline&space;x" title="x" /></a> can be calculated by numpy function : ```np.linalg.lstsq(A, b, rcond=None). ```  
After solving the equation, response curve is mapped to the top 256 value of vector <a href="https://www.codecogs.com/eqnedit.php?latex=\inline&space;x" target="_blank"><img src="https://latex.codecogs.com/gif.latex?\inline&space;x" title="x" /></a>. The response curve of R, G, B channels are shown below.

### Reconstruct Radiance Map
After colculating response curve of R, G, B channels, we follow the formula as below to reconstruct the log of radiance map:  

<a href="https://www.codecogs.com/eqnedit.php?latex=\inline&space;lnE_i&space;=&space;\dfrac{\sum^P_{j=1}w(Z_{ij})(g(Z_{ij})&space;-&space;ln\Delta&space;t_j)}{\sum^P_{j=1}w(Z_{ij})}" target="_blank"><img src="https://latex.codecogs.com/gif.latex?\inline&space;lnE_i&space;=&space;\dfrac{\sum^P_{j=1}w(Z_{ij})(g(Z_{ij})&space;-&space;ln\Delta&space;t_j)}{\sum^P_{j=1}w(Z_{ij})}" title="lnE_i = \dfrac{\sum^P_{j=1}w(Z_{ij})(g(Z_{ij}) - ln\Delta t_j)}{\sum^P_{j=1}w(Z_{ij})}" /></a>

Finally, we input the log of radiance map into the exponential function and get the radiance map.

## Tone Mapping
We implement two different tone mapping methods to map the HDR image to 0-255 pixel value.  
Both of the implementation steps are shown below.

* ### Dynamic Range Reduction Inspired by Photoreceptor Physiology
    This tone-mapping algorithm can be classified into two broad categories: global and local operators.  
    ### Luminance
    The luminance is computed for creating the tonemapping curve.  
    <a href="https://www.codecogs.com/eqnedit.php?latex=luminance&space;=&space;0.2125*red&space;&plus;&space;0.7154*green&space;&plus;&space;0.0721*blue" target="_blank"><img src="https://latex.codecogs.com/gif.latex?luminance&space;=&space;0.2125*red&space;&plus;&space;0.7154*green&space;&plus;&space;0.0722*blue" title="luminance = 0.2125*red + 0.7154*green + 0.0722*blue" /></a> 
    ### parameters
    * <a href="https://www.codecogs.com/eqnedit.php?latex=\inline&space;m" target="_blank"><img src="https://latex.codecogs.com/gif.latex?\inline&space;m" title="m" /></a> describes the contrast of the image  
    * <a href="https://www.codecogs.com/eqnedit.php?latex=\inline&space;f=exp(f')" target="_blank"><img src="https://latex.codecogs.com/gif.latex?\inline&space;f=exp(f')" title="f=exp(f')" /></a> describes the overall intensity of the image  
    * <a href="https://www.codecogs.com/eqnedit.php?latex=\inline&space;c" target="_blank"><img src="https://latex.codecogs.com/gif.latex?\inline&space;c" title="c" /></a> describes Chromatic adaption of the original image  
    * <a href="https://www.codecogs.com/eqnedit.php?latex=\inline&space;a" target="_blank"><img src="https://latex.codecogs.com/gif.latex?\inline&space;a" title="a" /></a> describes light Adaption of the original image  
    ### Global Operator
    The global operator compresses contrasts based on the whole image.  
    The formula is as below:  
    
    <a href="https://www.codecogs.com/eqnedit.php?latex=I_G&space;=&space;c*C_a_v&space;&plus;&space;(1-c)*L_a_v&space;" target="_blank"><img src="https://latex.codecogs.com/gif.latex?I_G&space;=&space;c*C_a_v&plus;&space;(1-c)*L_a_v&space;" title="I_G = c*C_a_v + (1-c)*L_a_v" /> ,</a>
    
    <a target="_blank">where <img src="https://latex.codecogs.com/gif.latex?C_a_v" title="I_G = c*C_a_v + (1-c)*L_a_v" /> is the color channel's average.</a>
    ### Local Operator
    The local operator compresses contrasts based on the neighboring pixels.  
    The formula is as below:
    
    <a href="https://www.codecogs.com/eqnedit.php?latex=I_L&space;=&space;c*PixelValue&space;&plus;&space;(1-c)*L&space;" target="_blank"><img src="https://latex.codecogs.com/gif.latex?I_L&space;=&space;c*PixelValue&plus;&space;(1-c)*L&space;" title="I_L = c*PixelValue + (1-c)*L" /></a> 
    ### Conversion
    The final operator is combined with the two mentioned operators  
    The formula is as below:  
    
     <a href="https://www.codecogs.com/eqnedit.php?latex=I_A&space;=&space;a*I_L&space;&plus;&space;(1-a)*I_G&space;" target="_blank"><img src="https://latex.codecogs.com/gif.latex?I_A&space;=&space;a*I_L&plus;&space;(1-a)*I_G&space;" title="I_A = a*I_L + (1-a)*I_G" /></a> 
     
     After we get the final operator, we use it to do the conversion.  
     The formula is as below:  
     <a href="https://www.codecogs.com/eqnedit.php?latex=OutputPixel&space;=&space;PixelValue&space;/&space;[PixelValue&plus;&space;(f*I_A)^m&space;]" target="_blank"><img src="https://latex.codecogs.com/gif.latex?OutputPixel&space;=&space;PixelValue&space;/&space;[PixelValue&plus;&space;(f*I_A)^m&space;]" title="OutputPixel = PixelValue / [PixelValue+(f*I_A)^m]" /></a> 
     ### Normalization
    After the mapping of the image, we normalize the color channel to the range of 0<a href="https://www.codecogs.com/eqnedit.php?latex=\inline&space;\sim" target="_blank"><img src="https://latex.codecogs.com/gif.latex?\inline&space;\sim" title="\sim" /></a>1. And then we convert them to the range of 0<a href="https://www.codecogs.com/eqnedit.php?latex=\inline&space;\sim" target="_blank"><img src="https://latex.codecogs.com/gif.latex?\inline&space;\sim" title="\sim" /></a>255.
    
* ### Fast Bilateral Filtering for the Display of High Dynamic Range Images

    ### Intensity Calculation
    We devided the HDR image into intensity field and color field.
    The converted formulas are as below:  
    
    <a href="https://www.codecogs.com/eqnedit.php?latex=intensity&space;=&space;0.2126*red&space;&plus;&space;0.7152*green&space;&plus;&space;0.0722*blue" target="_blank"><img src="https://latex.codecogs.com/gif.latex?intensity&space;=&space;0.2126*red&space;&plus;&space;0.7152*green&space;&plus;&space;0.0722*blue" title="intensity = 0.2126*red + 0.7152*green + 0.0722*blue" /></a>  
    <a href="https://www.codecogs.com/eqnedit.php?latex=color&space;=&space;pixel&space;value&space;/&space;intensity" target="_blank"><img src="https://latex.codecogs.com/gif.latex?color&space;=&space;pixel&space;value&space;/&space;intensity" title="color = pixel value / intensity" /></a>  
    
    After the conversion, we take the intensity field into log function and get the log intensity in order to reduce the difference between adjacent pixels.
    
    ### Bilateral Filter
    After finishing intensity calculation, we apply the 5x5 bilateral filter to log intensity to calcalate the large scale intensity.  
    The bilateral filter function is defined as below:  
    <a href="https://www.codecogs.com/eqnedit.php?latex=\inline&space;J(x)&space;=&space;\frac{1}{k(x)}*\sum_{x_i&space;\in&space;\xi}f(\parallel&space;x_i&space;-&space;x&space;\parallel)*g(\parallel&space;I(x_i)&space;-&space;I(x)\parallel)*I(x_i)" target="_blank"><img src="https://latex.codecogs.com/gif.latex?\inline&space;J(x)&space;=&space;\frac{1}{k(x)}*\sum_{x_i&space;\in&space;\xi}f(\parallel&space;x_i&space;-&space;x&space;\parallel)*g(\parallel&space;I(x_i)&space;-&space;I(x)\parallel)*I(x_i)" title="J(x) = \frac{1}{k(x)}*\sum_{x_i \in \xi}f(\parallel x_i - x \parallel)*g(\parallel I(x_i) - I(x)\parallel)*I(x_i)" /></a>
    
    The notations are defined as below:  
    * <a href="https://www.codecogs.com/eqnedit.php?latex=\inline&space;J(x)" target="_blank"><img src="https://latex.codecogs.com/gif.latex?\inline&space;J(x)" title="J(x)" /></a> is the bilateral filter function  
    * <a href="https://www.codecogs.com/eqnedit.php?latex=\inline&space;\xi" target="_blank"><img src="https://latex.codecogs.com/gif.latex?\inline&space;\xi" title="\xi" /></a> is the gaussion domain which size is 5x5  
    * <a href="https://www.codecogs.com/eqnedit.php?latex=\inline&space;f(x)" target="_blank"><img src="https://latex.codecogs.com/gif.latex?\inline&space;f(x)" title="f(x)" /></a> is a gaussion function with <a href="https://www.codecogs.com/eqnedit.php?latex=\inline&space;\sigma_f&space;=&space;1000" target="_blank"><img src="https://latex.codecogs.com/gif.latex?\inline&space;\sigma_f&space;=&space;1000" title="\sigma_f = 1000" /></a>  
    * <a href="https://www.codecogs.com/eqnedit.php?latex=\inline&space;g(x)" target="_blank"><img src="https://latex.codecogs.com/gif.latex?\inline&space;g(x)" title="g(x)" /></a> is a gaussion function with <a href="https://www.codecogs.com/eqnedit.php?latex=\inline&space;\sigma_g&space;=&space;2000" target="_blank"><img src="https://latex.codecogs.com/gif.latex?\inline&space;\sigma_g&space;=&space;2000" title="\sigma_g = 2000" /></a>  
    * <a href="https://www.codecogs.com/eqnedit.php?latex=\inline&space;I(x)" target="_blank"><img src="https://latex.codecogs.com/gif.latex?\inline&space;I(x)" title="I(x)" /></a> is the log intensity value of point <a href="https://www.codecogs.com/eqnedit.php?latex=\inline&space;x" target="_blank"><img src="https://latex.codecogs.com/gif.latex?\inline&space;x" title="x" /></a>  
    * <a href="https://www.codecogs.com/eqnedit.php?latex=\inline&space;k(x)&space;=&space;\sum_{x_i&space;\in&space;\xi}f(\parallel&space;x_i&space;-&space;x&space;\parallel)*g(\parallel&space;I(x_i)&space;-&space;I(x)\parallel)" target="_blank"><img src="https://latex.codecogs.com/gif.latex?\inline&space;k(x)&space;=&space;\sum_{x_i&space;\in&space;\xi}f(\parallel&space;x_i&space;-&space;x&space;\parallel)*g(\parallel&space;I(x_i)&space;-&space;I(x)\parallel)" title="k(x) = \sum_{x_i \in \xi}f(\parallel x_i - x \parallel)*g(\parallel I(x_i) - I(x)\parallel)" /></a>  
    
    After bilateral filter, we can calculate detail intensity field by subtracting large scale intensity from log intensity.The detail intensity field can retain the detail of the original image, and won't be blurred by gaussian filter after executing bilateral filter.
    
    ### Constrast Reduction
    The compression factor <a href="https://www.codecogs.com/eqnedit.php?latex=\inline&space;cf" target="_blank"><img src="https://latex.codecogs.com/gif.latex?\inline&space;cf" title="cf" /></a> is a parameter controlled by user, if not specified the default value is 0.7. We multiply large scale intensity by the compression factor in order to compress large scale feature. After that, we add detail intensity field back to the large scale intensity field to create the new log intensity image.  
    Finally, we input the log intensity image into the exponential function and merge the intensity field with color field by multiplying them together to get the tone mapping result.
    
    ### Normalization & Rescaling
    After getting the tone mapping output, we normalize the output from 0 and 255. However, the normalized output is still too dark, so we rescale the image by the original images' mean.  
    The formula is as below:  
    <a href="https://www.codecogs.com/eqnedit.php?latex=\inline&space;N(x)&space;=&space;x&space;*&space;Mean(OriginImages)/Mean(Output)" target="_blank"><img src="https://latex.codecogs.com/gif.latex?\inline&space;N(x)&space;=&space;x&space;*&space;Mean(OriginImages)/Mean(Output)" title="N(x) = x * Mean(OriginImages)/Mean(Output)" /></a>  
    
    The notations are defined as below:
    * <a href="https://www.codecogs.com/eqnedit.php?latex=\inline&space;N(x)" target="_blank"><img src="https://latex.codecogs.com/gif.latex?\inline&space;N(x)" title="N(x)" /></a> is the normalization function of <a href="https://www.codecogs.com/eqnedit.php?latex=\inline&space;x" target="_blank"><img src="https://latex.codecogs.com/gif.latex?\inline&space;x" title="x" /></a>
    * <a href="https://www.codecogs.com/eqnedit.php?latex=\inline&space;Mean(OriginImages)" target="_blank"><img src="https://latex.codecogs.com/gif.latex?\inline&space;Mean(OriginImages)" title="Mean(OriginImages)" /></a> is the weighted average of the original images. The weight function <a href="https://www.codecogs.com/eqnedit.php?latex=\inline&space;w" target="_blank"><img src="https://latex.codecogs.com/gif.latex?\inline&space;w" title="w" /></a> is the same as the one used in HDR response curve reconstruction task
    
## Experiments

### Experment 1

### Input
We shoot the photos with focal length 30mm, aperture f/1.4, and shutter speed 1/2 sec, 1/4 sec, 1/8 sec, 1/15 sec, 1/30 sec, 1/60 sec, 1/125 sec, 1/250 sec, 1/500 sec, 1/1250 sec respectively.  

![](https://i.imgur.com/GuYNB7f.jpg)

### Response Curve
![](https://i.imgur.com/O0vALU1.png)

### Output
![](https://i.imgur.com/ahsvWUJ.jpg)

### Experment 2

### Input
We shoot the photos with focal length 30mm, aperture f/1.4, and shutter speed 1/2 sec, 1/4 sec, 1/8 sec, 1/15 sec, 1/30 sec, 1/60 sec, 1/125 sec, 1/250 sec, 1/500 sec, 1/1000 sec, 1/2000 sec respectively.  

![](https://i.imgur.com/tznL01S.jpg)


### Response Curve
![](https://i.imgur.com/Kx5EKgK.png)


### Output
![](https://i.imgur.com/sDYVmAC.jpg)



