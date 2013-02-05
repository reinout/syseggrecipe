Description
===========

The buildout syseggrecipe uses system installed eggs, 
called syseggs.
These syseggs are used instead of installing them again during buildout.
This is usefull for hard to compile eggs or eggs that need specific 
development libraries.

Example
========

An example of how to use the recipe. Please note that the sysegg recipe
must be the first buildout part.::

  [buildout]
  parts = sysegg
  
  [sysegg]
  recipe = syseggrecipe
  eggs =
    netCDF4

To stop the buildout when not all syseggs are installed include: 
`force-sysegg = True`.::

  [buildout]
  parts = sysegg

  [sysegg]
  recipe = syseggrecipe
  force-sysegg = true
  eggs =
    netCDF4

Tests
======

To test if all syseggs are available while `force-sysegg = true` is 
enabled in the buildout configuration.:: 

  bin/buildout sysegg:force-sysegg=false install sysegg

Origin
======

This package is a fork of osc.recipe.sysegg_.
As such it is licensed under MIT. 

.. _osc.recipe.sysegg: http://pypi.python.org/pypi/osc.recipe.sysegg
