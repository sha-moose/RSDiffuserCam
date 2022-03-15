import sys
sys.path.append('helper/')
import cupy as np
import cupy.fft as fft
import matplotlib.pyplot as plt
import numpy as numpy
import cv2
from PIL import Image
from fista_spectral_cupy import *
from fista_2d_cupy import *

class image():
    def __init__(self, psfname, imgname):
        self.psfname = psfname
        self.imgname = imgname
        self.resize_factor = 1/8
        self.iters = 500
        
    def loaddata(self, psfname, imgname):
        psf = np.array(Image.open(psfname), dtype='float32')[:,:,1]
        data = np.array(Image.open(imgname), dtype='float32')[:,:,:-1]
    
        def resize(img):
            for i in range(int(-np.log2(self.resize_factor))):
                img = 0.25 * (img[::2,::2] + img[1::2,::2] + img[::2,1::2] + img[1::2,1::2])
            return img
    
        bg = np.mean(psf[5:15,5:15], axis=(0, 1))
        psf -= bg
        data -= bg
        psf = resize(psf)
        data = resize(data)
        psf /= np.linalg.norm(psf, axis=(0,1))
        data /= np.max(data)
        return psf, data
    
    def set_psfname(self, psfname):
        self.psfname = psfname
        
    def set_imgname(self, imgname):
        self.imgname = imgname
    
    def set_colour(self, boolean):
       self.is_colour = boolean
    
    def set_resize_factor(self, factor):
        self.resize_factor = factor
        
        
class image_2D(image):
    def __init__(self, psfname, imgname):
        super().__init__(psfname, imgname)
        self.resize_factor = 1/2
        self.prox_method = 'tv'
        self.tv_lambda = 3e-4 # change for best results
        self.tv_lambdaw = 1

    def set_params(self, fista):
        fista.iters = self.iters
        fista.prox_method = self.prox_method
        fista.tv_lambda = self.tv_lambda
        fista.tv_lambdaw = self.tv_lambdaw
    
    # loads in image from disk and runs 2D reconstruction
    def run(self):
        self.psf, self.img = self.loaddata(self.psfname, self.imgname)
        self.mask = np.ones(self.psf.shape)
        
        self.fista = fista_2d_cupy(self.psf, self.mask)
        self.set_params(self.fista)
        self.fista.run(self.img)
        self.out_img = self.fista.out_img
        self.fc_img = numpy.max(self.out_img, axis=-1) / numpy.max(self.out_img)
    
    def save(self, filepath):
        # TODO
        return


# A rolling shutter image
class image_RS(image):
    def __init__(self, psfname, imgname):
        super().__init__(psfname, imgname)
        self.num_frames = 30
        self.prox_method = 'tv' # options: non-neg, native, tv
        
        # Define soft thresholding constants
        self.tau = 5e-6             # Native sparsity tuning parameter
        self.tv_lambda = 3e-5       # Spatial TV tuning parameter
        self.tv_lambdaw = 50        # Temporal TV tuning parameter
    
        
    def make_rolling_mask(self, shape, num_frames):
        mask = np.zeros((shape[0], shape[1], num_frames))
        chunk = shape[0] / num_frames
        for i in range(num_frames):
            mask[i * chunk:(i + 1) * chunk, :, i] = 1
        return mask;
    
    def set_params(self, fista):
        fista.iters = self.iters
        fista.prox_method = self.prox_method
        fista.tau = self.tau
        fista.tv_lambda = self.tv_lambda
        fista.tv_lambdaw = self.tv_lambdaw
    
    # loads in image from disk and runs 3D reconstruction
    def run(self):
        self.psf, self.img = self.loaddata(self.psfname, self.imgname)
        self.mask = self.make_rolling_mask(self.img.shape[:2], self.num_frames)
        
        self.fista = fista_spectral_numpy(self.psf, self.mask)

        self.set_params(self.fista)
        self.fista.run(self.img)
        self.out_img = self.fista.out_img
        self.fc_img = self.out_img / numpy.max(self.out_img)
    
    # outputs a 1 second video containing all of the frames
    def save(self, filepath):
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        shape = (self.out_img.shape[1], self.out_img.shape[0])
        out = cv2.VideoWriter(filepath, fourcc, self.num_frames, self.shape, True)
        for i in range(self.num_frames):
            frames = (np.clip(np.asnumpy(self.out_img[:,:,i,:]) / np.asnumpy(np.max(self.out_img, axis=(0,1,2))), 0, 1) * 255).astype('uint8')
            out.write(frames)
        out.release()
