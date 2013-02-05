import os
import logging
import pkg_resources


class Recipe(object):
    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options
        options.setdefault('eggs', '')

    def install(self):
        log = logging.getLogger(self.name)
        eggs = self.options['eggs'].strip()
        eggs = [s.strip() for s in eggs.split('\n')]

        dev_egg_dir = self.buildout['buildout']['develop-eggs-directory']

        for egg in eggs:
            try:
                dist = pkg_resources.require(egg)[0]
            except pkg_resources.DistributionNotFound:
                log.warn('No system distribution for %s found.' % egg)
                if self.force_syseggs():
                    raise

            else:
                egg_egg_link = os.path.join(
                    dev_egg_dir,
                    '%s.egg-link' % dist.project_name)
                f = open(egg_egg_link, 'w')
                f.write(dist.location)
                f.close()
                log.info('Using %s for %s' % (dist.location, egg))

        return ()

    def force_syseggs(self):
        force = self.options.get('force-sysegg', 'false')
        return force.lower() == 'true'

    update = install
