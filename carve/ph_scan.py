#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import gdal
import time
import numpy as np
from gdalconst import *
from ph_xml import *
from utils import *


class PhScan():
    """
    Simple class holding a Precision Hawk scan.
    """

    def __init__(self, fname):

        # -- set the filename
        self.fname = fname

        # -- open the TIF file
        print("reading {0}... ".format(self.fname)), 
        t00       = time.time()
        self.rast = gdal.Open(self.fname, GA_ReadOnly)
        print("{0}s".format(np.round(time.time() - t00, 2)))

        # -- extract data to array
        print("extracting to array... "), 
        t0        = time.time()
        self.img  = self.rast.ReadAsArray()
        self.nwav = self.img.shape[0]
        self.nrow = self.img.shape[1]
        self.ncol = self.img.shape[2]
        print("{0}s".format(np.round(time.time() - t0, 2)))

        # -- apply calibration
        # -- L = Gain * DN * (abscalfactor/effective bandwidth) + Offset 
        print("parsing XML file and applying calibration... "),
        t0                  = time.time()
        self.xml            = PhXml(self.fname)
        self.abs_cal_factor = np.array(self.xml.abscalfactor)
        self.effective_bandwidth = np.array(self.xml.effectivebandwidth)
        self.rad_cal = self.img * \
            (self.abs_cal_factor / self.effective_bandwidth) \
            [:, np.newaxis, np.newaxis]
        print("{0}s".format(np.round(time.time() - t0, 2)))

        # -- rescale to 0 to 1
        print("rescaling... "),
        t0 = time.time()
        self.imgs = self.img / float(self.img.max())
        print("{0}s".format(np.round(time.time() - t0, 2)))

        # -- renormalize by hand
        print("normalizing color channels... "),
        t0          = time.time()
        lum         = self.rad_cal[:3].sum(0).astype(float)
        self.norm   = np.vstack((self.rad_cal[:3] / (lum + (lum == 0)), 
                                 [self.rad_cal[3] / self.rad_cal[3].max()]))
        print("{0}s".format(np.round(time.time() - t0, 2)))

        # -- set rgb
        print("creating RGB... "),
        t0         = time.time()
        self.rgb   = self.rad_cal[:3].transpose(1, 2, 0)[..., ::-1].copy()
        self.rgb  /= self.rgb.max()
        self.grayw = grayworld(self.rgb)
        print("{0}s".format(np.round(time.time() - t0, 2)))

        # -- calculate NDVI
        print("calculating NDVI... "),
        t0        = time.time()
        sub       = (self.rad_cal[3] - self.rad_cal[2])
        add       = (self.rad_cal[3] + self.rad_cal[2])
        self.ndvi = sub / (add + (add == 0))
        print("{0}s".format(np.round(time.time() - t0, 2)))

        # -- print total read time
        print("total read time: {0}s".format(np.round(time.time() - t00, 2)))
        return
