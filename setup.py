import setuptools
import io

NAME = 'GNLookUp'
DESCRIPTION = 'News Scraper and Classifier.'
URL = 'https://github.com/me/myproject'
EMAIL = 'dario.pena@uexternado.edu.co'
AUTHOR = 'Dario Peña'
REQUIRES_PYTHON = '>=3.6.0'
VERSION = '0.1.0'
REQUIRED = [
	'requests'
]

try:
	with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
		long_description = '\n' + f.read()
except FileNotFoundError:
	long_description = DESCRIPTION

if __name__ == '__main__':
	setuptools.setup(
		name=NAME,

		version=VERSION,

		python_requires=REQUIRES_PYTHON,

		packages=setuptools.find_packages(exclude=['tests']),

		install_requires=REQUIRED,

		extras_requires={
			'all': ['python-utils'],
		},

		setup_requires=['pytest-runner'],

		tests_require=['pytest'],

		package_data={
			'': ['*.rst', '*.txt', '*.md'],
		},

		zip_safe=False,

		author=AUTHOR,
		
		author_email=EMAIL,

		description=DESCRIPTION,

		long_description='A very long description',

		long_description_content_type='text/markdown',

		license='BSD',

		url=URL,
	)
