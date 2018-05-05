#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import gdal
import time
import numpy as np
from gdalconst import *


class PhScan():
    """
    Simple class holding a Precision Hawk scan.
    """

    def __init__(self, fname):

        # -- set the filename
        self.fname = fname

        # -- open the TIF file
        print("reading {0}...".format(self.fname))
        self.rast = gdal.Open(self.fname, GA_ReadOnly)

        # -- extract data to array
        print("extracting to array... "), 
        t0       = time.time()
        self.img = self.rast.ReadAsArray()
        print("(extracted in {0}s)".format(time.time() - t0))

        # -- rescale to 0 to 1
        print("rescaling...")
        self.imgs = self.img / float(self.img.max())

        # -- renormalize by hand
        print("WARNING: NORMALIZATION FACTORS SET BY HAND")
#         self.fac    = np.array([1.260825e-02, 9.713071e-03, 1.103623e-02, 
#                            1.224380e-02])
        self.fac    = np.ones(4)
        self.norm   = self.fac / self.fac.max()
        self.imnorm = self.imgs.transpose(1, 2, 0) * self.norm

        # -- set rgb
        self.rgb = self.imnorm[..., :3][..., ::-1]

        # -- calculate NDVI
        sub       = (self.imnorm[:, :, 3] - self.imnorm[:, :, 2])
        add       = (self.imnorm[:, :, 3] + self.imnorm[:, :, 2])
        self.ndvi = sub / (add + (add == 0))

        return
