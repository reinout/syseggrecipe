import os

from setuptools import setup, find_packages

version = '1.0'


def read_file(name):
    return open(os.path.join(os.path.dirname(__file__),
                             name)).read()

readme = read_file('README.rst')
changes = read_file('CHANGES.rst')

setup(name='syseggrecipe',
      version=version,
      description=("Syseggrecipe allows the reuse of system eggs in "
                   "buildout installs"),
      long_description='\n\n'.join([readme, changes]),
      classifiers=[
          'Framework :: Buildout',
          'Topic :: Software Development :: Build Tools',
          'Development Status :: 5 - Production/Stable',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Environment :: MacOS X',
          'Environment :: Console',       
      ],
      packages=find_packages(exclude=['ez_setup']),
      keywords='',
      author='Roland van Laar',
      author_email='roland@nelen-schuurmans.nl',
      url='https://github.com/nens/syseggrecipe',
      license='MIT',
      zip_safe=False,
      install_requires=[
          'zc.buildout',
          'zc.recipe.egg',
      ],
      entry_points={'zc.buildout': [
          'default = syseggrecipe.recipe:Recipe']}
      )
