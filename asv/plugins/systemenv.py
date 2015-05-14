# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-

from __future__ import \
    absolute_import, division, unicode_literals, print_function

import sys

from .. import environment
from ..console import log
from .. import util


class SystemEnvironment(environment.Environment):

    """
    Manage an environment using virtualenv.
    """
    tool_name = "system"

    def __init__(self, conf, executable):
        self._executable = executable
        self._python = util.check_output(
            [executable,
             '-c',
             'import sys; '
             'print(str(sys.version_info[0]) + "." + str(sys.version_info[1]))'
             ]).strip()
        self._requirements = {}
        self._env = {}
        super(SystemEnvironment, self).__init__(conf)

    @classmethod
    def get_environments(cls, conf, python):
        yield cls(conf, sys.executable)

    @classmethod
    def matches(self, python):
        try:
            util.which('python{0}'.format(python))
        except IOError:
            return False
        else:
            return True

    def check_presence(self):
        if not super(SystemEnvironment, self).check_presence():
            return False
        return True

    def _setup(self):
        pass

    def install_project(self, conf, commit_hash=None):
        if commit_hash is None:
            commit_hash = self.repo.get_hash_from_master()
        self.build_project(commit_hash)

    def build_project(self, commit_hash):
        self.checkout_project(commit_hash)
        log.info("Building for {0}".format(self.name))
        self.run(['setup.py', 'build_ext', '-i'], cwd=self._build_root)
        self._env["PYTHONPATH"] = self._build_root

    def install(self, package):
        pass

    def uninstall(self, package):
        pass

    def run(self, args, **kwargs):
        log.debug("Running '{0}' in {1}".format(' '.join(args), self.name))
        if "env" in kwargs:
            kwargs["env"].update(self._env)
        else:
            kwargs.update({"env": self._env})
        return util.check_output([self._executable] + args, **kwargs)
