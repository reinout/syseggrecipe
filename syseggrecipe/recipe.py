import logging
import os
import pkg_resources


class Recipe(object):

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options
        options.setdefault('eggs', '')
        self.dev_egg_dir = self.buildout['buildout']['develop-eggs-directory']
        self.logger = logging.getLogger(self.name)
        force = self.options.get('force-sysegg', 'false')
        self.force_sysegg = (force.lower() == 'true')
        self.added = []

    def install(self):
        eggs = self.options['eggs'].strip()
        eggs = [s.strip() for s in eggs.split('\n')]

        for egg in eggs:
            self.add_dev_link_to_egg(egg)
        return ()

    update = install

    def add_dev_link_to_egg(self, egg):
        try:
            dist = pkg_resources.require(egg)[0]
        except pkg_resources.DistributionNotFound:
            self.logger.warn('No system distribution for %s found.' % egg)
            alternative = self.attempt_dev_link_via_import(egg)
            if alternative:
                return
            if self.force_sysegg:
                raise
            return

        if dist_is_egg_dir(dist):
            # Proper egg like
            # ``/usr/lib/python/dist-packages/EGGNAME.egg/`` instead
            # of a way-too-full ``/usr/lib/python/dist-packages/`` dir.
            egg_egg_link = os.path.join(
                self.dev_egg_dir,
                '%s.egg-link' % dist.project_name)
            f = open(egg_egg_link, 'w')
            f.write(dist.location)
            f.close()
            self.logger.info('Using sysegg %s for %s', dist.location, egg)
            self.added.append(egg_egg_link)
        else:
            # Ouch, a system path directory with possibly a lot of
            # distributions in there! Adding a .egg-link file to the
            # full directory means we enable way too many
            # distributions: everything in that directory.
            self.logger.debug(
                "Sysegg %s's location is %s, which is too generic",
                egg, dist.location)
            # We expect an egg-info file that we can copy.
            all_filenames = os.listdir(dist.location)
            egginfo_filenames = [
                filename for filename in all_filenames
                if (filename.endswith('.egg-info') or filename.endswith('.dist-info'))
                and (filename.startswith(dist.project_name)
                     or
                     filename.startswith(dist.project_name.replace('-', '_'))
                 )]
            if not egginfo_filenames:
                raise RuntimeError(
                    "Cannot find egg-info files in {0} for sysegg {1}".format(
                        dist.location, egg))

            for egginfo_filename in egginfo_filenames:
                egginfo_filepath = os.path.join(dist.location,
                                                egginfo_filename)
                self.logger.info("Using sysegg %s for %s",
                                 egginfo_filepath, egg)
                link_filepath = os.path.join(self.dev_egg_dir, egginfo_filename)
                if os.path.lexists(link_filepath):
                    # Note: yes, lexists() instead of exists(), this one
                    # returns true also if there's a symlink that leads
                    # nowhere. Exists() follows the symlink...
                    os.remove(link_filepath)
                os.symlink(egginfo_filepath, link_filepath)
                self.added.append(link_filepath)

            # Older versions of ourselves used to create an
            # egg-link file. Zap it if it is still there.
            erroneous_old_egglink = os.path.join(
                self.dev_egg_dir, '{0}.egg-link'.format(dist.project_name))
            if os.path.exists(erroneous_old_egglink):
                os.remove(erroneous_old_egglink)
                self.logger.debug("Removed old egglink %s",
                                  erroneous_old_egglink)

    def attempt_dev_link_via_import(self, egg):
        """Create egg-link to FS location if an egg is found through importing.

        Sometimes an egg *is* installed, but without a proper egg-info file.
        So we attempt to import the egg in order to return a link anyway.

        TODO: currently it only works with simple package names like
        "psycopg2" and "mapnik".

        """
        try:
            imported = __import__(egg)
        except ImportError:
            self.logger.warn("Tried importing '%s', but that also didn't work.", egg)
            return
        self.logger.info("Importing %s works, however", egg)
        try:
            probable_location = os.path.dirname(imported.__file__)
        except:  # Bare except
            self.logger.exception("Determining the location failed, however")
            return
        filesystem_egg_link = os.path.join(
            self.dev_egg_dir,
            '%s.egg-link' % egg)
        f = open(filesystem_egg_link, 'w')
        f.write(probable_location)
        f.close()
        self.logger.info('Using sysegg %s for %s', probable_location, egg)
        self.added.append(filesystem_egg_link)
        return True


def dist_is_egg_dir(dist):
    if not dist.location.endswith('egg'):
        return False
    if dist.egg_name() in dist.location:
        return True
    return False
