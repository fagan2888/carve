#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import matplotlib.pyplot as plt
from utils import *
from ph_scan import *
from gen_cmap import *
from utils import *

# 17SEP18165731-M2AS-057773250010_01_P002.png
# 17SEP18165737-M2AS-057773250040_01_P001.png
# 17SEP29170932-M2AS-057773250120_01_P002.png

# -- get the file list and select the correct scan
clist = get_tif_list()
base  = "17SEP29170932-M2AS-057773250120_01_P002"
# base  = "17SEP29170928-M2AS-057773250050_01_P001"
fac  = 4
for cfile in clist:
    if base in cfile:
        gfile = cfile
        break

# -- read the scan
scan = PhScan(gfile)
rgb  = (3.0 * grayworld(scan.rgb)).clip(0, 1)[::fac, ::fac]
ndvi = scan.ndvi[::fac, ::fac]


# -- get coords
cstr = [line for line in open(gfile.replace(".TIF", ".IMD"), "r")]

coords = [[float(line.split("=")[1][:-2]) for line in cstr if "ULLat"
           in line][0],
          [float(line.split("=")[1][:-2]) for line in cstr if "ULLon"
           in line][0],
          [float(line.split("=")[1][:-2]) for line in cstr if "LRLat"
           in line][0],
          [float(line.split("=")[1][:-2]) for line in cstr if "LRLon"
           in line][0]]

# -- get lat lon arrays
nrow, ncol = ndvi.shape
dlat = (coords[2] - coords[0]) / float(nrow)
dlon = (coords[3] - coords[1]) / float(ncol)
lats = coords[0] + dlat * (np.arange(nrow * ncol) / ncol).reshape(nrow, ncol)
lons = coords[1] + dlon * (np.arange(nrow * ncol) % ncol).reshape(nrow, ncol)



# -- plot rgb
# rgb  = (3.0 * grayworld(scan.rgb)).clip(0, 1)[::2, ::2]
# ndvi = scan.ndvi[::2, ::2]

def change_label(event):

    if event.inaxes == ax:
        # get location
        irow = int(round(event.ydata))
        icol = int(round(event.xdata))

        # reset label
        txt_loc2.set_text("({0}, {1})".format(lats[irow, icol], 
                                              lons[irow, icol]))

        tndvi = ndvi[irow, icol]

        if tndvi < 0.1:
            txt_hl2.set_text(" ")
            txt_hl2.set_color("k")
        elif tndvi < 0.3:
            txt_hl2.set_text("poor")
            txt_hl2.set_color("crimson")
        elif tndvi < 0.6:
            txt_hl2.set_text("fair")
            txt_hl2.set_color("darkorange")
        else:
            txt_hl2.set_text("good")
            txt_hl2.set_color("lime")

        fig.canvas.draw()

    return

plt.close("all")
xs = 5.5
ys = xs * float(nrow) / float(ncol)
fig, ax = plt.subplots(figsize=(xs, ys), facecolor="k")
fig.subplots_adjust(0.05, 0.05, 0.95, 0.9)
ax.axis("off")
im  = ax.imshow(rgb)
xr  = ax.get_xlim()
yr  = ax.get_ylim()
dx  = xr[1] - xr[0]
dy  = yr[1] - yr[0]
txt_loc1 = fig.text(0.05, 0.95, "location:", 
                    color="w", size="x-large", ha="left")
txt_loc2 = fig.text(0.21, 0.95, "(0, 0)", 
                    color="w", ha="left")
txt_hl1 = fig.text(0.7, 0.95, "health: ", 
                   color="w", size="x-large", ha="left")
txt_hl2 = fig.text(0.925, 0.95, " ", 
                   color="k", size="x-large", ha="right")
fig.canvas.set_window_title(base)
fig.canvas.draw()
fig.canvas.mpl_connect("motion_notify_event", change_label)
plt.show()
