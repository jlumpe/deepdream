# imports and basic notebook setup
import numpy as np
import scipy.ndimage as nd
from IPython.display import clear_output
from google.protobuf import text_format
import os
import caffe
import image




# Loads a net from a caffe model file
# I don't really know how these work
def load_net(paramfile, structfile = None):

	# Default value for structfile
	if structfile is None:
		structfile = os.path.dirname(os.path.realpath(paramfile)) + '/deploy.prototxt'

	# The rest is google's stuff

	# Patching model to be able to compute gradients.
	# Note that you can also manually add "force_backward: true" line to "deploy.prototxt".
	model = caffe.io.caffe_pb2.NetParameter()
	text_format.Merge(open(structfile).read(), model)
	model.force_backward = True
	open('tmp.prototxt', 'w').write(str(model))

	net = caffe.Classifier('tmp.prototxt', paramfile,
						   mean = np.float32([104.0, 116.0, 122.0]), # ImageNet mean, training set dependent
						   channel_swap = (2,1,0)) # the reference model has channels in BGR order instead of RGB

	return net





# a couple of utility functions for converting to and from Caffe's input image layout
def preprocess(net, img):
	return np.float32(np.rollaxis(img, 2)[::-1]) - net.transformer.mean['data']
def deprocess(net, img):
	return np.dstack((img + net.transformer.mean['data'])[::-1])




def make_step(net, step_size=1.5, end='inception_4c/output', jitter=32, clip=True):
	'''Basic gradient ascent step.'''

	src = net.blobs['data'] # input image is stored in Net's 'data' blob
	dst = net.blobs[end]

	ox, oy = np.random.randint(-jitter, jitter+1, 2)
	src.data[0] = np.roll(np.roll(src.data[0], ox, -1), oy, -2) # apply jitter shift
			
	net.forward(end=end)
	dst.diff[:] = dst.data  # specify the optimization objective
	net.backward(start=end)
	g = src.diff[0]
	# apply normalized ascent step to the input image
	src.data[:] += step_size/np.abs(g).mean() * g

	src.data[0] = np.roll(np.roll(src.data[0], -ox, -1), -oy, -2) # unshift image
			
	if clip:
		bias = net.transformer.mean['data']
		src.data[:] = np.clip(src.data, -bias, 255-bias)




def deepdream(net, base_img, iter_n=10, octave_n=4, octave_scale=1.4, end='inception_4c/output', clip=True, show=True, **step_params):
	# prepare base images for all octaves
	octaves = [preprocess(net, base_img)]
	for i in xrange(octave_n-1):
		octaves.append(nd.zoom(octaves[-1], (1, 1.0/octave_scale,1.0/octave_scale), order=1))
	
	src = net.blobs['data']
	detail = np.zeros_like(octaves[-1]) # allocate image for network-produced details
	for octave, octave_base in enumerate(octaves[::-1]):
		h, w = octave_base.shape[-2:]
		if octave > 0:
			# upscale details from the previous octave
			h1, w1 = detail.shape[-2:]
			detail = nd.zoom(detail, (1, 1.0*h/h1,1.0*w/w1), order=1)

		src.reshape(1,3,h,w) # resize the network's input image size
		src.data[0] = octave_base+detail
		for i in xrange(iter_n):
			make_step(net, end=end, clip=clip, **step_params)
			
			# visualization
			if show:
				vis = deprocess(net, src.data[0])
				if not clip: # adjust image contrast if clipping is disabled
					vis = vis*(255.0/np.percentile(vis, 99.98))
				image.show(vis)
				print 'Octave %i/%i' % (octave+1, octave_n), 'Iteration %i/%i' % (i+1, iter_n), 'Layer: %s' % (end), vis.shape
				clear_output(wait=True)
			
		# extract details produced on the current octave
		detail = src.data[0]-octave_base
	# returning the resulting image
	return deprocess(net, src.data[0])
