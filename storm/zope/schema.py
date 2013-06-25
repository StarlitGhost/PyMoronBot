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
"""ZStorm-aware schema manager."""
import transaction

from storm.schema import Schema


class ZCommitter(object):
    """A L{Schema} committer that uses Zope's transaction manager."""

    def commit(self):
        transaction.commit()

    def rollback(self):
        transaction.abort()


class ZSchema(Schema):
    """Convenience for creating L{Schema}s that use a L{ZCommitter}."""

    def __init__(self, creates, drops, deletes, patch_package):
        committer = ZCommitter()
        super(ZSchema, self).__init__(creates, drops, deletes, patch_package,
                                      committer)
