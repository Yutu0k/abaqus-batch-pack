# -*- coding: utf-8 -*-
"""Reference hook demonstrating ``hookkit.field`` for large field output.

Overview
--------
When extracting large field data (e.g. stress tensors at every element),
the data should be written as a CSV sidecar rather than stuffed into
stdout JSON.  ``hookkit.field()`` handles this automatically — the user
only provides rows + columns.

Modes (controlled by the Spec, not the hook code)
--------------------------------------------------
- ``"output": "file"``   → always CSV + envelope   (recommended for fields)
- ``"output": "inline"`` → always stdout JSON       (small vectors)
- ``"output": "auto"``   → threshold-based (default)

Usage as a hook
---------------
This script follows the standard ABQflow hook protocol.  It accepts
``--odb_path``, ``--tasks_json``, and ``--job_name``, and prints its
results wrapped in ``===ABQ_RESULT_BEGIN===`` / ``===ABQ_RESULT_END===``
sentinels.

Test without Abaqus
-------------------
::

	python examples/extraction_scripts/reference_field_hook.py \\
		--odb_path /fake/path.odb \\
		--tasks_json /tmp/tasks.json
"""

import os
import sys
sys.path.insert(0, os.getcwd())
import hookkit


def extract_one(odb_path, task):
	"""Extract a field or scalar from the ODB."""
	from odbAccess import openOdb          # import inside: testable without Abaqus
	name = task['result_name']

	with hookkit.opened(openOdb(path=odb_path, readOnly=True)) as odb:
		step = odb.steps[task.get('step', list(odb.steps.keys())[-1])]
		frame = step.frames[-1]

		# -- scalar example -------------------------------------------------
		if name == 'max_stress_mises':
			asm = odb.rootAssembly
			vals = frame.fieldOutputs['S'].getSubset(
				region=asm.elementSets[' ALL ELEMENTS']).values
			return hookkit.scalar(max(v.mises for v in vals))

		# -- field example --------------------------------------------------
		if name == 'stress_field':
			vals = frame.fieldOutputs['S'].values
			rows = [[v.elementLabel, v.mises] for v in vals]
			columns = task.get('columns', ['element_label', 'mises_stress'])
			return hookkit.field(task, rows, columns)

		# -- field example with multiple components -------------------------
		if name == 'stress_tensor':
			vals = frame.fieldOutputs['S'].values
			rows = [[v.elementLabel, v.mises, v.maxPrincipal, v.midPrincipal, v.minPrincipal]
					for v in vals]
			columns = task.get('columns',
				['element_label', 'mises', 'max_principal', 'mid_principal', 'min_principal'])
			return hookkit.field(task, rows, columns)

		raise ValueError("unsupported result_name: %s" % name)


if __name__ == '__main__':
	hookkit.run(extract_one, source_arg='--odb_path')
