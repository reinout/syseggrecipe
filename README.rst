Description
===========

Buildout is great for repeatable builds of Python packages. It grabs a
bunch of packages off Pypi (the Python package index) and you're done.
Pure Python packages are no problem. But sometimes there are packages
that are a bit harder.

Some packages require quite a number of libraries to be available,
preferrably as development packages. In Debian/Ubuntu terms, this are
the ``*-dev`` packages. These packages contain C code or build upon
existing libraries. All in all, this is sometimes functionality that's
better provided through your OS. Who wants to build "numpy" by hand?
Way nicer to just do an ``aptitude install python-numpy`` and to
automatically get all the dependencies.

The ``syseggrecipe`` buildout recipe provides a handy way to re-use
those perfectly packaged "system eggs". They are already there, so why
not use them? We know that buildout is best used to gather everything
together on its own, but there are practical limits. Sometimes system
eggs are handier.

The ``syseggrecipe`` recipe allows you to specify which eggs you want
to grab from your OS and it injects just those eggs into your buildout
so that you can use them without pulling in everything that's on your
system path.


Example
========

An example of how to use the recipe. Please note that the sysegg recipe
must be the first buildout part to make sure it gets the first go at
grabbing global eggs.::

  [buildout]
  parts = sysegg
  
  [sysegg]
  recipe = syseggrecipe
  eggs =
    netCDF4

To stop the buildout when not all syseggs are installed include: 
`force-sysegg = true`::

  [buildout]
  parts = sysegg

  [sysegg]
  recipe = syseggrecipe
  force-sysegg = true
  eggs =
    netCDF4

This way, the specified eggs **must** be installed globally. Otherwise
they are optional (which might be a fine choice, too).


How it works
============

The core of the system is buildout's concept of "development eggs".
This is a special directory (``develop-eggs/'' within your buildout)
with pointers to Python packages that are currently being developed.
These pointers take precedense over any other item. Examples include
the project you're working on, but also items you installed with
`mr.developer <http://pypi.python.org/pypi/mr.developer>`_.

For every egg specified in the part, setuptools is asked for a
matching distribution. If one is found, it is inserted into the
develop eggs directory. There are two ways:

- If it is a proper egg, an ``EGGNAME.egg-link`` file is made in the
  ``develop-eggs/`` directory that points at the correct egg.

- If it isn't a real egg, a matching ``EGGNAME*.egg-info`` file or
  directory is looked for and symlinked into the ``develop-eggs/``
  directory.

Both ways are enough for setuptools to know the global egg exists. As
buildout doesn't strip out the system path (except for the abortive
1.5/1.6/1/7 releases), setuptools can find them globally. We just had
to make sure it knows how to find them.


Origin
======

This package is a fork of (and improvement on)  osc.recipe.sysegg_.
As such it is licensed under MIT. 

.. _osc.recipe.sysegg: http://pypi.python.org/pypi/osc.recipe.sysegg
