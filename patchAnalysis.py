#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""

  This software is governed by the CeCILL-B license under French law and
  abiding by the rules of distribution of free software.  You can  use,
  modify and/ or redistribute the software under the terms of the CeCILL-B
  license as circulated by CEA, CNRS and INRIA at the following URL
  "http://www.cecill.info".

  As a counterpart to the access to the source code and  rights to copy,
  modify and redistribute granted by the license, users are provided only
  with a limited warranty  and the software's author,  the holder of the
  economic rights,  and the successive licensors  have only  limited
  liability.

  In this respect, the user's attention is drawn to the risks associated
  with loading,  using,  modifying and/or developing or reproducing the
  software by the user in light of its specific status of free software,
  that may mean  that it is complicated to manipulate,  and  that  also
  therefore means  that it is reserved for developers  and  experienced
  professionals having in-depth computer knowledge. Users are therefore
  encouraged to load and test the software's suitability as regards their
  requirements in conditions enabling the security of their systems and/or
  data to be ensured and,  more generally, to use and operate it in the
  same conditions as regards security.

  The fact that you are presently reading this means that you have had
  knowledge of the CeCILL-B license and that you accept its terms.

  #####################################################################
  Example:
  python patchAnalysis.py -i ~/Data/ALBERT_makropoulos/T2/ALBERT_01.nii.gz
        -s ~/Data/ALBERT_makropoulos/gm-posteriors-v3/ALBERT_01.nii.gz
        -x 10 -y 76 -z 65
  #####################################################################
"""
import argparse
import nibabel
import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize as optimize
from numba import jit


def computeOptWeights(P,P_j,i):
    num_example=P_j.shape[1]
    w=np.zeros([num_example])
    Z=np.zeros(P_j.shape)
    b=np.ones([num_example])
    for j in range(num_example):
        Z[:,j]=P_j[:,j]-P
    C=np.dot(Z.transpose(1,0),Z)
    trace = np.trace(C)
    fmin = lambda x: np.linalg.norm(np.dot(C,x)-b)
    sol = optimize.minimize(fmin, np.zeros(num_example), method='L-BFGS-B', bounds=[(0.,1.) for x in xrange(num_example)])
    w = sol['x']
    weights=w/np.sum(w)
    return weights



def computeNLMWeights(P,P_j,i,h):
    num_example=P_j.shape[1]
    w=np.zeros([num_example])
    dist_j=np.array([np.sum((P-P_j[:,j])**2) for j in range(num_example)]) #distance between P and P_j
    w=np.exp(-(dist_j/h))
    weights=w/np.sum(w)
    return weights


@jit
def computeSigmaNoise(img):
    sigma2=np.float(0.0)
    xmax=img.shape[0]
    ymax=img.shape[1]
    zmax=img.shape[2]
    omega=np.float(xmax*ymax*zmax)

    for ii in range(0,xmax):
      for jj in range(0,ymax):
        for kk in range(0,zmax):

          if ii not in [0,xmax-1]:
              Nii=[ii-1,ii+1]
          elif ii==0:
              Nii=[ii+1]
          elif ii==xmax-1:
              Nii=[ii-1]

          if jj not in [0,ymax-1]:
              Njj=[jj-1,jj+1]
          elif jj==0:
              Njj=[jj+1]
          elif jj==ymax-1:
              Njj=[jj-1]

          if kk not in [0,zmax-1]:
              Nkk=[kk-1,kk+1]
          elif kk==0:
              Nkk=[kk+1]
          elif kk==zmax-1:
              Nkk=[kk-1]

          nN=np.float(len(Nii)+len(Njj)+len(Nkk))

          epsilon0 = np.float(0.0)
          for iii in Nii:
            for jjj in Njj:
              for kkk in Nkk:
                epsilon0+= img[iii,jjj,kkk]
          sigma2+=(nN/(nN+1)) * (img[ii,jj,kk] - (1/nN * epsilon0))**2
    return sigma2/omega


def extractPatches(data,i,hss,hps):
    xmin = i[0]-hss[0]
    if xmin < hps[0]:
        xmin = hps[0]
    ymin = i[1]-hss[1]
    if ymin < hps[1]:
        ymin = hps[1]
    zmin = i[2]-hss[2]
    if zmin < hps[2]:
        zmin = hps[2]
    xmax = i[0]+hss[0]
    if xmax> data.shape[0]-hps[0]:
        xmax = data.shape[0]-hps[0]
    ymax = i[1]+hss[1]
    if ymax> data.shape[1]-hps[1]:
        ymax = data.shape[1]-hps[1]
    zmax = i[2]+hss[2]
    if zmax> data.shape[2]-hps[2]:
        zmax = data.shape[2]-hps[2]

    count=0
    size_patch=(2*hps[0]+1)*(2*hps[1]+1)*(2*hps[2]+1)
    P_j=np.zeros([size_patch,(2*hss[0]+1)*(2*hss[1]+1)*(2*hss[2]+1)-1])
    for ii in range(xmin,xmax):
        for jj in range(ymin,ymax):
            for kk in range(zmin,zmax):
                if [ii,jj,kk]==i:
                    P=data[i[0]-hps[0]:i[0]+hps[0]+1,i[1]-hps[1]:i[1]+hps[1]+1,i[2]-hps[2]:i[2]+hps[2]+1].reshape([size_patch])
                else:
                    P_j[:,count]=data[ii-hps[0]:ii+hps[0]+1,jj-hps[1]:jj+hps[1]+1,kk-hps[2]:kk+hps[2]+1].reshape([size_patch])
                    count+=1

    return P,P_j




if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='patchAnalysis')

    parser.add_argument('-i', '--input', help='Input anatomical image (required)', type=str, required = True)
    parser.add_argument('-s', '--seg', help='Input segmentation image (probability map, required)', type=str, required = True)
    parser.add_argument('-x', '--x', help='x location (required)', type=int, required = True)
    parser.add_argument('-y', '--y', help='y location (required)', type=int, required = True)
    parser.add_argument('-z', '--z', help='z location (required)', type=int, required = True)
    parser.add_argument('-hss', '--hss', help='Half search area size (default)', type=int, default=3, required = False)
    parser.add_argument('-hps', '--hps', help='Half path size', type=int, default=2, required = False)


    args = parser.parse_args()

    ###--Print Input Information--###

    print 'Input anatomical image: ',args.input
    print 'Input segmentation image (probability map): ',args.seg
    print 'Location: (',str(args.x),',',str(args.y),',',str(args.z),')'
    print 'Half search area size: ',str(args.hss)
    print 'Half patch size: ',str(args.hps)


    ###--Load input data--###

    input=np.float32(nibabel.load(args.input).get_data())
    seg=np.float32(nibabel.load(args.seg).get_data())
    vx=[args.x,args.y,args.z]
    hss=[args.hss,args.hss,args.hss]
    hps=[args.hps,args.hps,args.hps]


    ###--Compute analysis--###

    #--Extract patches--#
    Pi,Pi_j=extractPatches(input,vx,hss,hps)
    Ps,Ps_j=extractPatches(seg,vx,hss,hps)

    #--Compute weights--#
    Ws_opt=computeOptWeights(Ps,Ps_j,vx)
    Wi_opt=computeOptWeights(Pi,Pi_j,vx)
    beta=1.0
    h=np.float(2.0 * beta * (computeSigmaNoise(input)) * np.float((2*hps[0]+1)*(2*hps[1]+1)*(2*hps[2]+1)) )
    W_nlm=computeNLMWeights(Pi,Pi_j,vx,h)

    #--Compute loss--#
    num_example=Pi_j.shape[1]
    Ps_i=np.zeros(Pi.shape)
    Ps_s=np.zeros(Pi.shape)
    Pi_i=np.zeros(Pi.shape)
    Pi_s=np.zeros(Pi.shape)
    Pnlm_i=np.zeros(Pi.shape)
    Pnlm_s=np.zeros(Pi.shape)
    for j in range(num_example):
        Ps_i+=Ws_opt[j]*Pi_j[:,j]
        Ps_s+=Ws_opt[j]*Ps_j[:,j]
        Pi_i+=Wi_opt[j]*Pi_j[:,j]
        Pi_s+=Wi_opt[j]*Ps_j[:,j]
        Pnlm_i+=W_nlm[j]*Pi_j[:,j]
        Pnlm_s+=W_nlm[j]*Ps_j[:,j]
    loss_Ps_i=np.linalg.norm(Ps_i-Pi)
    loss_Ps_s=np.linalg.norm(Ps_s-Ps)
    loss_Pi_i=np.linalg.norm(Pi_i-Pi)
    loss_Pi_s=np.linalg.norm(Pi_s-Ps)
    loss_Pnlm_i=np.linalg.norm(Pnlm_i-Pi)
    loss_Pnlm_s=np.linalg.norm(Pnlm_s-Ps)


    ###--Show output plots--###

    Pi=Pi.reshape([(2*hps[0]+1),(2*hps[1]+1),(2*hps[2]+1)])
    Ps=Ps.reshape([(2*hps[0]+1),(2*hps[1]+1),(2*hps[2]+1)])
    Ps_i=Ps_i.reshape([(2*hps[0]+1),(2*hps[1]+1),(2*hps[2]+1)])
    Ps_s=Ps_s.reshape([(2*hps[0]+1),(2*hps[1]+1),(2*hps[2]+1)])
    Pi_i=Pi_i.reshape([(2*hps[0]+1),(2*hps[1]+1),(2*hps[2]+1)])
    Pi_s=Pi_s.reshape([(2*hps[0]+1),(2*hps[1]+1),(2*hps[2]+1)])
    Pnlm_i=Pnlm_i.reshape([(2*hps[0]+1),(2*hps[1]+1),(2*hps[2]+1)])
    Pnlm_s=Pnlm_s.reshape([(2*hps[0]+1),(2*hps[1]+1),(2*hps[2]+1)])

    sl=int(round(Ps_i.shape[2]/2))
    font={'family': 'serif','color':  'darkred','weight': 'normal','size': 16}

    f, axarr = plt.subplots(4, 4)
    axarr[0, 0].set_title('Int', fontdict=font)
    cax=axarr[0, 0].imshow(np.rot90(Pi[:,:,sl]), cmap="Greys_r", interpolation='nearest')
    axarr[0, 0].axis('off')
    axarr[0, 1].set_title('Seg', fontdict=font)
    axarr[0, 1].imshow(np.rot90(Ps[:,:,sl]), cmap="Greys_r", interpolation='nearest')
    axarr[0, 1].axis('off')
    axarr[0, 2].set_title('Loss Int', fontdict=font)
    axarr[0, 2].axis('off')
    axarr[0, 3].set_title('Loss Seg', fontdict=font)
    axarr[0, 3].axis('off')

    axarr[1, 0].text(-5,sl*1.25,'Ws', fontdict=font)
    axarr[1, 0].imshow(np.rot90(Ps_i[:,:,sl]), cmap="Greys_r", interpolation='nearest')
    axarr[1, 0].axis('off')
    axarr[1, 1].imshow(np.rot90(Ps_s[:,:,sl]), cmap="Greys_r", interpolation='nearest')
    axarr[1, 1].axis('off')
    axarr[1, 2].text(sl*0.15,sl*0.2,str(round(loss_Ps_i,2)))
    axarr[1, 2].axis('off')
    axarr[1, 3].text(sl*0.15,sl*0.2,str(round(loss_Ps_s,2)))
    axarr[1, 3].axis('off')

    axarr[2, 0].text(-5,sl*1.25,'Wi', fontdict=font)
    axarr[2, 0].imshow(np.rot90(Pi_i[:,:,sl]), cmap="Greys_r", interpolation='nearest')
    axarr[2, 0].axis('off')
    axarr[2, 1].imshow(np.rot90(Pi_s[:,:,sl]), cmap="Greys_r", interpolation='nearest')
    axarr[2, 1].axis('off')
    axarr[2, 2].text(sl*0.15,sl*0.2,str(round(loss_Pi_i,2)))
    axarr[2, 2].axis('off')
    axarr[2, 3].text(sl*0.15,sl*0.2,str(round(loss_Pi_s,2)))
    axarr[2, 3].axis('off')

    axarr[3, 0].text(-5,sl*1.25,'Wnlm', fontdict=font)
    axarr[3, 0].imshow(np.rot90(Pnlm_i[:,:,sl]), cmap="Greys_r", interpolation='nearest')
    axarr[3, 0].axis('off')
    axarr[3, 1].imshow(np.rot90(Pnlm_s[:,:,sl]), cmap="Greys_r", interpolation='nearest')
    axarr[3, 1].axis('off')
    axarr[3, 2].text(sl*0.15,sl*0.2,str(round(loss_Pnlm_i,2)))
    axarr[3, 2].axis('off')
    axarr[3, 3].text(sl*0.15,sl*0.2,str(round(loss_Pnlm_s,2)))
    axarr[3, 3].axis('off')

    plt.show()
