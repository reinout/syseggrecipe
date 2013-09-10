import logging
import os
import pkg_resources
import shutil


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
        return self.added

    update = install

    def add_dev_link_to_egg(self, egg):
        try:
            dist = pkg_resources.require(egg)[0]
        except pkg_resources.DistributionNotFound:
            self.logger.warn('No system distribution for %s found.' % egg)
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
                if filename.endswith('.egg-info')
                and filename.startswith(dist.project_name)]
            if not egginfo_filenames:
                raise RuntimeError(
                    "Cannot find egg-info files in {} for sysegg {}".format(
                        dist.location, egg))

            for egginfo_filename in egginfo_filenames:
                egginfo_filepath = os.path.join(dist.location,
                                                egginfo_filename)
                self.logger.info("Using sysegg %s for %s",
                                 egginfo_filename, egg)
                target = os.path.join(self.dev_egg_dir, egginfo_filename)
                shutil.copyfile(egginfo_filepath, target)
                self.added.append(target)
            
            # Older versions of ourselves used to create an
            # egg-link file. Zap it if it is still there.
            erroneous_old_egglink = os.path.join(
                self.dev_egg_dir, '{}.egg-link'.format(dist.project_name))
            if os.path.exists(erroneous_old_egglink):
                os.remove(erroneous_old_egglink)
                self.logger.debug("Removed old egglink %S",
                                  erroneous_old_egglink)


def dist_is_egg_dir(dist):
    if not dist.location.endswith('egg'):
        return False
    if dist.egg_name() in dist.location:
        return True
    return False
