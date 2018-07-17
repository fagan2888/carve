import os
import cv2
import glob
from ph_scan import *
from flask import Flask
from flask import request, render_template, jsonify, make_response, url_for, redirect, abort, send_file
import matplotlib.colors as colors

from osgeo import gdal, osr

# create app
app = Flask(__name__)

#customize path according to where ur images are stored
PATH_TO_IMAGES = '/Users/ishachaturvedi/Downloads/Delivery'
EXPORT_PATH = os.path.abspath('static/export')

imgpath = lambda f: os.path.join(PATH_TO_IMAGES, f)
exportpath = lambda f: os.path.join(EXPORT_PATH, f.replace('/', ','))

'''Helper/Utility Functions'''

def image_response(img):
	'''Converts image numpy array to a flask response.'''
	retval, buffer = cv2.imencode('.png', img)
	return make_response(buffer.tobytes())


def get_bounds(filename):
	imd_file = glob.glob(os.path.join(PATH_TO_IMAGES, os.path.dirname(filename), '*.IMD'))[0]

	cstr = [line for line in open(imd_file, "r")]

	ullat = [float(line.split("=")[1][:-2]) for line in cstr if "ULLat" in line][0]
	ullon = [float(line.split("=")[1][:-2]) for line in cstr if "ULLon" in line][0]
	lrlat = [float(line.split("=")[1][:-2]) for line in cstr if "LRLat" in line][0]
	lrlon = [float(line.split("=")[1][:-2]) for line in cstr if "LRLon" in line][0]
	return [[ullat, lrlat], [ullon, lrlon]]


def get_ndvi(filename, fac=4):
	scan = PhScan(imgpath(filename))
	rgb  = (3.0 * (scan.rgb).mean(-1)).clip(0, 1)[::fac, ::fac]
	return scan.ndvi[::fac, ::fac]


'''Init'''



# Load All Images
imgs = glob.glob(imgpath('*/*_MUL/*.TIF'))
imgs = [
	os.path.relpath(filename, PATH_TO_IMAGES)
	for filename in imgs
]

# get top right and bottom left corners
bounds = {
	filename: get_bounds(filename)
	for filename in imgs
}




'''Flask Routes'''


@app.route('/')
def index():
	'''The homepage or whatever. Render html'''
	return render_template('list.j2', title='Image List', imgs=imgs)



@app.route('/view/<path:filename>')
def view(filename):
	'''Page that draws an image'''
	coords = bounds[filename]
	ndvi = get_ndvi(filename)
	
	# jpg_file = glob.glob(os.path.join(PATH_TO_IMAGES, os.path.dirname(filename), '*.JPG'))[0]
	return render_template('image.j2', title='View {}'.format(filename), filename=filename, coords=coords, 
							ndvi=ndvi.tolist(), ndvishp=ndvi.shape)


def between(a, x, b):
	return a <= x <= b or b <= x <= a

@app.route('/search/<latlon>')
def search(latlon): #lat, lon, i=0
	'''Page that draws an image'''
	lat, lon = map(float, latlon.split(','))

	i = int(request.args.get('i', 0))

	filenames = [
		path for path, ((ullat, lrlat), (ullon, lrlon)) in bounds.items()
		if between(lrlat, lat, ullat) and between(lrlon, lon, ullon)
	]

	if i >= len(filenames):
		return abort(404)

	print(filenames)
	filename = filenames[i]

	coords = bounds[filename]
	ndvi = get_ndvi(filename)
	
	# jpg_file = glob.glob(os.path.join(PATH_TO_IMAGES, os.path.dirname(filename), '*.JPG'))[0]
	return render_template('image.j2', title='View {}'.format(filename), filename=filename, coords=coords, 
							ndvi=ndvi.tolist(), ndvishp=ndvi.shape, filenames=enumerate(filenames))









norm = colors.Normalize()


# @app.route('/image/<path:filename>')
# def image(filename):
# 	'''Used to render an image. Can do some processing here.'''
# 	img = cv2.imread(imgpath(filename))
# 	img = norm(img) * 255
# 	return image_response(img)

@app.route('/image/<path:filename>')
def image(filename):
	'''Used to render an image. Can do some processing here.'''
	jpg_file = glob.glob(os.path.join(PATH_TO_IMAGES, os.path.dirname(filename), '*.JPG'))[0]
	return send_file(open(jpg_file, 'rb'), 
		mimetype='image/jpeg')



@app.route('/export/<path:filename>')
def export(filename):
	'''Used to generate geotiff.'''
	export_filename = exportpath(filename) # 

	# if not os.path.isfile(export_filename): # generate file
	scan = PhScan(imgpath(filename))

	# create raster band array
	# print(scan.img[:3][::-1].shape, scan.img[3:].shape, scan.ndvi[None,...].shape)
	# scan.rgb.transpose(2, 0, 1)*255
	img = np.concatenate([scan._img, scan.ndvi[None,...]], axis=0) # [:3][::-1], scan.img[3:]

	# color_interp = [gdal.GCI_BlueBand, gdal.GCI_GreenBand, gdal.GCI_RedBand, gdal.GCI_GrayIndex, None]
	nbands, nx, ny = img.shape
	(xmin, xmax), (ymin, ymax) = bounds[filename]

	xres = (xmax - xmin) / float(nx)
	yres = (ymax - ymin) / float(ny)
	geotransform = (xmin, xres, 0, ymax, 0, -yres)

	# create the 3-band raster file
	dst_ds = gdal.GetDriverByName('GTiff').Create(export_filename, ny, nx, nbands, gdal.GDT_Byte, options=['PHOTOMETRIC=RGB'])

	if dst_ds is not None:
		dst_ds.SetGeoTransform(geotransform)    # specify coords
		srs = osr.SpatialReference()            # establish encoding
		srs.ImportFromEPSG(3857)                # WGS84 lat/long
		dst_ds.SetProjection(srs.ExportToWkt()) # export coords to file

		# write each band to the raster
		for i in range(nbands):
			dst_ds.GetRasterBand(i+1).WriteArray(img[i,:,:])  

		# write to disk 
		dst_ds.FlushCache()                     
		dst_ds = None
	else:
		print('Error creating geotiff file.')

	# return image object
	# return jsonify(dict(hi='Hi!'))
	return send_file(open(export_filename, 'rb'), 
		attachment_filename=os.path.basename(export_filename),
		mimetype='image/tif')






if __name__ == '__main__':
	app.run(debug=True, port=5000) # , threaded=True