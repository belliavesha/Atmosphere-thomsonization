import sys
#import copy
#from math import *
import numpy as np
#import numpy.random as random
import matplotlib
matplotlib.use('Agg')
#import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
from pylab import *
import matplotlib.ticker as ticker
#import scipy.ndimage as ndimage
#import pyfits
#import h5py
#import mcmcpy
#import emcee
import math, os
import corner

spath = ""
ndfiles = len(sys.argv)
spaths = []
if(ndfiles == 1):
	print ("Error: Should give data files as input!")
	quit()
#if(ndfiles == 2): #only one input file given
#	print ("Outputs read from and saved in:")
#	print (str(sys.argv[1]))
#	spath = str(sys.argv[1])
#	spaths.append(str(sys.argv[1]))
if(ndfiles >= 2):
	print ("Outputs read from (but triangle named only according to the last file):")
	for ii in range(1,ndfiles): 
		print (str(sys.argv[ii]))
		spaths.append(str(sys.argv[ii]))

print (spaths)



#read output from emcmc run:
#spath = "chains/emcp2datcc-"

#npars = 12
nwalk = 20#50
only_wmoves = False#True
iweights = True#False#True
plot_cpoint = True#False
samples_all = []
weights_all = []

#param_names = ["rad","mass","incl","theta","rho","dist","abb","gammaphot","scfrac","tplanck","logisg","nh","ipt","imt","mpr"]
swapmr = True
param_names = [
         "$R_{\\mathrm{eq}}$ \n (km)",
         "$M$ \n ($M_{\\odot}$)",
         "$i$ \n (deg)",
         "$\\theta$ \n (deg)",
	 ]

params_true = [12.0,1.4,40.0,60.0]
params = params_true
low_limit = [4.0, 1.0, 20.0, 40.0]
high_limit = [18.0, 2.0, 60.0, 80.0]
ignore_walkers = [6,7,19]#[8,19]#[3,5,8]


ndim = len(params)

for ispa in range(0,ndfiles-1):
	npars = len(params)
	spath = spaths[ispa]
	datafile = spath + "emcee.dat"
	#datafile = spath + "kmb.dat
	#full_chain= [[] for x in xrange(npars+1)]
	full_chain= [[] for x in range(npars+1)]
	weights = []
	Nchain_size = sum(1 for line in open(datafile))#50000
	print ("This file have ", Nchain_size, " lines")
	#input = file(datafile, 'r')
	input = open(datafile, 'r')
	lines = input.readlines()
	input.close()

	c_lines = int(Nchain_size/2)#2000#2500 #burn-in not read
	while(c_lines % nwalk != 0):
		c_lines = c_lines+1 
	print("Lines commented:", c_lines)

	nsamples = Nchain_size-c_lines

	for j in range(0,len(full_chain)):
		for i in range(c_lines,Nchain_size): #not reading comment lines
			parts = lines[i].split()
			full_chain[j].append(float(parts[j]))
		parts = lines[c_lines].split()

	if(iweights):
		for i in range(c_lines,Nchain_size):
			parts = lines[i].split()
			weights.append(float(parts[j+1]))

	full_chain = np.array(full_chain)
	#remove the walker numbers from array:
	full_chain = full_chain[1:,:]
	samples = full_chain.T#reshape([nsamples, ndim])

	#print(samples[0::nwalk,:])
	llen = int(len(samples[:,0])/nwalk)
	print("llen=",llen)
	for igwa in range(0,llen):
		ignorable = np.array(ignore_walkers)+(nwalk-len(ignore_walkers))*igwa
		#print(ignorable)
		samples = np.delete(samples,ignorable,0)
	#print(samples[17::nwalk,:])
	#print(samples[0::nwalk-3,:])
	samples_all.append(samples)
	weights_all.append(weights)



samples = samples_all[0]
for ii in range(1,ndfiles-1):
	samples = np.append(samples,samples_all[ii],0)

if(swapmr):
	samples_temp = np.copy(samples)
	#print(samples[:,0])
	samples[:,0] = np.copy(samples_temp[:,1])
	samples[:,1] = np.copy(samples_temp[:,0])

if not(only_wmoves):
	limits =  list(zip(low_limit,high_limit))
	if(plot_cpoint):
		print("quantiles=",)
		for ipar in range(0,len(samples[0,:])):
			qtls = corner.quantile(samples[:,ipar],(0.025,0.16,0.5,0.84,0.975))
			print(qtls)
		fig = corner.corner(samples,labels=param_names[0:npars],truths=params[0:npars],range=limits[0:npars], levels=(0.68,0.95,), 
quantiles=(0.025,0.16,0.84,0.975),smooth=0.75,smooth1d=1.0)#,color="darkorange")
	else:
		fig = corner.corner(samples,labels=param_names[0:npars],range=limits[0:npars])#,color="darkorange")

	if(ndfiles == 2):
		fig.savefig(spath+"emcmc_triangleX.pdf")
	else:
		fig.savefig(spath+"emcmc_triangleXCC.pdf")
	plt.close()











#quit()
#Copy pastes from somewhere else, not checked yet:
print("Plotting next also walker movements:")

for ispa in range(0,ndfiles-1):

	spath = spaths[ispa]
	#print full_chain[0,:]
	#wsamples = samples.T
	wsamples = samples_all[ispa].T
	weights = weights_all[ispa]



	#plot the movements in different parameters:
	plt.figure(1)
	plt.suptitle("Param values as function of moves for separate walkers")

	param_names = [
		 "$R_{\\mathrm{eq}}$ \n (km)",
		 "$M$ \n ($M_{\\odot}$)",
		 "$i$ \n (deg)",
		 "$\\theta$ \n (deg)",
		 ]

	if(iweights):
		wsamples = np.append(wsamples,[weights],axis=0)
		npars = npars+1
		low_limit.append(-4.0)
		high_limit.append(0.0)
		param_names.append("W")


	for i in range(0,npars):
	
		gs = GridSpec(1, 1)
		#ax = subplot(gs[0,0])
		ax = plt.subplot(3,3,i+1)
		frame1 = plt.gca()
		#plt.gca().set_color_cycle(['red', 'blue'])#, 'green'])
		for j in range(0,nwalk):
			full = wsamples[i,j::nwalk]
			#full = full[full!=0.0]
			#label if walker is stuck...
			if(j == 27):#j == 5 or j == 49 or j==27):#len(full) > 100):# and abs((full[len(full)-1]-full[len(full)-25])/full[len(full)-1]) < 0.01):
				ax.plot(full,alpha=0.5,label="walker " + str(j))
			#	if(i == 8):
			#		print full
			else:
				ax.plot(full,alpha=0.5)


		plt.setp(ax.get_yticklabels(), fontsize=7)
		#frame1.axes.xaxis.set_ticklabels([])
		tick_spacing = len(full)/2
		#print "tick_spacing = ", tick_spacing
		ax.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
		ax.xaxis.set_major_formatter(FormatStrFormatter('%i'))
		plt.setp(ax.get_xticklabels(), fontsize=5)
		plt.title(param_names[i],fontsize=10)
		ax.set_ylim(low_limit[i], high_limit[i])
		#legend = frame1.axes.legend(loc='upper right',prop={'size':6})
		#ax.plot(full_chain3[0,:],full_chain3[1,:])
		#ax.set_xlabel(param_name[i])
		#ax.set_ylabel('Flux')
		#plt.legend(['fitted', 'data'], loc='upper left')
		#plt.legend(['fitted "wrong solution"', 'exact data'], loc='upper left')
		#savefig("test"+ str(i) + ".png")
		#plt.close()
	#svname = "test_all2_"+ str(iembl) + ".png"
	#svname = spath + "wmoves.png"
	svname = spath + "wmoves.pdf"
	savefig(svname)
	print ("Wmoves saved to " + svname)
	plt.close()







