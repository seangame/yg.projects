#!/usr/bin/env python
# Generated by jaraco.develop (https://bitbucket.org/jaraco/jaraco.develop)
import setuptools

with open('README.txt') as readme:
	long_description = readme.read()
with open('CHANGES.txt') as changes:
	long_description += '\n\n' + changes.read()

setup_params = dict(
	name='yg.projects',
	use_hg_version=True,
	author="Jason R. Coombs",
	author_email="jason.coombs@yougov.com",
	description="yg.projects",
	long_description=long_description,
	url="https://yougov.kilnhg.com/Code/Repositories/support/yg-projects",
	packages=setuptools.find_packages(),
	namespace_packages=['yg'],
	setup_requires=[
		'hgtools',
	],
	entry_points=dict(
		console_scripts=[
			'submit-time=yg.projects.commands:InteractiveEntry.run',
		],
	),
	classifiers = [
		"Development Status :: 5 - Production/Stable",
		"Programming Language :: Python :: 3.2",
		"Programming Language :: Python :: 3.3",
		"Programming Language :: Python :: 3.4",
		"Programming Language :: Python :: 3.5",
	],
	install_requires = [
		'requests',
		'python-dateutil',
		'keyring',
		'jaraco.util>=10,<11',
	],
)
if __name__ == '__main__':
	setuptools.setup(**setup_params)
