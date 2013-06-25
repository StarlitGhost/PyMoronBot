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
"""Manage database shemas.

The L{Schema} class can be used to create, drop, clean and upgrade database
schemas.

A database L{Schema} is defined by the series of SQL statements that should be
used to create, drop and clear the schema, respectively and by a patch module
used to upgrade it (see also L{PatchApplier}).

For example:

>>> creates = ['CREATE TABLE person (id INTEGER, name TEXT)']
>>> drops = ['DROP TABLE person']
>>> deletes = ['DELETE FROM person']
>>> import patch_module
>>> Schema(creates, drops, deletes, patch_module)

where patch_module is a Python module containing database patches used to
upgrade the schema over time.
"""

from storm.locals import StormError
from storm.schema.patch import PatchApplier


class Schema(object):
    """Create, drop, clean and patch table schemas.

    @param creates: A list of C{CREATE TABLE} statements.
    @param drops: A list of C{DROP TABLE} statements.
    @param deletes: A list of C{DELETE FROM} statements.
    @param patch_package: The Python package containing patch modules to apply.
    @param committer: Optionally a committer to pass to the L{PatchApplier}.

    @see: L{PatchApplier}.
    """
    _create_patch = "CREATE TABLE patch (version INTEGER NOT NULL PRIMARY KEY)"
    _drop_patch = "DROP TABLE patch"

    def __init__(self, creates, drops, deletes, patch_package, committer=None):
        self._creates = creates
        self._drops = drops
        self._deletes = deletes
        self._patch_package = patch_package
        self._committer = committer

    def _execute_statements(self, store, statements):
        """Execute the given statements in the given store."""
        for statement in statements:
            try:
                store.execute(statement)
            except Exception:
                print "Error running %s" % statement
                raise
        store.commit()

    def create(self, store):
        """Run C{CREATE TABLE} SQL statements with C{store}."""
        self._execute_statements(store, [self._create_patch])
        self._execute_statements(store, self._creates)

    def drop(self, store):
        """Run C{DROP TABLE} SQL statements with C{store}."""
        self._execute_statements(store, self._drops)
        self._execute_statements(store, [self._drop_patch])

    def delete(self, store):
        """Run C{DELETE FROM} SQL statements with C{store}."""
        self._execute_statements(store, self._deletes)

    def upgrade(self, store):
        """Upgrade C{store} to have the latest schema.

        If a schema isn't present a new one will be created.  Unapplied
        patches will be applied to an existing schema.
        """
        patch_applier = PatchApplier(store, self._patch_package,
                                     self._committer)
        try:
            store.execute("SELECT * FROM patch WHERE 1=2")
        except StormError:
            # No schema at all. Create it from the ground.
            store.rollback()
            self.create(store)
            patch_applier.mark_applied_all()
            store.commit()
        else:
            patch_applier.apply_all()
