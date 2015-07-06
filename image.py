# imports and basic notebook setup
from cStringIO import StringIO
import numpy as np
import PIL.Image
from IPython.display import clear_output, Image, display



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