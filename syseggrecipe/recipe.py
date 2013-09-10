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

    def install(self):
        eggs = self.options['eggs'].strip()
        eggs = [s.strip() for s in eggs.split('\n')]

        for egg in eggs:
            self.add_dev_link_to_egg(egg)
        return ()

    update = install

    def force_syseggs(self):
        force = self.options.get('force-sysegg', 'false')
        return force.lower() == 'true'

    def add_dev_link_to_egg(self, egg):
        try:
            dist = pkg_resources.require(egg)[0]
        except pkg_resources.DistributionNotFound:
            self.logger.warn('No system distribution for %s found.' % egg)
            if self.force_syseggs():
                raise
            return

        if egg in dist.location:
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
        else:
            # Ouch, a system path directory with possibly a lot of
            # distributions in there! Adding a .egg-link file to the
            # full directory means we enable way too many
            # distributions: everything in that directory.
            self.logger.debug(
                "Sysegg %s's location is %s, which is too generic",
                egg, dist.location)
            link_to_this = os.path.join(dist.location, dist.project_name)
            if not os.path.exists(link_to_this):
                raise RuntimeError(
                    "Trying {} for sysegg: not found".format(
                        link_to_this))
            self.logger.info("Using sysegg path %s for %s",
                             link_to_this, egg)
            self.symlink(link_to_this, dist.project_name)
            # Also symlink the egg-info files.
            all_filenames = os.listdir(dist.location)
            egginfo_filenames = [
                filename for filename in all_filenames
                if filename.endswith('.egg-info')
                and filename.startswith(dist.project_name)]
            for egginfo_filename in egginfo_filenames:
                link_to_this = os.path.join(dist.location,
                                            egginfo_filename)
                self.symlink(link_to_this, egginfo_filename)
                self.logger.debug("Symlinked egg-info dir %s, too", 
                                  link_to_this)
            # Older versions of ourselves used to create an
            # egg-link file. Zap it if it is still there.
            erroneous_old_egglink = os.path.join(
                self.dev_egg_dir, '{}.egg-link'.format(dist.project_name))
            if os.path.exists(erroneous_old_egglink):
                os.remove(erroneous_old_egglink)
                self.logger.debug("Removed old egglink %S",
                                  erroneous_old_egglink)

    def symlink(self, origin, link_name):
        """Add a symlink LINK_NAME in the dev-egg dir to origin."""
        link_file = os.path.join(self.dev_egg_dir,
                                 link_name)
        if os.path.exists(link_file):
            os.remove(link_file)
        os.symlink(origin, link_file)
