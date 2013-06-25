#
# Copyright (c) 2006, 2007 Canonical
#
# Written by Gustavo Niemeyer <gustavo@niemeyer.net>
#
# This file is part of Storm Object Relational Mapper.
#
# Storm is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation; either version 2.1 of
# the License, or (at your option) any later version.
#
# Storm is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
"""Apply database patches.

The L{PatchApplier} class can be used to apply and keep track of a series
of database patches.

To create a patch series all is needed is to add Python files under a module
of choice, an name them as 'patch_N.py' where 'N' is the version of the patch
in the series. Each patch file must define an C{apply} callable taking a
L{Store} instance has its only argument. This function will be called when the
patch gets applied.

The L{PatchApplier} can be then used to apply to a L{Store} all the available
patches. After a patch has been applied, its version is recorded in a special
'patch' table in the given L{Store}, and it won't be applied again.
"""

import sys
import os
import re

from storm.locals import StormError, Int


class UnknownPatchError(Exception):
    """
    Raised if a patch is found in the database that doesn't exist
    in the local patch directory.
    """

    def __init__(self, store, patches):
        self._store = store
        self._patches = patches

    def __str__(self):
        return "store has patches the code doesn't know about: %s" % (
            ", ".join([str(version) for version in self._patches]))


class BadPatchError(Exception):
    """Raised when a patch failing with a random exception is found."""


class Patch(object):
    """Database object representing an applied patch.

    @version: The version of the patch associated with this object.
    """

    __storm_table__ = "patch"

    version = Int(primary=True, allow_none=False)

    def __init__(self, version):
        self.version = version


class PatchApplier(object):
    """Apply to a L{Store} the database patches from a given Python package.

    @param store: The L{Store} to apply the patches to.
    @param package: The Python package containing the patches. Each patch is
        represented by a file inside the module, whose filename must match
        the format 'patch_N.py', where N is an integer number.
    @param committer: Optionally an object implementing 'commit()' and
        'rollback()' methods, to be used to commit or rollback the changes
        after applying a patch. If C{None} is given, the C{store} itself is
        used.
    """

    def __init__(self, store, package, committer=None):
        self._store = store
        self._package = package
        if committer is None:
            committer = store
        self._committer = committer

    def _module(self, version):
        """Import the Python module of the patch file with the given version.

        @param: The version of the module patch to import.
        @return: The imported module.
        """
        module_name = "patch_%d" % (version,)
        return __import__(self._package.__name__ + "." + module_name,
                          None, None, [''])

    def apply(self, version):
        """Execute the patch with the given version.

        This will call the 'apply' function defined in the patch file with
        the given version, passing it our L{Store}.

        @param version: The version of the patch to execute.
        """
        patch = Patch(version)
        self._store.add(patch)
        module = None
        try:
            module = self._module(version)
            module.apply(self._store)
        except StormError:
            self._committer.rollback()
            raise
        except:
            type, value, traceback = sys.exc_info()
            patch_repr = getattr(module, "__file__", version)
            raise BadPatchError, \
                  "Patch %s failed: %s: %s" % \
                      (patch_repr, type.__name__, str(value)), \
                      traceback
        self._committer.commit()

    def apply_all(self):
        """Execute all unapplied patches.

        @raises UnknownPatchError: If the patch table has versions for which
            no patch file actually exists.
        """
        unknown_patches = self.get_unknown_patch_versions()
        if unknown_patches:
            raise UnknownPatchError(self._store, unknown_patches)
        for version in self._get_unapplied_versions():
            self.apply(version)

    def mark_applied(self, version):
        """Mark the patch with the given version as applied."""
        self._store.add(Patch(version))
        self._committer.commit()

    def mark_applied_all(self):
        """Mark all unapplied patches as applied."""
        for version in self._get_unapplied_versions():
            self.mark_applied(version)

    def has_pending_patches(self):
        """Return C{True} if there are unapplied patches, C{False} if not."""
        for version in self._get_unapplied_versions():
            return True
        return False

    def get_unknown_patch_versions(self):
        """
        Return the list of Patch versions that have been applied to the
        database, but don't appear in the schema's patches module.
        """
        applied = self._get_applied_patches()
        known_patches = self._get_patch_versions()
        unknown_patches = set()

        for patch in applied:
            if not patch in known_patches:
                unknown_patches.add(patch)
        return unknown_patches

    def _get_unapplied_versions(self):
        """Return the versions of all unapplied patches."""
        applied = self._get_applied_patches()
        for version in self._get_patch_versions():
            if version not in applied:
                yield version

    def _get_applied_patches(self):
        """Return the versions of all applied patches."""
        applied = set()
        for patch in self._store.find(Patch):
            applied.add(patch.version)
        return applied

    def _get_patch_versions(self):
        """Return the versions of all available patches."""
        format = re.compile(r"^patch_(\d+).py$")

        filenames = os.listdir(os.path.dirname(self._package.__file__))
        matches = [(format.match(fn), fn) for fn in filenames]
        matches = sorted(filter(lambda x: x[0], matches),
                         key=lambda x: int(x[1][6:-3]))
        return [int(match.group(1)) for match, filename in matches]
