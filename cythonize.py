#!/usr/bin/env python
'''
Usage: python cythonize.py path_to_setup.py py_file_path ...

python cythonize.py setup.py `cat cython_list
'''

from sys import argv
from os import rename, unlink

try:
	undo_i = argv.index('--undo')
	undo = True
	argv = argv[:undo_i] + argv[undo_i + 1:]
except:
	undo = False

setup_py_path = argv[1] if len(argv) > 1 else 'setup.py'
py_path_list = argv[2:] if len(argv) > 2 else filter(None, file('cython_list').read().split('\n'))
pyx_path_list = [path + 'x' for path in py_path_list]

# read in setup.py
with open(setup_py_path, 'r') as setup_py_file:
	setup_py = setup_py_file.readlines()

if undo:
	for py_path, pyx_path in zip(py_path_list, pyx_path_list):
		try:
			rename(pyx_path, py_path)
		except Exception, e:
			print 'rename', pyx_path, 'to', py_path, '::'
			print e
		else:
			try:
				line = "    '{}': base_flags,\n".format(
							'/'.join(pyx_path.split('/')[1:]))
				setup_py.remove(line)
			except Exception: pass
	try:
		line = "    '{}': base_flags,\n".format(
					'/'.join('kivy/core/text/ctext.pyx'.split('/')[1:]))
		setup_py.remove(line)
	except Exception: pass
else:
	# rename py files to pyx
	for py_path, pyx_path in zip(py_path_list, pyx_path_list):
		try:
			rename(py_path, pyx_path)
		except Exception, e:
			print 'rename', py_path, 'to', pyx_path, '::'
			print e
		else:
			# add pyx files to sources list in setup.py
			setup_py.insert(
				setup_py.index('sources = {\n') + 1,
				("    '{}': base_flags,\n").format(
					'/'.join(pyx_path.split('/')[1:])))
	setup_py.insert(
		setup_py.index('sources = {\n') + 1,
		("    '{}': base_flags,\n").format(
			'/'.join('kivy/core/text/ctext.pyx'.split('/')[1:])))

# make core/text/__init__.py import from pyx file
with open('kivy/core/text/__init__.py', 'r+') as py_file:
	corelines = py_file.readlines()
	lines = corelines[:]
	
	try:
		if undo:
			i1 = lines.index("#DEFAULT_FONT = 'DroidSans'\n")
			i2 = lines.index("## Load the appropriate provider\n") + 1
			
			for i in range(i1, i2):
				lines[i] = lines[i][1:]
			lines.remove('from ctext import LabelBase\n')
		else:
			i1 = lines.index("DEFAULT_FONT = 'DroidSans'\n")
			i2 = lines.index("# Load the appropriate provider\n") + 1
			
			for i in range(i1, i2):
				lines[i] = '#' + lines[i]
			lines.insert(i2, 'from ctext import LabelBase\n')
	except Exception, e:
		print e
	
	py_file.seek(0)
	py_file.writelines(lines)
	py_file.truncate()

if undo:
	unlink('kivy/core/text/ctext.pyx')
else:
	with open('kivy/core/text/ctext.pyx', 'w') as core_py_file:
		cutindex = corelines.index("# Load the appropriate provider\n")
		core_py_file.writelines(corelines[:cutindex])

with open(setup_py_path, 'w') as setup_py_file:
	setup_py_file.writelines(setup_py)
