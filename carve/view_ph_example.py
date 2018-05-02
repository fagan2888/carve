#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import gdal
import time
import numpy as np
import matplotlib.pyplot as plt
from gdalconst import *

# -- set the image name
fname = os.path.join("..", "data", "Delivery", "057773250100_01", 
                     "057773250100_01_P001_MUL", 
                     "17SEP29170931-M2AS-057773250100_01_P001.TIF")


# -- open the TIF file
print("reading {0}...".format(fname))
rast = gdal.Open(fname, GA_ReadOnly)


# -- extract data to array
print("extracting to array... "), 
t0  = time.time()
img = rast.ReadAsArray()
print("(extracted in {0}s)".format(time.time() - t0))


# -- rescale to 0 to 1
print("rescaling...")
imgs = img / float(img.max())


# -- renormalize by hand
fac    = np.array([1.260825e-02, 9.713071e-03, 1.103623e-02, 1.224380e-02])
norm   = fac / fac.max()
imnorm = imgs.transpose(1, 2, 0) * norm


# -- set rgb
rgb = imnorm[..., :3][..., ::-1]


# -- calculate NDVI
sub  = (imnorm[:, :, 3] - imnorm[:, :, 2])
add  = (imnorm[:, :, 3] + imnorm[:, :, 2])
ndvi = sub / (add + (add == 0))


# -- plot
fig, ax = plt.subplots(2, 1, figsize=[4, 8])
fig.subplots_adjust(0.05, 0.05, 0.95, 0.95)
dum = [i.axis("off") for i in ax]
im0 = ax[0].imshow(ndvi[::4, ::4], cmap="gist_gray", clim=[0.5, 0.75])
im1 = ax[1].imshow((2.0 * rgb[::4, ::4]).clip(0, 1))
fig.canvas.draw()
plt.show()
