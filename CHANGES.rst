CHANGES
=======


0.2 (2013-09-10)
----------------

- Fix in README for running sysegg standalone.

- Distributions that aren't eggs but directories directly inside a
  ``sys.path`` directory would have the actual system folder as their
  location. This used to mean that everything in that system folder
  can erroneously be used as a system egg. Not anymore, as those
  directories are now symlinked directly instead of being used through
  a too-generic ``.egg-link`` file.

- This recipe uses symlinks for the above fix, which means it doesn't
  work on windows anymore.


0.1 (2013-02-05)
----------------

- Patch code to allow for force-sysegg=false

- Add original code from osc.recipe.sysegg.

- Add buildout and setup.py.

- Added readme, changes and MIT license.
