import os
import cv2
import glob
from ph_scan import *
from flask import Flask
from flask import request, render_template, jsonify, make_response, url_for, redirect, abort
import matplotlib.colors as colors


# create app
app = Flask(__name__)

PATH_TO_IMAGES = '/Users/ishachaturvedi/Downloads/Delivery'

imgpath = lambda f: os.path.join(PATH_TO_IMAGES, f)

'''Helper/Utility Functions'''

def image_response(img):
	'''Converts image numpy array to a flask response.'''
	retval, buffer = cv2.imencode('.png', img)
	return make_response(buffer.tobytes())




'''Flask Routes'''


@app.route('/')
def index():
	'''The homepage or whatever. Render html'''
	imgs = glob.glob(imgpath('*/*_MUL/*.TIF'))
	imgs = [
		os.path.relpath(path, PATH_TO_IMAGES)
		for path in imgs
	]
	return render_template('list.j2', title='Image List', imgs=imgs)



@app.route('/view/<path:filename>')
def view(filename):
	'''Page that draws an image'''

	imd_file = glob.glob(os.path.join(PATH_TO_IMAGES, os.path.dirname(filename), '*.IMD'))[0]

	cstr = [line for line in open(imd_file, "r")]

	ullat = [float(line.split("=")[1][:-2]) for line in cstr if "ULLat" in line][0]
	ullon = [float(line.split("=")[1][:-2]) for line in cstr if "ULLon" in line][0]
	lrlat = [float(line.split("=")[1][:-2]) for line in cstr if "LRLat" in line][0]
	lrlon = [float(line.split("=")[1][:-2]) for line in cstr if "LRLon" in line][0]
	coords = [[ullat, lrlat], [ullat, lrlon]]

	fac = 4

	# -- read the scan
	scan = PhScan(imgpath(filename))
	rgb  = (3.0 * (scan.rgb).mean(-1)).clip(0, 1)[::fac, ::fac]
	ndvi = scan.ndvi[::fac, ::fac]

	
	# jpg_file = glob.glob(os.path.join(PATH_TO_IMAGES, os.path.dirname(filename), '*.JPG'))[0]


	return render_template('image.j2', title='View {}'.format(filename), filename=filename, coords=coords, 
							ndvi=ndvi.tolist(), ndvishp=ndvi.shape)



norm = colors.Normalize()


@app.route('/image/<path:filename>')
def image(filename):
	'''Used to render an image. Can do some processing here.'''
	img = cv2.imread(imgpath(filename))
	# img = img[::-1,:,::-1] # flip upsidedown and reverse color channels
	img = norm(img) * 255
	return image_response(img)







if __name__ == '__main__':
	app.run(debug=True, port=5000) # , threaded=True