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


# Creates image of random noise
def noise(width, height=None):
	if height is None:
		height = width
	return np.random.rand(height, width, 3) * 255


# Creates some perlin noise
def perlin(octaves=8, roughness=1, zoom=1):

	# How much to scale displacement by each octave
	base = 2.0 / roughness

	# Init with random 2x2 image
	size = 2
	scale = 1.0
	img = np.random.rand(2, 2, 3)

	# more octaves
	for i in range(1, octaves):
		scale = scale / base
		size = size * 2
		img = nd.zoom(img, (2, 2, 1), order=1)
		img = img + np.random.rand(size, size, 3) * scale

	# Rescale image to 0-255 range
	img = (img - img.min()) * (255 / (img.max() - img.min()))

	# Perform final zoom if needed
	if zoom > 1:
		return nd.zoom(img, (zoom, zoom, 1), order=2)
	else:
		return img