#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import glob
import gdal
import numpy as np
import pandas as pd
from gdalconst import *
from ph_scan import *

# -- landsat
rast = gdal.Open(os.path.join("..", "data", "myearthexplorer", 
                          "LC08_L1TP_023031_20180427_20180502_01_T1_B10.TIF"))

arr  = rast.ReadAsArray()

nrow2, ncol2 = arr.shape

#ullat2, ullon2, lrlat2, lrlon2 = 42.80249, -89.80538, 40.68867, -86.93491
#ullat2, ullon2, lrlat2, lrlon2 = 42.83685, -89.80538, 40.65680, -86.93270
ullat2, ullon2, lrlat2, lrlon2 = 42.81482, -89.73062, 40.68886, -86.93511

# -- precision hawk
spath = os.path.join("..", "supplementary", "sites_geocoded.csv")
sites = pd.read_csv(spath)
lats  = sites.latitude.dropna().values
lons  = sites.longitude.dropna().values

cpath  = os.path.join("..", "data", "Delivery", "*", "*P00*MUL", "*.IMD")
clist  = np.array(sorted(glob.glob(cpath)))
cstrs  = [[line for line in open(i, "r")] for i in clist]
coords = np.zeros([len(clist), 4])

for ii, cstr in enumerate(cstrs):
    coords[ii] = [[float(line.split("=")[1][:-2]) for line in cstr if "ULLat" 
                   in line][0], 
                  [float(line.split("=")[1][:-2]) for line in cstr if "ULLon" 
                   in line][0], 
                  [float(line.split("=")[1][:-2]) for line in cstr if "LRLat" 
                   in line][0], 
                  [float(line.split("=")[1][:-2]) for line in cstr if "LRLon" 
                   in line][0]]

tlat = lats[1]
tlon = lons[1]
# tlat = 41.75955
# tlon = -88.34591

ind  = (tlat < coords[:, 0]) & (tlat >= coords[:, 2]) & \
    (tlon >= coords[:, 1]) & (tlon < coords[:, 3])

ullat, ullon, lrlat, lrlon = coords[ind][0]
scan = PhScan(clist[ind][0].replace(".IMD", ".TIF"))
nrow, ncol = scan.rgb.shape[:2]

# -- convert RGB to grayworld
rgb_ma = np.ma.array(scan.rgb)
rgb_ma.mask = np.dstack([rgb_ma.sum(2) == 0 for i in range(3)])
fac  = rgb_ma.mean(0).mean(0)
fac /= fac.max()
rgb_ma = ((3.0 * scan.rgb / fac).clip(0, 1))


# -- get it
deltlat = (lrlat2 - ullat2) / nrow2
r1 = int(round((ullat - ullat2)/deltlat))
r2 = int(round((lrlat - ullat2)/deltlat))
deltlon = (lrlon2-ullon2)/ncol2
c1 = int(round((ullon - ullon2)/deltlon))
c2 = int(round((lrlon - ullon2)/deltlon))


sub = arr[r1:r2, c1:c2]

from scipy.misc import imresize
foo = imresize(sub, rgb_ma.shape[:2])


imshow(arr, "gist_gray")
ylim(3179, 2716)
xlim(6521, 7007)
arr.min()
arr.max()
clim(0, 4000)
clim(0, 10000)
clim(0, 20000)
clim(0, 30000)
clim(0, 20000)
clim(10000, 20000)
clim(15000, 20000)
clim(17000, 20000)
clim(17500, 20000)
clim(17500, 19000)
clim(17500, 21000)
clf()
imshow(arr)
42.81482
40.68886
dlat = (40.68886 - 42.81482) / 7951
dlat
42.81482 + dlat * 2716
42.81482 + dlat * 3179
-89.19648
-87.52823
dlon = (-87.52823 - -89.19648) / 7831
dlon
-89.19648 + dlon * 6521
-89.19648 + dlon * 7007

# 41.664554, -87.438089
