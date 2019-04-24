from numpy import *
from numpy import random
from scipy.ndimage import filters
import cal_rssi
from scipy.misc import imsave

im = zeros((500,500))
im[100:400,100:400] = 128
im[200:300,200:300] = 255

im = im + 30*random.standard_normal((500,500))

imsave('synth_ori.pdf', im)

U, T = cal_rssi.de_noise(im, im, 0.07)

G = filters.gaussian_filter(im, 10)

imsave('synth_rof.pdf', U)
imsave('synth_gaussian.pdf', G)