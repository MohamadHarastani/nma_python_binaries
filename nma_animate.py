#!/usr/bin/env python3
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#
# animate.py  - oscillating animation of normal modes
# Modified script from the ModeHunter package, http://modehunter.biomachina.org
#
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#
# Request to cite published literature:
#
# When using this software in scholarly work please cite the publications(s)
# posted at http://modehunter.biomachina.org/fref.html
# 
#
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
import numpy 
import pickle
import sys
import string
import copy
from .m_inout_Bfact import *

def compute_animation(pdb_name,pickle_name,start_mode,end_mode,amplitude,outname,numframes,step,thr_mass):
	"top level function for writing animated traectories in PDB format"
 
	# process the input files, sanity checks
	f = open(pickle_name, 'r')
	eigvecs = pickle.load(f)
	f.close()
	s1,s2 = numpy.shape(eigvecs)
	s2=s2-1
	#assert s1 / 3.0 == s1 // 3.0, "animate> Error: pickle length not a multiple of 3"
	#assert s2 / 3.0 == s2 // 3.0, "animate> Error: pickle width not a multiple of 3"
	print('animate> Mode pickle file %s read, containing %i modes for %i atoms' % (pickle_name, s1, s2 / 3))

	bfact = m_inout_import_bfact(pdb_name)

	coords = m_inout_import_coords(pdb_name)
	natoms = len(coords)/3
	assert natoms == s2/3, "animate> Error: number of atoms in PDB does not match input pickle number of columns"
	#assert s1 > 6, "animate> Error: pickle file contains insufficient number of modes"
	if start_mode <= 0:
		print("animate> Did not recognize start mode index, reset to 7")
		start_mode = 7
	if start_mode > s1:
		print("animate> Start mode index set to max possible value, %i" % s1)
		start_mode = s1
	if end_mode < start_mode:
		print("animate> Did not recognize end mode index, reset to %i" % start_mode)
		end_mode = start_mode
	if end_mode > s1:
		print("animate> End mode index set to max possible value, %i" % s1)
		end_mode = s1

	# prepare a list of elongations
	elongation = numpy.array([])
	for i in numpy.arange(numframes):
		elongation = numpy.append(elongation,amplitude * numpy.math.cos(i*(2*numpy.math.pi)/numframes))

	# create animations for selected range of modes
	nummodes = end_mode - start_mode + 1
	animations = numpy.zeros((nummodes,s2,numframes))
	for i in numpy.arange(nummodes):
		print("animate> Computing %i steps of animation of mode %i" % (numframes, i + start_mode))
		for j in numpy.arange(s2):
			for k in numpy.arange(numframes):
				animations[i][j][k] = coords[j]+float(eigvecs[i+start_mode-1][j])*elongation[k]

	# output the animations
	for i in numpy.arange(nummodes):
		f_name = outname + ('_%03d' % (i+start_mode)) + '.pdb'
		print("animate> Writing %i steps of animation to file %s" % (numframes, f_name))
		f=open(f_name,'w')
		for k in numpy.arange(numframes):
			inodenum = 0
			index_atom_accept = 0
			for j in numpy.arange(0,3*natoms,3*step):
				inodenum += 1
				if bfact[inodenum-1] > thr_mass:
					index_atom_accept += 1
					f.write('ATOM  ')
					f.write('%5s' % index_atom_accept)
					f.write(' QPDB')
					f.write(' QPDB')
					f.write('%5s    ' % index_atom_accept)
					f.write('%8.3f' % animations[i][j][k])
					f.write('%8.3f' % animations[i][j+1][k])
					f.write('%8.3f' % animations[i][j+2][k])
					f.write('%6.2f' % 1.00)
					f.write('%6.2f' % bfact[inodenum-1])
					f.write('\n')
			f.write('TER')
			f.write('\n')
			f.write('ENDMDL')
			f.write('\n')
		f.close()
	print("animate> All done")

# Main
  
if __name__ == '__main__':
	if len(sys.argv) < 9 or len(sys.argv) > 10:
		print('Usage: ./nma_animate.py pdb_name pickle_name start_mode end_mode amplitude outname numframes step thr_mass')
		print(' ')
		print('Input:')
		print('  inpdb:       PDB file containing N atoms')
		print('  inpickle:    Existing python pickle file containing 3M modes for the N atoms')
		print('  start:       User-specified start index of desired mode range (1 <= start <= 3M)')
		print('  end:         User-specified end index of desired mode range (start <= end <= 3M)')
		print('  amplitude:   Mode amplitude as root-mean-square deviation from inpdb (in Angstrom)')
		print('  outname:     User-defined text string for output file names, see below')
		print('  step:     Step for reducing the number of atoms')
		print('  massthr:     Threshold on atom mass for reducing the number of atoms')
		print(' ')
		print('Output:')
		print('  outname_#.pdb: Oscillating trajectories in PDB format corresponding to mode range')
	else:
		compute_animation(sys.argv[1],sys.argv[2],int(sys.argv[3]),int(sys.argv[4]),float(sys.argv[5]),sys.argv[6],int(sys.argv[7]),int(sys.argv[8]),float(sys.argv[9]))
	sys.exit()



