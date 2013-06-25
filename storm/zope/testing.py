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
import transaction
from testresources import TestResourceManager
from zope.component import provideUtility, getUtility

from storm.zope.zstorm import ZStorm
from storm.zope.interfaces import IZStorm


class ZStormResourceManager(TestResourceManager):
    """Provide a L{ZStorm} resource to be used in test cases.

    The constructor is passed the details of the L{Store}s to be registered
    in the provided L{ZStore} resource. Then the C{make} and C{clean} methods
    make sure that such L{Store}s are properly setup and cleaned for each test.

    @param databases: A C{list} of C{dict}s holding the following keys:
        - 'name', the name of the store to be registered.
        - 'uri', the database URI to use to create the store.
        - 'schema', the L{Schema} for the tables in the store.
        - 'schema-uri', optionally an alternate URI to use for applying the
          schema, if not given it defaults to 'uri'.

    @ivar force_delete: If C{True} for running L{Schema.delete} on a L{Store}
        even if no commit was performed by the test. Useful when running a test
        in a subprocess that might commit behind our back.
    """
    force_delete = False

    def __init__(self, databases):
        super(ZStormResourceManager, self).__init__()
        self._databases = databases
        self._zstorm = None
        self._schema_zstorm = None
        self._commits = {}
        self._schemas = {}

    def make(self, dependencies):
        """Create a L{ZStorm} resource to be used by tests.

        @return: A L{ZStorm} object that will be shared among all tests using
            this resource manager.
        """
        if self._zstorm is None:

            zstorm = ZStorm()
            schema_zstorm = ZStorm()
            databases = self._databases

            # Adapt the old databases format to the new one, for backward
            # compatibility. This should be eventually dropped.
            if isinstance(databases, dict):
                databases = [{"name": name, "uri": uri, "schema": schema}
                             for name, (uri, schema) in databases.iteritems()]

            for database in databases:
                name = database["name"]
                uri = database["uri"]
                schema = database["schema"]
                schema_uri = database.get("schema-uri", uri)
                self._schemas[name] = schema
                zstorm.set_default_uri(name, uri)
                schema_zstorm.set_default_uri(name, schema_uri)
                store = zstorm.get(name)
                self._set_commit_proxy(store)
                schema_store = schema_zstorm.get(name)
                schema.upgrade(schema_store)
                # Clean up tables here to ensure that the first test run starts
                # with an empty db
                schema.delete(schema_store)

            provideUtility(zstorm)
            self._zstorm = zstorm
            self._schema_zstorm = schema_zstorm

        elif getUtility(IZStorm) is not self._zstorm:
            # This probably means that the test code has overwritten our
            # utility, let's re-register it.
            provideUtility(self._zstorm)

        return self._zstorm

    def _set_commit_proxy(self, store):
        """Set a commit proxy to keep track of commits and clean up the tables.

        @param store: The L{Store} to set the commit proxy on. Any commit on
            this store will result in the associated tables to be cleaned upon
            tear down.
        """
        store.__real_commit__ = store.commit

        def commit_proxy():
            self._commits[store] = True
            store.__real_commit__()

        store.commit = commit_proxy

    def clean(self, resource):
        """Clean up the stores after a test."""
        try:
            for name, store in self._zstorm.iterstores():
                # Ensure that the store is in a consistent state
                store.flush()
                # Clear the alive cache *before* abort is called,
                # to prevent a useless loop in Store.invalidate
                # over the alive objects
                store._alive.clear()
        finally:
            transaction.abort()

        # Clean up tables after each test if a commit was made
        for name, store in self._zstorm.iterstores():
            if self.force_delete or store in self._commits:
                schema_store = self._schema_zstorm.get(name)
                schema = self._schemas[name]
                schema.delete(schema_store)
        self._commits = {}
