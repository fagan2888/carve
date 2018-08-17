#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import glob
import gdal
import osr
import numpy as np
from sklearn.cluster import KMeans
from gen_cmap import *
from ph_xml import *

def get_tif_list():
    # -- get the full list of TIFs
    cpath = os.path.join("..", "data", "Delivery", "*", "*P*MUL", "*.TIF")
    clist = np.array(sorted(glob.glob(cpath)))

    return clist



def grayworld(rgb):
    """ Convert RGB (range 0 to 1) to gray world """

    ind  = rgb.sum(2) > 0
    fac  = np.array([i[ind].mean() for i in rgb.transpose(2, 0, 1)])
    fac /= fac.max()

    return (rgb / fac).clip(0, 1)



def search_latlon(lat, lon):
    """ Get the TIF list for an input lat, lon """

    # -- get the TIF list and read the XMLs
    flist = get_tif_list()
    xmls  = [PhXml(i) for i in flist]

    # -- create array of UL and LR lats and lons
    lats = np.array([[i.ul_latlon[0], i.lr_latlon[0]] for i in xmls])
    lons = np.array([[i.ul_latlon[1], i.lr_latlon[1]] for i in xmls])

    # -- index on input lat, lon
    latind = (lat >= lats[:, 1]) & (lat < lats[:, 0])
    lonind = (lon >= lons[:, 0]) & (lon < lons[:, 1])

    return flist[latind & lonind]



def latlon_to_rowcol(lat, lon, ul_latlon, lr_latlon, nrow, ncol):
    """ Convert input lat/lon to row/col given corners. """

    # -- latitude (row)
    ull  = ul_latlon[0]
    lrl  = lr_latlon[0]
    irow = int(np.round((lat - ull) / (lrl - ull) * nrow))

    # -- longitude (col)
    ull  = ul_latlon[1]
    lrl  = lr_latlon[1]
    icol = int(np.round((lon - ull) / (lrl - ull) * ncol))

    return irow, icol


def cluster_ph(scan, n_clusters=5, n_jobs=10, frac=0.05):
    """ Cluster a Precision Hawk scan. """

    # -- pull off the data
    data = scan.rad_cal.transpose(1, 2, 0)

    # -- sub-select based on on NDVI
    ind = (scan.ndvi >= 0.3) & (data.max(2) > 0)
    sub = data[ind]
    
    # -- cluster on a percentage of the data
    np.random.seed(98123)
    km   = KMeans(n_clusters=n_clusters, n_jobs=10, random_state=3025784)
    sig  = sub.std(1, keepdims=True)
    norm = (sub - sub.mean(1, keepdims=True)) / (sig + (sig == 0))
    indc = np.random.rand(norm.shape[0]).argsort()[:int(frac * norm.shape[0])]
    km.fit(norm[indc])

    # -- create label image (-1 and +1 are b/c km.labels_.min() = 0)
    labs      = np.zeros(data.shape[:2], dtype=int) - 1
    labs[ind] = km.predict(norm) + 1

    return labs



def write_tif(fname, scan, phrag, clust):
    """ Write Precision Hawk data plus vegetative health estimate plus 
    phragmites location estimate plus clustering results to file. """

    # -- stack the data into a single array
    print("Stacking data into an array...")
    odata  = np.vstack((scan.rad_cal, scan.ndvi[None], phrag[None], 
                        clust[None]))
    nband  = odata.shape[0]
    nrow   = odata.shape[1]
    ncol   = odata.shape[2]

    # -- open the file writer driver and create file
    print("Opening the file writer...")
    driver = gdal.GetDriverByName("GTiff")
    orast  = driver.Create(fname, ncol, nrow, nband, gdal.GDT_Float32)
    dum    = orast.SetGeoTransform(scan.rast.GetGeoTransform())

    # -- push data into file
    print("Sending data to file...")
    for iband in range(nband):
        oband = orast.GetRasterBand(iband + 1)
        oband.WriteArray(odata[iband])
        oband.FlushCache()

    # -- reset projection and close
    print("Resetting projection and closing...")
    prj   = scan.rast.GetProjection()
    srs   = osr.SpatialReference(wkt=prj)
    dum   = orast.SetProjection(srs.ExportToWkt())
    orast = None

    return
