import scipy
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from scalpy.scalar import *
from scalpy.fluids import *
import time
from scipy.integrate import dblquad

start = time.time()

z = np.linspace(2.69, 4.52, 10)

def CMD(z):
    c = 3e5
    H0 = 70
    mpc_to_cm = 3.086e24
    E = np.sqrt(0.279*(1+z)**3 + 0.721)
    X = c/(H0*E)#*mpc_to_cm
    return X

def X(zarray):
    
    x = LCDM(0.3)
    mpc_to_cm = 3.086e24
    chi = [x.co_dis_z(z) for z in zarray]
    return chi

Xchi = X(z)

def n_b(z):
    '''
    Parameters
    ------------
    R: A list - list of radii for the bubbles
    z: A float
    
    Returns
    ---------
    PR: A list - the probabilities of each bubble having that radius
    '''
    R = np.linspace(0.01,60,100)
    sigma = np.log(2)
    Ravg = 47.72*(3-z) #-47.72*z + 231.68 
    PR = [(1/r) * 1/np.sqrt(2*np.pi*sigma**2)*np.exp(-(np.log((r/Ravg)))**2/(2*sigma**2)) for r in R]
    
    return PR

def Vb():
    '''
    Parameters
    ------------
    R: A float A list - list of radii for the bubbles
    
    Returns
    ------------
    VR: A float A list - list of volumes of the bubbles
    '''
    R = np.linspace(0.01,60,100)
    VR = [(4*np.pi/3) * r**3 for r in R]
    
    return VR

def Fdenom(z):
    '''
    Calculates the integral in the denominator of Eq. 9 in the CMB paper
    
    Parameters
    ------------
    R: A float A list - list of radii

    Returns
    --------
    FB: A float A list - integ
    '''
    PR = n_b(z)
    VB = Vb()
    FB = [p*v for p, v in zip(PR, VB)]
    return scipy.integrate.trapz(FB)

def W(k):
    '''
    Parameters
    ------------
    k: A float
    R: A float

    Returns
    ---------
    WkR: A float
    '''
    R = np.linspace(0.01,60,100)
    WkR = [(3/(k*r)**3)*(np.sin(k*r) - k*r*np.cos(k*r)) for r in R]
    return WkR

def Fnum(k, z):
    '''
    Parameters
    -----------
    k: A float
    R: a float

    Returns
    ----------
    FT: a float
    '''
    P = n_b(z)
    V = Vb()
    Wkr = W(k)
    Fpv = [p * v**2 for p, v in zip(P, V)]
    FT = [f * w**2 for f, w in zip(Fpv, Wkr)] 
    return scipy.integrate.trapz(FT) 
    
def F(k, z): # Trying to use z float instead of zarray
    '''
    '''
    
    bot = Fdenom(z) 
    top = Fnum(k,z)
    
    F = top/bot 
    return F 

def G3(k, z):
    y = LCDM(0.3)
    theta_array = np.linspace(0,np.pi,10)
    fxy = lambda kp, theta: (kp**2/(2*np.pi)**2)*np.sin(theta)*y.Pk_bbks(abs(k**2 + kp**2 - 2*k*kp*np.cos(theta)),0)*F(kp,z)
    fg3 = lambda theta: scipy.integrate.simps(fxy(np.logspace(-3,0,10),10),np.logspace(-3,0,10))
    return scipy.integrate.simps([fg3(i) for i in theta_array], theta_array)
def G2(k, z):
    y = LCDM(0.3)
    fg = lambda kp, theta: (kp**2/(2*np.pi)**2)*np.sin(theta)*y.Pk_bbks(abs(k**2 + kp**2 - 2*k*kp*np.cos(theta)),0)*F(kp,z)
    area = dblquad(fg, 1, 10, lambda theta: 0, lambda theta: np.pi)
    return area[0]#dblquad(fg, 1, 1000, lambda theta: 0, lambda theta: np.pi)

def G(k, z): # Trying to use z float instead of zarray
    kparray = np.logspace(-3,0,10)
    x = LCDM(0.3)
    Farray = [F(kp, z) for kp in kparray] # Becomes a float
    Garray = []
    theta_array = np.linspace(0,np.pi, 10)
    
    for theta in theta_array:
   
        for j in range(len(kparray)): # move back 4 spaces

    	    womp_rat = abs(k**2 + kparray[j]**2 - 2*k*kparray[j]*np.cos(theta))

    	    area = (kparray[j]**2)*(1/(2*np.pi)**2)*np.sin(theta)*x.Pk_bbks(womp_rat,0)*Farray[j] 

        Garray.append(area) # added 4 spaces
    
    return scipy.integrate.trapz(Garray)
    
def Pxe(k, z): # changed karray to k
    xe = 0.25
    g = G2(k, z)
    f = F(k, z)
    PXE = xe*(1-xe)*(f + g) 
    return PXE    
	    
def Cttl(l, Xchi, zarray):
    sigmaT = 6.65e-25
    n_e = 6.9e-8
    mpc_to_cm = 3.086e24
    a = 1
    k = [i/j for i,j in zip(l, Xchi)]
    PXE = []
    for z in zarray:
    	temp = []
    	for kk in k:
    	    temp.append(Pxe(kk,z))
    	PXE.append(temp)
    
    Carray = []
    for i in range(len(Xchi)):
    
	pxe = [p/Xchi[i]**2 for p in PXE[i]]
        area = scipy.integrate.trapz(pxe)
	Carray.append(area)

    Cttlarray = [mpc_to_cm**2*c*sigmaT**2*n_e**2/a**4 for c in Carray]
    return Cttlarray

l = np.linspace(0.1,3000,len(z))
C = Cttl(l, Xchi, z)
C = [c*(i*(i+1)/(2*np.pi)) for i, c in zip(l,C)]

larray = np.array(l)
Carray = np.array(C)
print("The length of l is", len(larray))
print('The length of C is', len(Carray))

fig, ax = plt.subplots()

ax.plot(l[:len(C)], C)

#ax.set_xscale('log')
ax.set_yscale('log')

ax.set(xlabel = '$l$', ylabel = r'$C_l^{\tau\tau} l(l+1)/2\pi$')

end = time.time()
print('Total running time:', (end-start)/3600)

plt.show()
