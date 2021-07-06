"""Dilation, erosion, opening, closing operations on binary nifti files."""
# Based on ://gist.github.com/ofgulban/21f9b257de849c546f34863aa26f3dd3
# James Cole 06/07/2021

import os
import sys
import numpy as np
from scipy.ndimage import morphology
from nibabel import load, save, Nifti1Image

# Load data
file = sys.argv[1]
print(file)
nii = load(file)
#nii = load('/home/jcole/Desktop/SynthSR/t1_1mm_bet_mask.nii.gz')
basename = nii.get_filename().split(os.extsep, 1)[0]
dirname = os.path.dirname(nii.get_filename())
data = np.asarray(nii.dataobj)

# Perform dilaions
dilations = int(sys.argv[2])
data = morphology.binary_dilation(data, iterations=dilations)

# Save as nifti
out = Nifti1Image(data, header=nii.header, affine=nii.affine)
save(out, basename + "_dilated.nii.gz")

print('Finished.')
