# -*- coding: utf-8 -*-
# get_max_stress_mises.py — runs under abaqus python (Py2.7/Py3 both)
import os
import sys
sys.path.insert(0, os.getcwd())     # hookkit is staged here by ABQflow
import hookkit


def extract_one(odb_path, task):
	"""The ONLY thing the user writes: physics in, value out.
	Raise on failure — hookkit converts it to None + stderr log."""
	from odbAccess import openOdb          # import inside: testable without Abaqus
	name = task['result_name']

	with hookkit.opened(openOdb(path=odb_path, readOnly=True)) as odb:
		step = odb.steps[task.get('step', list(odb.steps.keys())[-1])]
		frame = step.frames[-1]
		asm = odb.rootAssembly

		if name == 'max_stress_mises':
			vals = frame.fieldOutputs['S'].getSubset(
				region=asm.elementSets[' ALL ELEMENTS']).values
			return hookkit.scalar(max(v.mises for v in vals))
		if name == 'max_displacement':
			vals = frame.fieldOutputs['U'].getSubset(
				region=asm.nodeSets[' ALL NODES']).values
			return hookkit.scalar(max(v.magnitude for v in vals))
		raise ValueError("unsupported result_name: %s" % name)


if __name__ == '__main__':
	hookkit.run(extract_one, source_arg='--odb_path')
