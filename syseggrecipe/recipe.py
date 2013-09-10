import logging
import os
import pkg_resources


class Recipe(object):

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options
        options.setdefault('eggs', '')

    def install(self):
        logger = logging.getLogger(self.name)
        eggs = self.options['eggs'].strip()
        eggs = [s.strip() for s in eggs.split('\n')]

        dev_egg_dir = self.buildout['buildout']['develop-eggs-directory']

        for egg in eggs:
            try:
                dist = pkg_resources.require(egg)[0]
            except pkg_resources.DistributionNotFound:
                logger.warn('No system distribution for %s found.' % egg)
                if self.force_syseggs():
                    raise

            else:
                if egg in dist.location:
                    # Proper egg instead of a
                    # /usr/lib/python/dist-packages dir.
                    egg_egg_link = os.path.join(
                        dev_egg_dir,
                        '%s.egg-link' % dist.project_name)
                    f = open(egg_egg_link, 'w')
                    f.write(dist.location)
                    f.close()
                    logger.info('Using %s for %s', dist.location, egg)
                else:
                    # Ouch, a some_syspath_dir/EGGNAME dir...
                    logger.debug(
                        "Sysegg %s's location is %s, which is too generic",
                        egg, dist.location)
                    link_to_this = os.path.join(dist.location, dist.project_name)
                    if not os.path.exists(link_to_this):
                        raise RuntimeError(
                            "Trying {} for sysegg: not found".format(
                                link_to_this))
                    logger.info("Using direct path %s for %s", 
                                link_to_this, egg)
                    link_file = os.path.join(dev_egg_dir, dist.project_name)
                    if os.path.exists(link_file):
                        os.remove(link_file)
                    os.symlink(link_to_this, link_file)
                    # Also symlink the egg-info files.
                    all_filenames = os.listdir(dist.location)
                    egginfo_filenames = [
                        filename for filename in all_filenames
                        if filename.endswith('.egg-info')
                        and filename.startswith(dist.project_name)]
                    for egginfo_filename in egginfo_filenames:
                        link_to_this = os.path.join(dist.location, 
                                                    egginfo_filename)
                        link_file = os.path.join(dev_egg_dir, 
                                                 egginfo_filename)
                        if os.path.exists(link_file):
                            os.remove(link_file)
                        os.symlink(link_to_this, link_file)
                    # Older versions of ourselves used to create an
                    # egg-link file. Zap it if it is still there.
                    erroneous_old_egglink = os.path.join(
                        dev_egg_dir, '{}.egg-link'.format(dist.project_name))
                    if os.path.exists(erroneous_old_egglink):
                        os.remove(erroneous_old_egglink)
                        logger.debug("Removed old egglink %S", 
                                     erroneous_old_egglink)

        return ()

    def force_syseggs(self):
        force = self.options.get('force-sysegg', 'false')
        return force.lower() == 'true'

    update = install
