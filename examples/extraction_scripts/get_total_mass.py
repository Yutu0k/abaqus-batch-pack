# -*- coding: utf-8 -*-
# get_total_mass.py — runs under abaqus cae (Py2.7/Py3 both)
import os
import sys
sys.path.insert(0, os.getcwd())     # hookkit is staged here by ABQflow
import hookkit


def extract_one(inp_path, task):
	"""The ONLY thing the user writes: physics in, value out.
	Raise on failure — hookkit converts it to None + stderr log."""
	from abaqus import mdb               # import inside: testable without Abaqus
	name = task['result_name']

	mdb.ModelFromInputFile(name='_hook_temp', inputFileName=inp_path)
	if 'Model-1' in mdb.models:
		del mdb.models['Model-1']

	root_assembly = mdb.models['_hook_temp'].rootAssembly
	region = root_assembly.sets['ALL'].elements

	if name == 'total_mass':
		mass = root_assembly.getMassProperties(regions=region)['mass']
		return hookkit.scalar(mass)
	raise ValueError("unsupported result_name: %s" % name)


if __name__ == '__main__':
	hookkit.run(extract_one, source_arg='--inp_path')
