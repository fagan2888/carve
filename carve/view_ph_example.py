#!/usr/bin/env python
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
from ph_scan import *

# -- set the image name
fname = os.path.join("..", "data", "Delivery", "057773250100_01", 
                     "057773250100_01_P001_MUL", 
                     "17SEP29170931-M2AS-057773250100_01_P001.TIF")


# -- read in the scan
scan = PhScan(fname)

# -- plot
fig, ax = plt.subplots(2, 1, figsize=[4, 8])
fig.subplots_adjust(0.05, 0.05, 0.95, 0.95)
dum = [i.axis("off") for i in ax]
im0 = ax[0].imshow(scan.ndvi[::4, ::4], cmap="gist_gray", clim=[0.5, 0.75])
im1 = ax[1].imshow((2.0 * scan.rgb[::4, ::4]).clip(0, 1))
fig.canvas.draw()
plt.show()
