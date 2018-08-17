#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import numpy as np
from scipy.ndimage.filters import median_filter as mf
from scipy.ndimage.filters import uniform_filter as uf
from ph_scan import *

def phrag_map(bgrn, wid=10):
    """ Impose a model for phragmites on a scaled (R,G,B,N -> r,g,b,N/Nmax)
    map """

    # -- smooth the images
    print("median filtering... ")
    t0      = time.time()
    imgsm   = mf(bgrn, (1, wid, wid))
    print("  {0}s".format(np.round(time.time() - t0, 2)))
    imgusm  = uf(bgrn, (0, wid, wid))
    img2usm = uf(bgrn**2, (0, wid, wid))

    # -- get the variance image
    var = img2usm - imgusm**2

    # -- get the pseudo NDVI
    pndvi   = bgrn[3] - bgrn[2]

    # -- apply cuts
    return (imgsm[0] - imgsm[1] > 0.09) & (var[3] < 0.005) & (pndvi > 0.0)


