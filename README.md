# neoSeg

## Table of Contents

- [Introduction](#introduction)
- [Requirements](#requirements)
- [Run](#run)
- [Publications](#publications)

## Introduction

This repository contains the work during the PhD of Carlos Tor-Díez, titled "Automatic segmentation of the cortical surface in neonatal brain MRI". It includes two main contributions:

- **patchBasedSegmentation.py**, where several methods of label fusion (the final step of the multi-atlas segmentation approaches) are performed, including IMAPA [1].
- **topologicalCorrection.py**, where a topological correction for segmentation is presented, which consists in a multi-scale, multi-label topological-preserving deformation [2].

## Requirements

All scripts were coded in `python 2.7`, but we are working to be compatible to `python 3.7`.

<details>
<summary><b>Python packages</b></summary>

- argparse
- nibabel
- numpy
- scipy
- time
- itertools
- multiprocessing
- numba
- math
- random
- matplotlib
- scikit-image (skimage)
- scikit-fmm (skfmm)
</details>

The file called `requirements.txt` helps to install all the python libraries.

- Using pip:
```
pip install -r requirements.txt
```

- Using anaconda:
```
conda install --file requirements.txt
```

## Run

### patchBasedSegmentation.py

Example of IMAPA application using an atlas set of two pairs of images using two iterations (`alpha = 0` and `alpha = 0.25`) using 4 threads in parallel:

```
python neoSeg/patchBasedSegmentation.py  -i  brain.nii.gz -a  atlas1_registered_HM.nii.gz  atlas2_registered_HM.nii.gz -l  label1_propagated.nii.gz  label2_propagated.nii.gz  -mask mask.nii.gz  -m IMAPA  -hss 3  -hps 1  -k 15  -alphas 0 0.25  -t 4
```

**i**: input anatomical image

**a**: anatomical atlas images in the input space

**l**: label atlas images in the input space

**mask**: binary image for input

**m**: segmentation method chosen (LP, S_opt, I_opt, IS_opt or IMAPA)

**hss**: half search window size

**hps**: half patch size

**k**: k-Nearest Neighbors (kNN)

**alphas**: alphas parameter for IS_opt and IMAPA methods

**t**: Number of threads (0 for the maximum number of cores available)

> Note: We recommend to previously register the intensity image from the atlas set to the input image, apply a histogram matching algorithm and propagate the transformations to the label maps.

### topologicalCorrection.py

Example of topological correction using two segmentation maps (White Matter and cortical Gray Matter) as segmentation of reference and an atlas prior of the brainstem in order to apply a topological relaxation. Most relevant defaults parameters are to add the background as an extra label, start the correction with omega = 2, apply the relaxation step in omega = 1, stop the correction in omega = 0 and consider a connectivity 6-26 (6:WM and GM, 26:background).

```
python neoSeg/topologicalCorrection.py  -sref  neoSeg/examples/31_wm.nii.gz  neoSeg/examples/31_ribbon_cortex.nii.gz -rp neoSeg/31_brainstem_drawem.nii.gz -opath neoSeg/results  -spath neoSeg/topology/intermediate
```

**sref**: input segmentation maps to be corrected (multiple entries are accepted)

**rp**: binary image providing the spatial prior where the topological relaxation will be applied

**opath**: Output path

**spath**: Step path


> Note: A set of files for a demonstration is available in the repository 'github.com/rousseau/neoSeg/examples'. In order to check obtained results, they are available in 'github.com/rousseau/neoSeg/results'.

## Publications

- [1] C. Tor-Díez, N. Passat, I. Bloch, S. Faisan, N. Bednarek and F. Rousseau, “An iterative multi-atlas patch-based approach for cortex segmentation from neonatal MRI,” Computerized Medical Imaging and Graphics, 70:73–82, 2018, hal-01761063.

- [2] C. Tor-Díez, S. Faisan, L. Mazo, N. Bednarek, Hélène Meunier, I. Bloch, N. Passat and F. Rousseau, “Multilabel, multiscale topological transformation for cerebral MRI segmentation post-processing,” In 14th International Symposium on Mathematical Morphology (ISMM 2019), pp. 471–482, 2019, hal-01982972.
