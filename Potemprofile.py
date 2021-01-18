# -*- coding: utf-8 -*-
"""
Created on Mon Dec 28 14:38:58 2020

@author: AndrewPC
"""
import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
import pandas as pd
import metpy.calc as mpcalc
from metpy.units import units

def alt2pres(altitude):
  

    press = 100 * ((44331.514 - altitude) / 11880.516) ** (1 / 0.1902632)

    return press

def theta(p, T, p0=101325.0, k=0.286):
   
    return T * (p0/p)**k


ds = xr.open_dataset('E:/Climate Physics/MAIO/Cabauw Large scale circulation/cesar_tower_meteo_lb1_t10_v1.2_202010.nc')


temp = ds.TA

z = np.array([200.0, 140.0, 80.0, 40.0, 20.0, 10.0, 2.0])
pres = alt2pres(z)
"""

ds.assign_coords(pres=("p", pres))

temp_new = temp.assign_coords(pres=("z", pres)) #added pressure coord in the temp dataarray


exp = temp_new.expand_dims("z") 
exp.assign_coords(pres=("z", pres))
exp = temp_new.expand_dims("z") 

temp2 = temp.values #dataarray to numpy
"""
temp2 = temp.resample(time='H').mean().values #resample to Hours

t_200 = temp2[:, 0]-273.15  #temperature at 200m in degC
t_140 = temp2[:, 1]-273.15
t_80 = temp2[:, 2]-273.15
t_40 = temp2[:, 3]-273.15
t_20 = temp2[:, 4]-273.15
t_10 = temp2[:, 5]-273.15
t_2 = temp2[:, 6]-273.15

theta_200 = theta(alt2pres(200), t_200)         #pot temp at 200m in degC
theta_140 = theta(alt2pres(140), t_140)
theta_80 = theta(alt2pres(80), t_80)
theta_40 = theta(alt2pres(40), t_40)
theta_20 = theta(alt2pres(20), t_20)
theta_10 = theta(alt2pres(10), t_10)
theta_2 = theta(alt2pres(2), t_2)                  
                  
potemp = np.vstack((theta_200, theta_140, theta_80, theta_40, theta_20, theta_10, theta_2))


fig, ax = plt.subplots(figsize=(12,6))
date = 398
ax.plot(potemp[:,22], z) 
ax.set_xlabel('Potential Temperature (C)')
ax.set_ylabel('Height (m)')
ax.set_title('Potential temperature profile for') #(date))
plt.tight_layout()

# z = units.length(z, "m")
# potemp = units.temperature(potemp, "C")
BVF = mpcalc.brunt_vaisala_frequency_squared(z *units.meter, potemp*units.degC, vertical_dim=0)
freq = np.array(BVF, dtype='float')


# count=[]
# for i in range(len(freq)):
#     if np.all(freq[i])>0:
        
#         count=+1
#     else   
# print(count)

# vd = np.zeros((7,744), 'bool')
# vd[0,:] = freq[0,:] >=0
# vd[1,:] = freq[1,:] >=0
# vd[2,:] = freq[2,:] >=0
# vd[3,:] = freq[3,:] >=0
# vd[4,:] = freq[4,:] >=0
# vd[5,:] = freq[5,:] >=0
# vd[6,:] = freq[6,:] >=0

# valid_in = vd.all(axis=0)
vd = (freq>=0).all(axis=0)
freq_stable = freq[:,vd]
