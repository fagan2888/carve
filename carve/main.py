#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This script will do the following:
#   1. Load a Precision Hawk geotif
#   2. Calculate the vegetative health (NDVI estimate)
#   3. Check if a phragmites map exists (generate if it does not)
#   4. Check if a cluster map exists (generate if it does not)
#   5. Pack BGRN, NDVI, PHRAGMAP, and CLUSTERS into a geotif and write
#
# Required directories are:
#   ../data/Delivery/ (contains folder with Precision Hawk data)
#   ../output/ (a destination for the phragmites and cluster outputs

import os
import glob
import utils
import numpy as np
from ph_scan import PhScan
from phrag_map import phrag_map
from utils import cluster_ph, write_tif


if __name__ == "__main__":

    # -- set a filename to process the full data set, loop through flist 
    #    instead of flist[:1] below
    flist = utils.get_tif_list() # get the full TIF list

    for fname in flist[:1]:

        # -- load the scan
        scan = PhScan(fname)


        # -- check if phragmites estimate exists for this scan (or generate 
        #    it if it does not)
        #    (Note: bgrn is defined to be (B/L,G/L,R/L,N/max(N)) where 
        #     L = B+G+R)
        pfile = os.path.join("..", "output", "phrag_maps", 
                             *fname.split(os.sep)[2:]) \
                             .replace(".TIF", "_phrag.npy")
        pdir  = os.path.split(pfile)[0] # path to phragmites map results

        if not os.path.exists(pdir):
            os.makedirs(pdir)

        if os.path.isfile(pfile):
            print("Reading phragmites map...")
            phrag = np.load(pfile)
        else:
            print("Generating phragmites estimate...")
            bgrn  = scan.norm
            phrag = phrag_map(bgrn)

            print("Writing phragmites map to {0}...".format(pfile))
            np.save(pfile, phrag)


        # -- check if cluster results exist for this scan (or generate 
        #    it if it does not)
        cfile = os.path.join("..", "output", "cluster_maps", 
                             *fname.split(os.sep)[2:]) \
                             .replace(".TIF", "_cluster_n05.npy")
        cdir  = os.path.split(cfile)[0] # path to phragmites map results

        if not os.path.exists(cdir):
            os.makedirs(cdir)

        if os.path.isfile(cfile):
            print("Reading cluster map...")
            clust = np.load(cfile)
        else:
            print("Generating the clusters...")
            clust = cluster_ph(scan, n_clusters=5, n_jobs=10, frac=0.05)

            print("Writing cluster map to {0}...".format(cfile))
            np.save(cfile, clust)


        # -- write to GeoTIFF if it does not exist
        ffile = os.path.join("..", "output", "processed_maps", 
                             *fname.split(os.sep)[2:]) \
                             .replace(".TIF", "_proc.npy")
        fdir  = os.path.split(ffile)[0] # path to phragmites map results
        
        if not os.path.exists(fdir):
            os.makedirs(fdir)

        if not os.path.isfile(ffile):
            print("Writing processed maps to GeoTIFF {0}...".format(ffile))

            write_tif(ffile, scan, phrag, clust)
