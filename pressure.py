# -*- coding: utf-8 -*-
"""
Created on Wed Dec  9 21:33:35 2020

@author: teunz
"""
import pandas as pd
import numpy as np

##import data
debilt = pd.read_csv('KNMI_20201209_hourly_260.txt', sep=",", header=12, names=["STN", "YYYYMMDD", "HH", "P260"])
roffa = pd.read_csv('KNMI_20201209_hourly_344.txt', sep=",", header=12, names=["STN", "YYYYMMDD", "HH", "P344"])
cabauw = pd.read_csv('KNMI_20201209_hourly_348.txt', sep=",", header=12, names=["STN", "YYYYMMDD", "HH", "P348"])
debilt['HH'] = debilt['HH']-1
debilt["HH"] = debilt.HH.map("{:02}".format)
debilt['Datetime'] = pd.to_datetime(debilt['YYYYMMDD'].astype(str) + debilt['HH'], format='%Y%m%d%H')
frames = [roffa,debilt,cabauw]
pressure = pd.concat(frames,axis=1)
pressure = pressure.drop(['YYYYMMDD', 'HH', 'STN'], axis=1)
pressure = pressure.set_index(pd.DatetimeIndex(pressure['Datetime']))
pressure = pressure.drop(['Datetime'], axis=1)
P = pressure.to_numpy() #hPa

##Derive geowind
rho = 1013 #hPA
omega = .000072921 #rad/s
lat = 51.970 #degrees north, for Cabauw
f = 2*omega*np.sin(lat) #rad/s
dp = (P[:,0]-P[:,1])/(.556*111200) #calc pressure gradient between roffa and debilt, where .556 is distance between roffa and debilt in degrees
pk = P[:,0] + dp*.0427*111200 #interpolated pressure at k, where .0427 is distance between roffa and point k
pn = P[:,0] + dp*.487*111200 #interpolated pressure at n, where .487 is distance between roffa and point n
dpdx = (P[:,2] - pk)/(.437*111200) #hPa/degree, calc pressure gradient between cabauw and k, where .437 is distance between them in degrees
dpdy = (pn - P[:,2])/(.082*111200) #hPa/degree, calc pressure gradient between cabauw and n, where .082 is distance between them in degrees
ug = -1/(rho*f)*dpdy #
vg = 1/(rho*f)*dpdx #
