# imports
from cStringIO import StringIO
import numpy as np
import PIL.Image
from IPython.display import clear_output, Image, display
import scipy.ndimage as nd
import scipy.misc as misc



# Guess this saves an array as an image file, then displays it?
def show(a, fmt='jpeg'):
	a = np.uint8(np.clip(a, 0, 255))
	f = StringIO()
	PIL.Image.fromarray(a).save(f, fmt)
	display(Image(data=f.getvalue()))


# Load an image into an array by file path
def load(path):
	return np.float32(PIL.Image.open(path))


# Save image from array
def save(a, path, fmt='jpeg'):
	PIL.Image.fromarray(np.uint8(a)).save(path, fmt)


# Resizes an image to a given resolution
def resize(img, interp='bicubic', **args):
	if 'scale' in args:
		return misc.imresize(img, float(args['scale']), interp)
	else:
		ratio = float(img.shape[1]) / img.shape[0]
		if 'width' in args:
			return misc.imresize(img, (int(args['width'] / ratio), int(args['width']), 3), interp)
		elif 'height' in args:
			return misc.imresize(img, (int(args['height']), int(args['height'] * ratio), 3), interp)
		else:
			raise ValueError('One of "scale", "width", "height" must be given')
