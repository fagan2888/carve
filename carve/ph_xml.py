#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import glob

class PhXml():
    """ A class holding information from an TIF's associated XML file. """

    def __init__(self, fname):

        # -- get the path to the data
        fpath = os.path.split(fname)[0]

        # -- read the XML file
        self.fname   = fname
        self.xmlname = sorted(glob.glob(os.path.join(fpath, "*.XML")))[0]
        self._xmltxt = [line for line in open(self.xmlname, "r")]

        # -- first get global params
        self.abscalfactor = []
        self.effectivebandwidth = []
        self.tdilevel = []

        for line in self._xmltxt:

            if "ABSCALFACTOR" in line:
                self.abscalfactor.append(self.parse_float(line))

            if "EFFECTIVEBANDWIDTH" in line:
                self.effectivebandwidth.append(self.parse_float(line))

            if "TDILEVEL" in line:
                self.tdilevel.append(self.parse_int(line))

        # -- now get tile sizes and boundaries
        self.ul_latlon = [0, 0]
        self.lr_latlon = [0, 0]

        rflag = False

        for line in self._xmltxt:

            if os.path.split(fname)[1] in line:
                rflag = True

            if ("ULLAT" in line) & rflag:
                self.ul_latlon[0] = self.parse_float(line)

            if ("ULLON" in line) & rflag:
                self.ul_latlon[1] = self.parse_float(line)

            if ("LRLAT" in line) & rflag:
                self.lr_latlon[0] = self.parse_float(line)

            if ("LRLON" in line) & rflag:
                self.lr_latlon[1] = self.parse_float(line)

            if ("/TILE" in line) & rflag:
                rflag = False

        return


    def parse_int(self, rec):
        """ Pull off integer value from IMD line. """

        return int(rec.split(">")[1].split("<")[0])


    def parse_float(self, rec):
        """ Pull off float value from IMD line. """

        return float(rec.split(">")[1].split("<")[0])
